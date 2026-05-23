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

log = logging.getLogger("osint.dedup")

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


def dedup_incidents(db, *, jaccard_threshold: float = 0.5) -> dict:
    """DB에 이미 쌓인 중복 사건을 제거한다.

    제목 토큰 자카드 유사도로 같은 이벤트를 클러스터링하고, 클러스터마다
    가장 품질이 좋은 사건 하나만 남긴 뒤 나머지 사건과 그 원본 문서를
    삭제한다. (문서를 함께 지워야 다음 추출 때 사건이 되살아나지 않는다.)

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

    for i in range(n):
        ti = recs[i]["toks"]
        if len(ti) < 3:
            continue  # 토큰이 너무 적은 사건은 제목만으로 병합하지 않음
        si = recs[i]["side"]
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
        "samples": samples,
    }
    log.info("이벤트 중복제거: %d → %d (%d건 제거, %d개 클러스터)",
             n, n - removed, removed, dup_clusters)
    return result
