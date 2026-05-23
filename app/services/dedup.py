"""이벤트 중복 제거.

문제
────
같은 실제 사건을 Reuters·AP·BBC·CNN 등 여러 언론사가 보도하면 URL·본문이
모두 달라서 기존 중복제거(URL/본문 해시)가 잡지 못한다. 그 결과 하나의
사건이 사건 목록·지도에 여러 번 중복 표시된다.

해결
────
기사 제목의 의미 토큰 집합을 비교한다. 같은 사건을 다룬 기사들은 제목의
핵심 단어(행위자·표적·수단·지명·숫자)를 대부분 공유하므로, 토큰 자카드
유사도가 임계값 이상이면 같은 이벤트로 묶는다.

  - event_signature(title) : 수집 단계의 빠른 결정적 중복 차단용 서명
  - dedup_incidents(db)    : DB에 이미 쌓인 중복 사건을 클러스터링해 정리
"""
from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone

log = logging.getLogger("osint.dedup")


def _norm_dt(dt: datetime | None) -> datetime | None:
    """발행일을 timezone-aware UTC 로 정규화."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

# 불용어 + 언론사명 + 뉴스 상투어 — 이벤트 식별에 무의미한 토큰
_STOP: frozenset[str] = frozenset({
    # 관사·전치사·접속사·대명사·be/조동사
    "a", "an", "the", "in", "on", "at", "of", "to", "for", "and", "or", "but",
    "with", "as", "by", "from", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "will", "would", "could", "should", "may", "might",
    "do", "does", "did", "not", "no", "nor", "so", "than", "then", "this", "that",
    "these", "those", "it", "its", "he", "she", "they", "them", "their", "there",
    "here", "what", "which", "who", "whom", "whose", "how", "why", "when", "where",
    "amid", "over", "after", "before", "during", "into", "out", "up", "down",
    "off", "about", "against", "between", "through", "near", "if", "all", "more",
    # 뉴스 상투어
    "says", "say", "said", "report", "reports", "reported", "claim", "claims",
    "claimed", "tells", "told", "according", "new", "latest", "live", "update",
    "updates", "breaking", "watch", "video", "photos", "analysis", "opinion",
    "exclusive", "now", "amid", "vs",
    # 언론사·통신사명
    "reuters", "ap", "associated", "press", "bbc", "cnn", "nyt", "times",
    "post", "guardian", "aljazeera", "jazeera", "npr", "abc", "nbc", "cbs",
    "fox", "news", "axios", "politico", "bloomberg", "afp", "wsj", "journal",
    "sky", "dpa", "anadolu", "tass", "irna", "mehr", "tasnim", "presstv",
    "haaretz", "jpost", "ynet", "i24", "cnbc", "newsweek", "hill", "intercept",
})


def _stem(word: str) -> str:
    """가벼운 어간 추출 — 복수형/시제 차이를 흡수 (missile/missiles, kill/killed)."""
    for suf in ("ing", "ed", "s"):
        if len(word) > len(suf) + 2 and word.endswith(suf):
            return word[: -len(suf)]
    return word


def title_tokens(title: str | None) -> set[str]:
    """제목에서 의미 토큰 집합을 추출 (소문자·어간화·불용어 제거)."""
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", (title or "").lower())
    tokens: set[str] = set()
    for raw in cleaned.split():
        if len(raw) < 2 or raw in _STOP:
            continue
        stemmed = _stem(raw)
        if len(stemmed) >= 2 and stemmed not in _STOP:
            tokens.add(stemmed)
    return tokens


def jaccard(a: set[str], b: set[str]) -> float:
    """두 토큰 집합의 자카드 유사도 (교집합 / 합집합)."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def event_signature(title: str | None) -> str:
    """수집 단계용 결정적 이벤트 서명.

    의미 토큰 중 가장 긴(=정보량 많은) 6개를 정렬해 해시한다. 같은 사건을
    다룬 기사들은 핵심 단어를 공유하므로 서명이 일치할 가능성이 높다.
    토큰이 3개 미만이면 제목 자체를 해시해 과도한 병합을 막는다.
    """
    tokens = title_tokens(title)
    if len(tokens) < 3:
        base = re.sub(r"[^a-z0-9]+", "", (title or "").lower())
        return "t:" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]
    top = sorted(sorted(tokens, key=len, reverse=True)[:6])
    return "e:" + hashlib.sha1("|".join(top).encode("utf-8")).hexdigest()[:16]


