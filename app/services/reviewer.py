from __future__ import annotations
from typing import Any


def review_ingest_health(ingest: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    inserted = ingest.get('inserted', 0)
    candidates_total = ingest.get('candidates_total', 0)
    dup_feed = ingest.get('duplicate_in_feed', 0)
    dup_db = ingest.get('duplicate_in_db', 0)
    if inserted >= 10:
        level = 'good'
    elif inserted >= 3:
        level = 'acceptable'
    elif candidates_total == 0:
        level = 'poor'
    elif dup_feed > inserted + 5 or dup_db > inserted + 10:
        level = 'limited_by_duplicates'
    else:
        level = 'low_yield'
    return {
        'level': level,
        'inserted': inserted,
        'candidates_total': candidates_total,
        'duplicates_total': dup_feed + dup_db,
        'documents_in_window': metrics.get('documents', 0),
        'incidents_in_window': metrics.get('incidents', 0),
    }


def summarize_ingest_issue(ingest: dict[str, Any], metrics: dict[str, Any]) -> str:
    inserted = ingest.get('inserted', 0)
    if inserted > 0:
        return f"새 기사 {inserted}건을 수집했고, 사건 데이터와 지도/브리핑을 갱신했습니다."
    if metrics.get('documents', 0) > 0:
        return "새로 추가된 기사는 없었지만, 기존 데이터를 재사용해 출력물을 갱신했습니다."
    return "관련 기사를 확보하지 못했습니다. 네트워크 상태, RSS/GDELT 접근, 검색 쿼리를 점검하세요."


def build_collection_advice(ingest: dict[str, Any], metrics: dict[str, Any]) -> list[str]:
    advice: list[str] = []
    if ingest.get('inserted', 0) == 0 and ingest.get('duplicate_in_feed', 0) > 10:
        advice.append('피드 중복이 많습니다. 쿼리를 세분화하거나 소스를 다양화하세요.')
    if ingest.get('inserted', 0) == 0 and metrics.get('documents', 0) == 0:
        advice.append('네트워크 또는 뉴스 소스 접근이 차단된 것 같습니다. GDELT/Google News 접근을 확인하세요.')
    if ingest.get('fetch_failures', 0) > 3:
        advice.append('기사 본문 fetch 실패가 많습니다. HTTP timeout과 user-agent를 조정하세요.')
    if not advice:
        advice.append('수집이 정상 범위입니다.')
    return advice
