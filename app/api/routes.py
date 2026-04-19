from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db


def require_admin(request: Request) -> None:
    """공개 모드일 경우 X-Admin-Token 헤더 또는 ?token=... 쿼리로 관리자 인증.
    PUBLIC_MODE=0 (기본, 로컬) 에서는 인증 없이 통과한다.
    """
    if not settings.public_mode:
        return
    expected = settings.admin_token
    if not expected:
        # 공개 모드인데 토큰이 설정되지 않았으면 안전을 위해 전부 차단
        raise HTTPException(status_code=503, detail="ADMIN_TOKEN 미설정으로 파이프라인 트리거 불가")
    supplied = request.headers.get("X-Admin-Token") or request.query_params.get("token")
    if supplied != expected:
        raise HTTPException(status_code=401, detail="관리자 토큰이 필요합니다")
from app.services.briefer import BriefingService
from app.services.extractor import IncidentExtractor
from app.services.mapper import MapService
from app.services.news_ingestor import GoogleNewsRSSIngestor
from app.services.reviewer import review_ingest_health
from app.services.reviewer import build_collection_advice
from app.services.reviewer import summarize_ingest_issue
from app.services.reporter import read_status, set_last_result, update_status
from app.services.dashboard import DEFAULT_WINDOW_DAYS, build_dashboard_metrics, classify_damage_severity, get_all_incidents
from app.services.seed_data import get_actor_side
from app.services.ko_translate import (
    translate_actor, translate_means, translate_location,
    translate_sentence, translate_verified_status,
)
from app.services.glossary import lookup as glossary_lookup

BASE_DIR = Path(__file__).resolve().parents[1]
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _format_incident(inc, doc):
    """템플릿 렌더링용 dict 생성."""
    actor = inc.actor or ""
    side = get_actor_side(actor)
    pub_date = ""
    if doc and doc.published_at:
        pub_date = doc.published_at.strftime("%Y-%m-%d %H:%M")
    elif inc.created_at:
        pub_date = inc.created_at.strftime("%Y-%m-%d %H:%M")
    return {
        "id": inc.id,
        "pub_date": pub_date,
        # 기본 표시는 한국어, 영어 원본은 *_en 필드로 유지 (클릭 시 토글에 사용)
        "actor": translate_actor(actor),
        "actor_en": actor or "Unknown",
        "target_actor": translate_actor(inc.target_actor),
        "target_actor_en": inc.target_actor or "-",
        "location_name": translate_location(inc.location_name),
        "location_name_en": inc.location_name or "-",
        "latitude": inc.latitude,
        "longitude": inc.longitude,
        "means": translate_means(inc.means),
        "means_en": inc.means or "-",
        "damage_summary": translate_sentence(inc.damage_summary),
        "damage_summary_en": inc.damage_summary or "-",
        "damage_severity": classify_damage_severity(inc.damage_summary),
        "confidence": inc.confidence,
        "verified_status": translate_verified_status(inc.verified_status),
        "verified_status_raw": inc.verified_status,
        "is_iran_side": side == "iran",
        "is_us_side": side == "us_israel",
        "actor_side": side,
        "source_url": doc.url if doc else "#",
        "source_title": doc.title if doc else "미상",
    }


def _build_war_status(incident_pairs) -> dict:
    """전쟁 경과일, 최근 이벤트 요약 정보를 반환한다."""
    from datetime import datetime, timezone as _tz, date as _date
    WAR_START = _date(2026, 2, 28)
    today = _date.today()
    war_day = (today - WAR_START).days + 1

    # 가장 최근 이벤트 찾기 (시간 역순)
    latest = None
    latest_t = None
    for inc, doc in incident_pairs:
        if doc and doc.published_at:
            t = doc.published_at
        else:
            t = inc.created_at
        if t and t.tzinfo is None:
            t = t.replace(tzinfo=_tz.utc)
        if t and (latest_t is None or t > latest_t):
            latest_t = t
            latest = (inc, doc)

    latest_info = None
    if latest:
        inc, doc = latest
        side = get_actor_side(inc.actor or "")
        latest_info = {
            "id": inc.id,
            "side": side,
            "actor_ko": translate_actor(inc.actor),
            "actor_en": inc.actor or "-",
            "target_ko": translate_actor(inc.target_actor) if inc.target_actor else "-",
            "target_en": inc.target_actor or "-",
            "location_ko": translate_location(inc.location_name) if inc.location_name else "-",
            "location_en": inc.location_name or "-",
            "damage_ko": translate_sentence(inc.damage_summary) if inc.damage_summary else "-",
            "damage_en": inc.damage_summary or "-",
            "date_str": latest_t.strftime("%Y-%m-%d %H:%M") if latest_t else "-",
            "means_ko": translate_means(inc.means) if inc.means else "-",
            "means_en": inc.means or "-",
        }

    return {
        "war_day": war_day,
        "war_start": "2026-02-28",
        "today": today.isoformat(),
        "latest": latest_info,
        "total_incidents": len(incident_pairs),
    }