def _quality(rec: dict) -> tuple:
    """클러스터에서 '대표로 남길 사건'을 고르는 품질 점수 (클수록 우선)."""
    inc = rec["inc"]
    doc = rec["doc"]
    return (
        rec["rel"],                                      # 1) 출처 신뢰도
        float(inc.confidence or 0.0),                    # 2) 검증 신뢰도
        1 if (inc.latitude is not None and inc.longitude is not None) else 0,  # 3) 좌표 보유
        len(inc.damage_summary or ""),                   # 4) 피해 설명 충실도
        (doc.published_at.timestamp() if doc and doc.published_at else 0.0),   # 5) 최신성
    )


def dedup_incidents(
    db,
    *,
    jaccard_threshold: float = 0.5,
    date_window_days: int = 3,
) -> dict:
    """DB에 이미 쌓인 중복 사건을 제거한다.

    제목 토큰 자카드 유사도로 같은 이벤트를 클러스터링하고, 클러스터마다
    가장 품질이 좋은 사건 하나만 남긴 뒤 나머지 사건과 그 원본 문서를
    삭제한다. (문서를 함께 지워야 다음 추출 때 사건이 되살아나지 않는다.)

    발행일이 date_window_days 보다 더 차이나면 제목이 비슷해도 병합하지
    않는다 — 날짜만 다른 정기 보고서(예: "Iran Update May 1" vs "May 11")가
    잘못 합쳐지는 것을 막는다.

    여러 번 호출해도 안전하며, 결과 통계와 병합 샘플을 반환한다.
    """
    from app.models.entities import Incident, SourceDocument
    from app.services.seed_data import get_actor_side

    incidents = db.query(Incident).all()
    n = len(incidents)
    recs: list[dict] = []
    for inc in incidents:
        doc = (
            db.query(SourceDocument)
            .filter(SourceDocument.id == inc.document_id)
            .first()
        )
        title = (doc.title if doc else "") or ""
        recs.append({
            "inc": inc,
            "doc": doc,
            "title": title,
            "toks": title_tokens(title),
            "side": get_actor_side(inc.actor or ""),
            "rel": float((doc.source_reliability if doc else 0.0) or 0.0),
            "date": _norm_dt(doc.published_at if doc else None),
        })

    # ── union-find 로 같은 이벤트끼리 묶기 ──
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    window_sec = date_window_days * 86400
    for i in range(n):
        ti = recs[i]["toks"]
        if len(ti) < 3:
            continue  # 토큰이 너무 적은 사건은 제목만으로 병합하지 않음
        si = recs[i]["side"]
        di = recs[i]["date"]
        for j in range(i + 1, n):
            if find(i) == find(j):
                continue
            tj = recs[j]["toks"]
            if len(tj) < 3:
                continue
            # 진영(이란측/미국측/기타)이 다르면 병합하지 않음 (단, 기타는 허용)
            sj = recs[j]["side"]
            if si != sj and "other" not in (si, sj):
                continue
            # 발행일이 창(window)보다 더 차이나면 같은 사건으로 보지 않는다.
            dj = recs[j]["date"]
            if di and dj and abs((di - dj).total_seconds()) > window_sec:
                continue
            if jaccard(ti, tj) >= jaccard_threshold:
                union(i, j)

    # ── 클러스터별로 대표 1건만 남기고 삭제 ──
    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)

    removed = 0
    dup_clusters = 0
    samples: list[dict] = []
    for members in clusters.values():
        if len(members) <= 1:
            continue
        dup_clusters += 1
        members.sort(key=lambda idx: _quality(recs[idx]), reverse=True)
        keep_idx = members[0]
        drop = members[1:]
        if len(samples) < 10:
            samples.append({
                "kept_id": recs[keep_idx]["inc"].id,
                "kept_title": recs[keep_idx]["title"][:100],
                "removed": len(drop),
                "removed_titles": [recs[d]["title"][:100] for d in drop[:4]],
            })
        for d in drop:
            inc = recs[d]["inc"]
            doc = recs[d]["doc"]
            db.delete(inc)
            if doc:
                db.delete(doc)
            removed += 1

    db.commit()
    result = {
        "incidents_before": n,
        "duplicates_removed": removed,
        "incidents_after": n - removed,
        "duplicate_clusters": dup_clusters,
        "jaccard_threshold": jaccard_threshold,
        "date_window_days": date_window_days,
        "samples": samples,
    }
    log.info("이벤트 중복제거: %d → %d (%d건 제거, %d개 클러스터)",
             n, n - removed, removed, dup_clusters)
    return result


