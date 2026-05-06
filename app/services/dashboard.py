from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import Incident, SourceDocument

DEFAULT_WINDOW_DAYS = 90  # 전쟁 시작(2/28) 이후 전체를 커버


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_window_start(days: int = DEFAULT_WINDOW_DAYS) -> datetime:
    return utc_now() - timedelta(days=days)


def _as_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _doc_time(doc: SourceDocument) -> datetime | None:
    return _as_aware(doc.published_at or doc.ingestion_time)


def _incident_time(incident: Incident) -> datetime:
    return _as_aware(incident.created_at) or utc_now()


def classify_damage_severity(damage_summary: str | None) -> str:
    text = (damage_summary or '').lower()
    if not text:
        return '미상'
    high_keywords = ['killed', 'destroyed', 'major damage', 'severe', 'dozens', 'large fire',
                     'critical', 'fatalities', 'sunk', 'eliminated', 'inoperable', 'shot down']
    medium_keywords = ['injured', 'wounded', 'damaged', 'hit', 'casualties', 'fire', 'minor damage',
                       'intercepted', 'closed', 'halted']
    if any(k in text for k in high_keywords):
        return '높음'
    if any(k in text for k in medium_keywords):
        return '중간'
    return '낮음'


def get_recent_documents(db: Session, days: int = DEFAULT_WINDOW_DAYS) -> list[SourceDocument]:
    since = get_window_start(days)
    docs = db.query(SourceDocument).order_by(SourceDocument.published_at.desc(), SourceDocument.ingestion_time.desc()).all()
    return [doc for doc in docs if (_doc_time(doc) and _doc_time(doc) >= since)]


def get_all_documents(db: Session) -> list[SourceDocument]:
    """시간 필터 없이 전체 문서 반환."""
    return db.query(SourceDocument).order_by(SourceDocument.published_at.desc()).all()


def get_recent_incidents(db: Session, days: int = DEFAULT_WINDOW_DAYS) -> list[tuple[Incident, SourceDocument | None]]:
    since = get_window_start(days)
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    recent: list[tuple[Incident, SourceDocument | None]] = []
    for incident in incidents:
        doc = db.query(SourceDocument).filter(SourceDocument.id == incident.document_id).first()
        basis_time = _as_aware(doc.published_at) if doc and doc.published_at else _incident_time(incident)
        if basis_time and basis_time >= since:
            recent.append((incident, doc))
    return recent


def get_all_incidents(db: Session) -> list[tuple[Incident, SourceDocument | None]]:
    """시간 필터 없이 전체 사건 반환 — 지도용."""
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    result: list[tuple[Incident, SourceDocument | None]] = []
    for incident in incidents:
        doc = db.query(SourceDocument).filter(SourceDocument.id == incident.document_id).first()
        result.append((incident, doc))
    return result


def build_dashboard_metrics(db: Session, days: int = DEFAULT_WINDOW_DAYS) -> dict[str, Any]:
    # 지도 표시용은 전체 데이터 사용
    all_incidents = get_all_incidents(db)
    all_docs = get_all_documents(db)
    verified = [inc for inc, _ in all_incidents if inc.verified_status in {'verified', 'confirmed', 'partially_verified', 'likely'}]
    exact_mappable = [inc for inc, _ in all_incidents if inc.latitude is not None and inc.longitude is not None]
    fallback = max(len(all_incidents) - len(exact_mappable), 0)
    return {
        'window_days': days,
        'window_start': get_window_start(days).isoformat().replace('+00:00', 'Z'),
        'documents': len(all_docs),
        'incidents': len(all_incidents),
        'verified_incidents': len(verified),
        'mappable_incidents': len(exact_mappable),
        'fallback_mappable_incidents': fallback,
        'unmappable_incidents': max(len(all_incidents) - len(exact_mappable), 0),
    }