def _build_strategic_analysis(incident_pairs) -> dict:
    """각 진영(이란, 미국/이스라엘, 기타)의 주요 이벤트를 전략적 목적과 함께 정리.
    returns: { "iran": [...], "us_israel": [...], "other": [...] }
    각 항목은 최대 5건의 고영향 이벤트, 시간 역순(최신 우선).
    """
    from datetime import timezone as _tz

    buckets: dict[str, list] = {"iran": [], "us_israel": [], "other": []}

    for inc, doc in incident_pairs:
        if not getattr(inc, "is_high_impact", False):
            continue
        side = get_actor_side(inc.actor or "")
        if doc and doc.published_at:
            t = doc.published_at
        else:
            t = inc.created_at
        if t and t.tzinfo is None:
            t = t.replace(tzinfo=_tz.utc)

        # 전략 평가를 한국어로 번역
        strat_ko = translate_sentence(inc.strategic_assessment) if inc.strategic_assessment else "-"
        tact_ko = translate_sentence(inc.tactical_assessment) if inc.tactical_assessment else "-"

        entry = {
            "id": inc.id,
            "date_str": t.strftime("%m/%d") if t else "-",
            "date_full": t.strftime("%Y-%m-%d") if t else "-",
            "actor_ko": translate_actor(inc.actor),
            "actor_en": inc.actor or "-",
            "target_ko": translate_actor(inc.target_actor) if inc.target_actor else "-",
            "target_en": inc.target_actor or "-",
            "location_ko": translate_location(inc.location_name) if inc.location_name else "-",
            "location_en": inc.location_name or "-",
            "means_ko": translate_means(inc.means) if inc.means else "-",
            "means_en": inc.means or "-",
            "damage_ko": translate_sentence(inc.damage_summary) if inc.damage_summary else "-",
            "damage_en": inc.damage_summary or "-",
            "strategic_ko": strat_ko,
            "strategic_en": inc.strategic_assessment or "-",
            "tactical_ko": tact_ko,
            "tactical_en": inc.tactical_assessment or "-",
            "confidence": inc.confidence,
            "_sort": t,
        }
        buckets[side].append(entry)

    # 각 진영 최대 5건, 최신 우선
    for side in buckets:
        buckets[side].sort(key=lambda x: x["_sort"] or "", reverse=True)
        buckets[side] = buckets[side][:5]
        for e in buckets[side]:
            del e["_sort"]

    return buckets