# ──────────────────────────────────────────────────────────────────
# 불필요(정크) 기사 탐지 — 개별 사건이 아닌 라운드업·해설·오피니언
# ──────────────────────────────────────────────────────────────────
_JUNK_PATTERNS: list[tuple[str, str]] = [
    ("roundup",
     r"latest developments|live updates?|liveblog|live blog|as it happened|"
     r"as it unfolds|what we know|what to know|here'?s what|key takeaways?|"
     r"\brecap\b|minute[- ]by[- ]minute|in pictures|in photos|in maps|"
     r"your questions answered|day \d+ of the war"),
    ("explainer",
     r"\bexplained\b|\bexplainer\b|^what is |^what are |^who is |^who are |"
     r"^why is |^why are |^why did |^how does |^how did |^how is |"
     r"a guide to|everything you need to know"),
    ("opinion",
     r"^opinion\b|opinion:|\| opinion|analysis:|^analysis |editorial|"
     r"^comment:|viewpoint|^column:"),
    ("listicle",
     r"\b\d+ things\b|things to know|things you"),
]
_JUNK_COMPILED = [(cat, re.compile(pat, re.IGNORECASE)) for cat, pat in _JUNK_PATTERNS]


def is_junk_title(title: str | None) -> str | None:
    """제목이 '개별 사건'이 아니라 라운드업·해설·오피니언이면 카테고리명을,
    아니면 None 을 반환한다."""
    if not title:
        return None
    for cat, rx in _JUNK_COMPILED:
        if rx.search(title):
            return cat
    return None


