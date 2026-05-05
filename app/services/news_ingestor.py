from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Iterable, List
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import SourceDocument
from app.services.utils import (
    canonicalize_url,
    normalize_whitespace,
    publisher_domain,
    safe_parse_date,
    sha256_text,
)


class GoogleNewsRSSIngestor:
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    def _build_rss_url(self, query: str, days: int = 7) -> str:
        effective_query = query if f"when:{days}d" in query else f"{query} when:{days}d"
        return f"https://news.google.com/rss/search?q={quote_plus(effective_query)}&hl=en-US&gl=US&ceid=US:en"

    def _extract_google_redirect_target(self, url: str) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        for key in ("url", "u", "q"):
            value = query.get(key)
            if value and value[0].startswith(("http://", "https://")):
                return unquote(value[0])
        return url

    def _extract_link_from_summary(self, summary_html: str) -> str | None:
        if not summary_html:
            return None
        try:
            soup = BeautifulSoup(summary_html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = html.unescape(a["href"])
                if href.startswith("http://") or href.startswith("https://"):
                    return href
        except Exception:
            return None
        return None

    def _resolve_final_url(self, url: str) -> str:
        candidate = self._extract_google_redirect_target(url)
        try:
            response = self.session.get(candidate, timeout=settings.http_timeout, allow_redirects=True)
            response.raise_for_status()
            return canonicalize_url(str(response.url))
        except Exception:
            return canonicalize_url(candidate)

    def _fetch_article(self, url: str) -> tuple[str, str]:
        try:
            response = self.session.get(url, timeout=settings.http_timeout, allow_redirects=True)
            response.raise_for_status()
            final_url = str(response.url)
            soup = BeautifulSoup(response.text, "html.parser")

            canonical_link = soup.find("link", rel=lambda v: v and "canonical" in str(v).lower())
            if canonical_link and canonical_link.get("href"):
                final_url = canonical_link["href"]

            og_url = soup.find("meta", property="og:url")
            if og_url and og_url.get("content"):
                final_url = og_url["content"]

            article_node = soup.find("article")
            text_nodes = article_node.find_all(["p", "li"]) if article_node else soup.find_all("p")
            paragraphs = [p.get_text(" ", strip=True) for p in text_nodes]
            text = normalize_whitespace(" ".join(paragraphs))
            return canonicalize_url(final_url), text[:40000]
        except Exception:
            return canonicalize_url(url), ""

    def _parse_entry_time(self, entry: Any) -> datetime | None:
        for field in ("published", "updated"):
            value = getattr(entry, field, None)
            if value:
                dt = safe_parse_date(value)
                if dt:
                    return dt
        return None

    def _is_within_days(self, dt: datetime | None, days: int) -> bool:
        if not dt:
            return True
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= datetime.now(timezone.utc) - timedelta(days=days)

    def _normalized_title_key(self, title: str, publisher: str) -> str:
        normalized_title = re.sub(r"[^a-z0-9 ]+", " ", (title or "").lower())
        normalized_title = re.sub(r"\s+", " ", normalized_title).strip()
        normalized_publisher = re.sub(r"[^a-z0-9]+", "", (publisher or "").lower())
        return f"{normalized_title}::{normalized_publisher}"[:500]

    def _event_signature(self, title: str, published_at: datetime | None) -> str:
        """사건-수준 dedup 키: 제목 첫 6개 의미 단어(stopword·매체명 제거) + UTC YYYY-MM-DD.
        같은 사건을 다른 출판사가 다른 문구로 보도해도 묶이도록 한다.
        6단어로 잡은 이유: 뉴스 헤드라인의 핵심 사실은 보통 첫 5~6단어에 압축되며,
        그 이후엔 매체명·attribution(report/says/sources) 등 변동이 큰 토큰이 자주 붙는다.
        """
        normalized = re.sub(r"[^a-z0-9 ]+", " ", (title or "").lower())
        words = [w for w in normalized.split() if w and len(w) > 1]
        # 흔한 stopword + 매체명·보도 동사 제거 — 'iran/israel'처럼 핵심 명사는 보존
        STOP = {
            # 영어 stopword
            "the", "a", "an", "in", "on", "at", "of", "to", "for", "and", "or",
            "by", "with", "as", "is", "are", "was", "were", "from", "after",
            "amid", "into", "over", "off", "out", "but", "vs", "via",
            # 매체명 (제목 끝에 자주 붙는 형태)
            "reuters", "ap", "bbc", "cnn", "nyt", "reports", "report", "says",
            "said", "sources", "guardian", "wsj", "afp", "ft", "axios", "bloomberg",
            "newsweek", "telegraph", "haaretz", "nbc", "cbs", "abc",
        }
        signal = [w for w in words if w not in STOP][:6]
        prefix = " ".join(signal) if signal else " ".join(words[:6])
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            day_key = published_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
        else:
            day_key = "unknown"
        return sha256_text(f"{prefix}|{day_key}")[:32]

    def _dedupe_key(self, canonical_url: str, title: str, publisher: str, published_at: datetime | None, raw_text: str) -> tuple[str, str]:
        day_key = published_at.strftime("%Y-%m-%d") if published_at else "unknown"
        title_key = self._normalized_title_key(title, publisher)
        if raw_text and len(raw_text) >= 300:
            content_key = sha256_text(raw_text[:5000])
        else:
            content_key = sha256_text(f"{title_key}|{day_key}")
        url_key = canonical_url or f"title://{title_key}|{day_key}"
        return url_key, content_key

    def _is_known_document(self, canonical_url: str, content_hash: str | None = None,
                           title: str | None = None, publisher: str | None = None,
                           published_at: datetime | None = None,
                           event_signature: str | None = None) -> bool:
        clauses = []
        if canonical_url:
            clauses.append(SourceDocument.url == canonical_url)
        if content_hash:
            clauses.append(SourceDocument.content_hash == content_hash)
        if event_signature:
            # 사건-수준 매치 — 같은 사건 다른 출판사도 같은 사건으로 인식
            clauses.append(SourceDocument.event_signature == event_signature)
        if title and publisher and published_at:
            start_of_day = published_at.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            clauses.append(
                (SourceDocument.title == title) &
                (SourceDocument.publisher == publisher) &
                (SourceDocument.published_at >= start_of_day) &
                (SourceDocument.published_at < end_of_day)
            )
        if not clauses:
            return False
        return self.db.query(SourceDocument.id).filter(or_(*clauses)).first() is not None

    def _iter_google_entries(self, queries: Iterable[str], max_per_query: int, days: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        stats = {"feed_entries_seen": 0, "fetch_failures": 0, "per_query": []}
        candidates: list[dict[str, Any]] = []
        for query in queries:
            feed = feedparser.parse(self._build_rss_url(query, days=days))
            entries = list(feed.entries[:max_per_query])
            stats["feed_entries_seen"] += len(entries)
            stats["per_query"].append({"query": query, "entries_seen": len(entries)})
            for entry in entries:
                raw_link = normalize_whitespace(html.unescape(getattr(entry, "link", "")))
                summary_link = self._extract_link_from_summary(getattr(entry, "summary", "") or "")
                link_candidate = summary_link or raw_link
                if not link_candidate:
                    stats["fetch_failures"] += 1
                    continue
                published_at = self._parse_entry_time(entry)
                if not self._is_within_days(published_at, days):
                    continue
                publisher = "Unknown"
                if hasattr(entry, "source") and getattr(entry.source, "title", None):
                    publisher = entry.source.title
                title = normalize_whitespace(getattr(entry, "title", "Untitled"))
                candidates.append({
                    "title": title,
                    "publisher": publisher,
                    "published_at": published_at,
                    "raw_link": raw_link,
                    "summary_link": summary_link,
                    "preferred_link": link_candidate,
                    "summary": normalize_whitespace(BeautifulSoup(getattr(entry, "summary", "") or "", "html.parser").get_text(" ", strip=True)),
                    "query": query,
                })
        return candidates, stats

    def _iter_gdelt_entries(self, queries: Iterable[str], max_per_query: int, days: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        stats = {"gdelt_entries_seen": 0, "gdelt_failures": 0, "per_query": []}
        mode = "ArtList"
        for query in queries:
            params = {
                "query": query,
                "mode": mode,
                "maxrecords": str(max_per_query),
                "sort": "DateDesc",
                "format": "json",
                "timespan": f"{days}d",
            }
            try:
                response = self.session.get("https://api.gdeltproject.org/api/v2/doc/doc", params=params, timeout=settings.http_timeout)
                response.raise_for_status()
                payload = response.json()
                articles = payload.get("articles", []) if isinstance(payload, dict) else []
                stats["gdelt_entries_seen"] += len(articles)
                stats["per_query"].append({"query": query, "entries_seen": len(articles)})
                for item in articles[:max_per_query]:
                    title = normalize_whitespace(item.get("title", "Untitled"))
                    url = normalize_whitespace(item.get("url", ""))
                    if not url:
                        continue
                    published_at = safe_parse_date(item.get("seendate") or item.get("date"))
                    if not self._is_within_days(published_at, days):
                        continue
                    publisher = normalize_whitespace(item.get("domain", "Unknown")) or "Unknown"
                    candidates.append({
                        "title": title,
                        "publisher": publisher,
                        "published_at": published_at,
                        "raw_link": url,
                        "summary_link": url,
                        "preferred_link": url,
                        "summary": normalize_whitespace(item.get("socialimage", "") or ""),
                        "query": f"GDELT:{query}",
                    })
            except Exception:
                stats["gdelt_failures"] += 1
        return candidates, stats

    def _rotate_queries(self, queries: List[str], max_active: int = 10) -> List[str]:
        """시간 기반 쿼리 회전 — 매 실행마다 다른 쿼리 조합을 사용하여 중복을 줄인다."""
        from datetime import datetime, timezone
        if len(queries) <= max_active:
            return queries
        # 현재 시간의 hour를 seed로 사용하여 쿼리 그룹을 회전
        hour_seed = int(datetime.now(timezone.utc).strftime("%Y%m%d%H"))
        # 항상 처음 7개 (핵심 쿼리)는 포함, 나머지에서 회전 선택
        core = queries[:7]
        extra = queries[7:]
        if not extra:
            return core
        # 회전 오프셋 계산
        offset = hour_seed % len(extra)
        selected_extra = (extra[offset:] + extra[:offset])[:max_active - len(core)]
        return core + selected_extra

    def ingest(self, queries: List[str] | None = None, max_per_query: int = 25, days: int = 7) -> dict[str, Any]:
        queries = self._rotate_queries(queries or settings.default_queries)
        inserted = 0
        duplicate_in_feed = 0
        duplicate_in_db = 0
        fetch_failures = 0
        seen_keys: set[str] = set()
        seen_hashes: set[str] = set()
        seen_signatures: set[str] = set()  # 사건-수준 dedup (이번 ingest 호출 안에서)
        network_error = False

        try:
            google_candidates, google_stats = self._iter_google_entries(queries, max_per_query=max_per_query, days=days)
        except Exception as e:
            google_candidates = []
            google_stats = {"feed_entries_seen": 0, "fetch_failures": 1, "per_query": [], "error": str(e)}
            network_error = True

        try:
            gdelt_candidates, gdelt_stats = self._iter_gdelt_entries(queries, max_per_query=max(10, max_per_query // 2), days=days)
        except Exception as e:
            gdelt_candidates = []
            gdelt_stats = {"gdelt_entries_seen": 0, "gdelt_failures": 1, "per_query": [], "error": str(e)}
            network_error = True

        candidates = google_candidates + gdelt_candidates

        # 네트워크 실패 또는 후보 부족 시 검증된 시드 데이터로 폴백한다.
        # force=True 를 넘겨 seed_sample_data 가 이미 추가된 URL 은 건너뛰고
        # 새로 추가된 검증 이벤트만 DB 에 삽입하도록 한다.
        if not candidates:
            from app.services.seed_data import seed_sample_data
            seed_result = seed_sample_data(self.db, force=True)
            msg_ko = (
                "네트워크 접속 실패로 검증된 시드 데이터를 사용합니다. "
                "실제 뉴스 수집을 위해 네트워크 연결을 확인하세요."
                if network_error
                else "뉴스 피드에서 새 후보를 찾지 못해 검증된 시드 데이터로 폴백했습니다."
            )
            return {
                "inserted": seed_result.get("documents_inserted", 0),
                "feed_entries_seen": 0,
                "gdelt_entries_seen": 0,
                "duplicate_in_feed": 0,
                "duplicate_in_db": 0,
                "fetch_failures": 1 if network_error else 0,
                "sources": {"google": google_stats, "gdelt": gdelt_stats},
                "candidates_total": 0,
                "window_days": days,
                "network_error": network_error,
                "fallback_seed": seed_result,
                "message": msg_ko,
            }

        for item in candidates:
            resolved_url = self._resolve_final_url(item["preferred_link"]) if item["preferred_link"] else ""
            canonical_url, raw_text = self._fetch_article(resolved_url) if resolved_url else ("", "")
            canonical_url = canonicalize_url(canonical_url or resolved_url or item["preferred_link"] or item["raw_link"])
            raw_text = raw_text or item["summary"] or item["title"]
            url_key, content_key = self._dedupe_key(canonical_url, item["title"], item["publisher"], item["published_at"], raw_text)
            event_sig = self._event_signature(item["title"], item["published_at"])

            # 1) 같은 ingest 호출 안의 메모리 dedup
            if url_key in seen_keys or content_key in seen_hashes or event_sig in seen_signatures:
                duplicate_in_feed += 1
                continue
            seen_keys.add(url_key)
            seen_hashes.add(content_key)
            seen_signatures.add(event_sig)

            # 2) DB-수준 dedup (이전 cron 실행에서 들어간 동일 사건도 거름)
            if self._is_known_document(canonical_url, content_key, item["title"],
                                       item["publisher"], item["published_at"],
                                       event_signature=event_sig):
                duplicate_in_db += 1
                continue

            domain = publisher_domain(canonical_url)
            reliability = 0.9 if any(domain.endswith(d) for d in settings.trusted_domains) else 0.55
            if item["query"].startswith("GDELT:") and reliability < 0.6:
                reliability = 0.6

            doc = SourceDocument(
                title=item["title"],
                url=canonical_url or f"urn:article:{content_key}",
                publisher=item["publisher"],
                published_at=item["published_at"],
                language="en",
                query_used=item["query"],
                raw_text=raw_text[:40000],
                content_hash=content_key,
                event_signature=event_sig,
                source_reliability=reliability,
            )
            self.db.add(doc)
            try:
                self.db.flush()
                inserted += 1
            except IntegrityError:
                self.db.rollback()
                duplicate_in_db += 1

        self.db.commit()
        return {
            "inserted": inserted,
            "feed_entries_seen": google_stats["feed_entries_seen"],
            "gdelt_entries_seen": gdelt_stats["gdelt_entries_seen"],
            "duplicate_in_feed": duplicate_in_feed,
            "duplicate_in_db": duplicate_in_db,
            "fetch_failures": fetch_failures + google_stats["fetch_failures"] + gdelt_stats["gdelt_failures"],
            "sources": {
                "google": google_stats,
                "gdelt": gdelt_stats,
            },
            "candidates_total": len(candidates),
            "window_days": days,
        }