def _build_timeline(incident_pairs) -> list[dict]:
    """개전일(2026-02-28) 이후 주요 사건(고영향 이벤트)만 시간 오름차순으로 정리.
    각 원소는 타임라인 위젯이 바로 렌더할 수 있는 dict.
    """
    from datetime import datetime, timezone as _tz
    WAR_START = datetime(2026, 2, 28, tzinfo=_tz.utc)

    def _time_of(inc, doc):
        if doc and doc.published_at:
            t = doc.published_at
        else:
            t = inc.created_at
        if t and t.tzinfo is None:
            t = t.replace(tzinfo=_tz.utc)
        return t

    high_impact = []
    for inc, doc in incident_pairs:
        if not getattr(inc, "is_high_impact", False):
            continue
        t = _time_of(inc, doc)
        if not t:
            continue
        high_impact.append((t, inc, doc))
    high_impact.sort(key=lambda x: x[0])

    timeline: list[dict] = []
    for t, inc, doc in high_impact:
        day_num = (t.date() - WAR_START.date()).days + 1
        side = get_actor_side(inc.actor or "")
        actor_ko = translate_actor(inc.actor)
        target_ko = translate_actor(inc.target_actor) if inc.target_actor else "-"
        damage_ko = translate_sentence(inc.damage_summary) if inc.damage_summary else "-"
        # 타임라인 카드는 매우 간결해야 하므로 80자로 컷
        if len(damage_ko) > 90:
            damage_ko = damage_ko[:90] + "…"
        damage_en = (inc.damage_summary or "-")
        if len(damage_en) > 90:
            damage_en = damage_en[:90] + "…"
        # 전략/전술 평가
        strat_ko = translate_sentence(inc.strategic_assessment) if inc.strategic_assessment else ""
        tact_ko = translate_sentence(inc.tactical_assessment) if inc.tactical_assessment else ""
        means_ko = translate_means(inc.means) if inc.means else "-"
        timeline.append({
            "id": inc.id,
            "date_str": t.strftime("%m/%d"),
            "date_full": t.strftime("%Y-%m-%d"),
            "day_num": day_num,
            "side": side,
            "actor_ko": actor_ko,
            "actor_en": inc.actor or "-",
            "target_ko": target_ko,
            "target_en": inc.target_actor or "-",
            "damage_ko": damage_ko,
            "damage_en": damage_en,
            "location_ko": translate_location(inc.location_name) if inc.location_name else "-",
            "location_en": inc.location_name or "-",
            "means_ko": means_ko,
            "means_en": inc.means or "-",
            "strategic_ko": strat_ko,
            "strategic_en": inc.strategic_assessment or "",
            "tactical_ko": tact_ko,
            "tactical_en": inc.tactical_assessment or "",
            "latitude": inc.latitude,
            "longitude": inc.longitude,
        })
    return timeline


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    metrics = build_dashboard_metrics(db, DEFAULT_WINDOW_DAYS)
    # ★ 전체 데이터 표시 (시간 필터 없음)
    incident_pairs = get_all_incidents(db)[:100]
    incidents = [_format_incident(inc, doc) for inc, doc in incident_pairs]
    timeline = _build_timeline(incident_pairs)
    war_status = _build_war_status(incident_pairs)
    strategic = _build_strategic_analysis(incident_pairs)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "incidents": incidents,
            "timeline": timeline,
            "war_status": war_status,
            "strategic": strategic,
            "metrics": metrics,
            "report_status": read_status(),
            "public_mode": settings.public_mode,
            "site_title": settings.site_title,
        },
    )