def cleanup_incidents(
    db,
    *,
    dry_run: bool = True,
    jaccard_threshold: float = 0.5,
    date_window_days: int = 3,
    cross_date_threshold: float = 0.78,
    drop_junk: bool = True,
) -> dict:
    """사건 목록 종합 정리 — 불필요(정크) 기사 + 중복을 한 번에 정리한다.

    1) 정크 제거: 라운드업·해설·오피니언 기사, 그리고 행위자·수단·표적이
       모두 없는 '내용 없음' 사건.
    2) 중복 제거: 제목 유사도로 같은 사건을 묶어 대표 1건만 남긴다.
       - 발행일이 가까우면(date_window_days 이내) 유사도 0.5 이상 병합
       - 발행일이 멀어도 유사도가 매우 높으면(cross_date_threshold 이상)
         병합 — '최근 기사가 과거 사건을 재탕'한 경우를 잡는다.

    dry_run=True 면 무엇이 지워질지 분석 리포트만 반환하고 삭제는 하지 않는다.
    """
    from app.models.entities import Incident, SourceDocument
    from app.services.seed_data import get_actor_side

    incidents = db.query(Incident).all()
    n = len(incidents)

    recs: list[dict] = []
    for inc in incidents:
        doc = (
            db.query(SourceDocument)
            .filter(SourceDocument.id == inc.document_id)
            .first()
        )
        title = (doc.title if doc else "") or ""
        junk_cat = is_junk_title(title) if drop_junk else None
        # 행위자·수단·표적유형이 모두 없으면 사건으로서 내용이 없다고 본다.
        if drop_junk and junk_cat is None and not (inc.actor or inc.means or inc.target_type):
            junk_cat = "low_content"
        recs.append({
            "inc": inc,
            "doc": doc,
            "title": title,
            "toks": title_tokens(title),
            "side": get_actor_side(inc.actor or ""),
            "rel": float((doc.source_reliability if doc else 0.0) or 0.0),
            "date": _norm_dt(doc.published_at if doc else None),
            "junk": junk_cat,
        })

    junk_recs = [r for r in recs if r["junk"]]
    keep_recs = [r for r in recs if not r["junk"]]

    junk_by_cat: dict[str, int] = {}
    junk_samples: list[dict] = []
    _per_cat: dict[str, int] = {}
    for r in junk_recs:
        c = r["junk"]
        junk_by_cat[c] = junk_by_cat.get(c, 0) + 1
        _per_cat[c] = _per_cat.get(c, 0) + 1
        if _per_cat[c] <= 4:
            junk_samples.append({"category": c, "title": r["title"][:100]})

    # ── 정크를 제외한 사건들에 대해 중복 클러스터링 ──
    m = len(keep_recs)
    parent = list(range(m))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    window_sec = date_window_days * 86400
    for i in range(m):
        ti = keep_recs[i]["toks"]
        if len(ti) < 3:
            continue
        si = keep_recs[i]["side"]
        di = keep_recs[i]["date"]
        for j in range(i + 1, m):
            if find(i) == find(j):
                continue
            tj = keep_recs[j]["toks"]
            if len(tj) < 3:
                continue
            sj = keep_recs[j]["side"]
            if si != sj and "other" not in (si, sj):
                continue
            sim = jaccard(ti, tj)
            if sim < jaccard_threshold:
                continue
            dj = keep_recs[j]["date"]
            within = (not (di and dj)) or abs((di - dj).total_seconds()) <= window_sec
            # 날짜가 가까우면 일반 임계값, 멀면 고유사도(재탕)일 때만 병합
            if within or sim >= cross_date_threshold:
                union(i, j)

    clusters: dict[int, list[int]] = {}
    for i in range(m):
        clusters.setdefault(find(i), []).append(i)

    dup_remove: list[int] = []
    dup_samples: list[dict] = []
    dup_clusters = 0
    for members in clusters.values():
        if len(members) <= 1:
            continue
        dup_clusters += 1
        members.sort(key=lambda idx: _quality(keep_recs[idx]), reverse=True)
        drop = members[1:]
        if len(dup_samples) < 10:
            dup_samples.append({
                "kept_title": keep_recs[members[0]]["title"][:100],
                "removed": len(drop),
                "removed_titles": [keep_recs[d]["title"][:100] for d in drop[:3]],
            })
        dup_remove.extend(drop)

    junk_count = len(junk_recs)
    dup_count = len(dup_remove)
    after = n - junk_count - dup_count

    report: dict = {
        "mode": "dry_run" if dry_run else "executed",
        "total_incidents": n,
        "junk": {
            "total": junk_count,
            "by_category": junk_by_cat,
            "samples": junk_samples,
        },
        "duplicates": {
            "total": dup_count,
            "clusters": dup_clusters,
            "samples": dup_samples,
        },
        "incidents_after": after,
    }

    if dry_run:
        report["note"] = (
            "dry_run — 실제 삭제는 하지 않았습니다. 위 분석을 확인한 뒤 "
            "?dry_run=false 로 실제 정리를 실행하세요."
        )
        log.info("cleanup(dry_run): 전체 %d, 정크 %d, 중복 %d → %d 예상",
                 n, junk_count, dup_count, after)
        return report

    # ── 실제 삭제 ──
    to_delete = list(junk_recs) + [keep_recs[i] for i in dup_remove]
    removed = 0
    for r in to_delete:
        db.delete(r["inc"])
        if r["doc"]:
            db.delete(r["doc"])
        removed += 1
    db.commit()
    report["removed"] = removed
    report["note"] = f"{removed}건 삭제 완료 (정크 {junk_count} + 중복 {dup_count})."
    log.info("cleanup: %d → %d (정크 %d, 중복 %d)", n, after, junk_count, dup_count)
    return report