@router.post("/pipeline/run")
def run_pipeline(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    days = DEFAULT_WINDOW_DAYS
    update_status(state="running", step="데이터 수집 중", message="Google News RSS 및 GDELT에서 관련 기사를 수집하고 있습니다.")
    ingestor_stats = GoogleNewsRSSIngestor(db).ingest(max_per_query=30, days=days)

    update_status(state="running", step="사건 추출 중", message="행위자, 위치, 공격수단, 피해 정보를 추출 중입니다.")
    extractor = IncidentExtractor(db)
    before_unextracted = extractor.count_unextracted_documents()
    extracted = extractor.extract_new_documents()
    after_unextracted = extractor.count_unextracted_documents()

    update_status(state="running", step="지도 생성 중", message="좌표 보정 및 지도 렌더링 중입니다.")
    map_path = MapService(db).build_map()

    update_status(state="running", step="브리핑 작성 중", message="HTML 브리핑을 생성 중입니다.")
    brief_path = BriefingService(db).build_daily_html()

    metrics = build_dashboard_metrics(db, days)
    health = review_ingest_health(ingestor_stats, metrics)
    message = summarize_ingest_issue(ingestor_stats, metrics)

    result = {
        "status": "ok",
        "message": message,
        "ingest": ingestor_stats,
        "extract": {"before_unextracted": before_unextracted, "extracted": extracted, "after_unextracted": after_unextracted},
        "totals": metrics,
        "map_url": "/map",
        "health": health,
        "advice": build_collection_advice(ingestor_stats, metrics),
    }
    set_last_result(result)
    update_status(state="completed", step="완료", message=message)
    return result


@router.post("/pipeline/refresh")
def refresh_outputs(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    update_status(state="running", step="재처리 중", message="좌표 보정 및 출력물 재생성 중입니다.")
    backfilled = IncidentExtractor(db).backfill_missing_locations()
    map_path = MapService(db).build_map()
    brief_path = BriefingService(db).build_daily_html()
    metrics = build_dashboard_metrics(db)
    result = {
        "status": "ok",
        "message": f"출력물을 재생성했습니다. 좌표보정: {backfilled}건",
        "location_backfilled": backfilled,
        "totals": metrics,
    }
    set_last_result(result)
    update_status(state="completed", step="완료", message=result["message"])
    return result


@router.get("/report/status")
def report_status():
    return read_status()


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    return build_dashboard_metrics(db)


@router.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return [_format_incident(i, doc) for i, doc in get_all_incidents(db)]


@router.get("/map")
def get_map(db: Session = Depends(get_db)):
    path = MapService(db).build_map()
    return FileResponse(path)


@router.get("/brief/daily")
def get_daily_brief(db: Session = Depends(get_db)):
    path = BriefingService(db).build_daily_html()
    return FileResponse(path)


@router.get("/api/glossary")
def api_glossary(term: str = Query("", description="조회할 용어 (공격수단, 표적, 행위자)")):
    """용어 사전 조회. 프런트엔드 모달이 호출한다.

    Returns:
        {
          found: bool,
          query: str,
          category: "weapon" | "target" | "actor" | "unknown",
          name_ko, name_en, desc_ko,
          wiki_ko, wiki_en,
        }
    """
    return glossary_lookup(term)


@router.get("/api/db/summary")
def api_db_summary(db: Session = Depends(get_db)):
    """현재 DB에 저장된 수집 결과 요약 (재수집 중복 방지 안내용)."""
    from app.models.entities import Incident, SourceDocument
    from sqlalchemy import func
    doc_count = db.query(func.count(SourceDocument.id)).scalar() or 0
    inc_count = db.query(func.count(Incident.id)).scalar() or 0
    last_doc = db.query(func.max(SourceDocument.published_at)).scalar()
    last_ingest = db.query(func.max(SourceDocument.ingestion_time)).scalar()
    first_doc = db.query(func.min(SourceDocument.published_at)).scalar()
    return {
        "documents_saved": doc_count,
        "incidents_saved": inc_count,
        "earliest_event": first_doc.isoformat() if first_doc else None,
        "latest_event": last_doc.isoformat() if last_doc else None,
        "last_ingest_at": last_ingest.isoformat() if last_ingest else None,
        "note": "이미 저장된 문서/사건은 재수집 시 중복 삽입되지 않습니다 (URL/콘텐츠 해시 기준 dedup)."
    }


# ──────────────────────────────────────────────
# 사용자 피드백
# ──────────────────────────────────────────────
from pydantic import BaseModel, Field

class FeedbackIn(BaseModel):
    category: str = Field("general", pattern="^(general|translation|data_error|feature_request)$")
    message: str = Field(..., min_length=2, max_length=1000)
    rating: int | None = Field(None, ge=1, le=5)

@router.post("/api/feedback")
def submit_feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    from app.models.entities import Feedback
    fb = Feedback(category=body.category, message=body.message, rating=body.rating)
    db.add(fb)
    db.commit()
    return {"status": "ok", "message": "피드백이 등록되었습니다. 감사합니다!"}

@router.get("/api/feedback")
def list_feedback(db: Session = Depends(get_db)):
    from app.models.entities import Feedback
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(50).all()
    return [
        {"id": r.id, "category": r.category, "message": r.message,
         "rating": r.rating, "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]


@router.post("/pipeline/seed")
def seed_data(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    from app.services.seed_data import seed_sample_data
    update_status(state="running", step="검증 데이터 삽입 중", message="2026 이란전쟁 검증 이벤트를 삽입합니다.")
    result = seed_sample_data(db, force=True)

    update_status(state="running", step="지도 생성 중", message="검증 데이터로 지도를 생성합니다.")
    MapService(db).build_map()

    update_status(state="running", step="브리핑 작성 중", message="검증 데이터로 브리핑을 생성합니다.")
    BriefingService(db).build_daily_html()

    metrics = build_dashboard_metrics(db)
    final = {
        "status": "ok",
        "message": f"검증 데이터 로드 완료: 문서 {result['documents_inserted']}건, 사건 {result['incidents_inserted']}건",
        "seed_result": result,
        "totals": metrics,
    }
    set_last_result(final)
    update_status(state="completed", step="완료", message=final["message"])
    return final
