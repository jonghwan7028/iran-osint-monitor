from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import feedback_limiter, public_limiter


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
import re as _re

BASE_DIR = Path(__file__).resolve().parents[1]
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ── 출처 유형 분류 (#4) ──
def _classify_source_type(publisher: str) -> dict:
    """매체 이름으로 출처 유형(정부/통신사/방송/신문/OSINT/참고/기타) 분류."""
    pub = (publisher or "").lower()
    if any(k in pub for k in ["pentagon", "ministry", "centcom", "idf", "government",
                               "state department", "house of commons"]):
        return {"type": "government", "ko": "정부 발표", "en": "Official", "icon": "🏛️", "cls": "src-gov"}
    if any(k in pub for k in ["reuters", "ap ", "associated press", "afp"]):
        return {"type": "wire", "ko": "통신사", "en": "Wire", "icon": "📡", "cls": "src-wire"}
    if any(k in pub for k in ["cnn", "bbc", "al jazeera", "nbc", "cbs", "npr", "fox"]):
        return {"type": "broadcast", "ko": "방송사", "en": "Broadcast", "icon": "📺", "cls": "src-broadcast"}
    if any(k in pub for k in ["nyt", "washington post", "times of israel", "guardian"]):
        return {"type": "newspaper", "ko": "신문", "en": "Press", "icon": "📰", "cls": "src-press"}
    if any(k in pub for k in ["bellingcat", "satellite", "maxar", "planet", "osint"]):
        return {"type": "osint", "ko": "OSINT", "en": "OSINT", "icon": "🛰️", "cls": "src-osint"}
    if any(k in pub for k in ["wikipedia", "britannica", "crs"]):
        return {"type": "reference", "ko": "참고자료", "en": "Reference", "icon": "📚", "cls": "src-ref"}
    return {"type": "other", "ko": "기타", "en": "Other", "icon": "📄", "cls": "src-other"}


# ── KIA 추정 (#전쟁배너) ──
def _estimate_casualties(incident_pairs) -> dict:
    """damage_summary 텍스트에서 사상자 수를 추출하여 진영별 합산.
    피해자는 target_actor의 진영으로 분류한다 (공격 당한 쪽의 손실).
    evidence 리스트도 함께 반환하여 UI에서 근거를 표시할 수 있도록 한다.
    """
    stats = {
        "us_israel": {"military_kia": 0, "civilian_kia": 0, "wounded": 0},
        "iran":      {"military_kia": 0, "civilian_kia": 0, "wounded": 0},
    }
    evidence = []  # 근거 리스트: [{side, cat, n, phrase, source, actor, target}]

    for inc, doc in incident_pairs:
        dmg = (inc.damage_summary or "")
        target_side = get_actor_side(inc.target_actor or "")
        actor_side  = get_actor_side(inc.actor or "")
        source_name = doc.publisher if doc else ""

        # 사망 패턴: "X killed", "X [words] killed", "X dead", "X eliminated"
        for m in _re.finditer(r'(\d+)\s+[\w\s]{0,40}?\b(?:killed|dead|eliminated|사망)', dmg, _re.IGNORECASE):
            n = int(m.group(1))
            context = m.group(0).lower()
            # 누가 죽었는지 판별
            if any(w in context for w in ["attacker", "militia fighter"]):
                side = actor_side
                cat = "military_kia"
            elif any(w in context for w in ["civilian", "children", "resident"]):
                side = target_side if target_side in stats else "iran"
                cat = "civilian_kia"
            elif any(w in context for w in ["sailor", "crew", "idf", "personnel", "soldier",
                                            "officer", "cleric", "operativ", "service member"]):
                if any(w in context for w in ["us ", "american", "idf personnel", "idf killed"]):
                    side = "us_israel"
                elif any(w in context for w in ["irgc", "hezbollah", "houthi", "militia",
                                                "iranian", "operativ"]):
                    side = "iran"
                elif "idf" in context and "hezbollah" not in context:
                    side = "us_israel"
                elif "sailor" in context or "crew" in context:
                    side = target_side if target_side in stats else "us_israel"
                else:
                    side = target_side if target_side in stats else "iran"
                cat = "military_kia"
            else:
                side = target_side if target_side in stats else "iran"
                cat = "military_kia"
            if side in stats:
                stats[side][cat] += n
                evidence.append({
                    "side": side, "cat": cat, "n": n,
                    "phrase": m.group(0).strip(),
                    "source": source_name,
                    "actor": inc.actor or "", "target": inc.target_actor or "",
                })

        # "Khamenei killed" 등 이름 단위 사망 (숫자 없음) — 주요 인물 1명씩
        for pattern in [r'(?:Khamenei|Ghaani|commander)\s+(?:killed|eliminated|dead)',
                        r'(?:killed|eliminated)\s+(?:Khamenei|Ghaani|commander)']:
            mm = _re.search(pattern, dmg, _re.IGNORECASE)
            if mm:
                side = target_side if target_side in stats else "iran"
                stats[side]["military_kia"] += 1
                evidence.append({
                    "side": side, "cat": "military_kia", "n": 1,
                    "phrase": mm.group(0).strip(),
                    "source": source_name,
                    "actor": inc.actor or "", "target": inc.target_actor or "",
                })

        # 부상 패턴: "X wounded", "X injured"
        for m in _re.finditer(r'(\d+)\s+[\w\s]{0,30}?\b(?:wounded|injured|부상)', dmg, _re.IGNORECASE):
            n = int(m.group(1))
            context = m.group(0).lower()
            if any(w in context for w in ["us ", "american", "sailor"]):
                side = "us_israel"
            elif any(w in context for w in ["iranian", "irgc", "hezbollah", "police"]):
                side = "iran"
            else:
                side = target_side if target_side in stats else "iran"
            if side in stats:
                stats[side]["wounded"] += n
                evidence.append({
                    "side": side, "cat": "wounded", "n": n,
                    "phrase": m.group(0).strip(),
                    "source": source_name,
                    "actor": inc.actor or "", "target": inc.target_actor or "",
                })

    return {"stats": stats, "evidence": evidence}


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
        "verified_status_5level": inc.verified_status,
        "verified_status_raw": inc.verified_status,
        "is_iran_side": side == "iran",
        "is_us_side": side == "us_israel",
        "actor_side": side,
        "source_url": doc.url if doc else "#",
        "source_publisher": doc.publisher if doc else "Unknown",
        "source_published_at": doc.published_at.isoformat() if doc and doc.published_at else None,
        "source_title": doc.title if doc else "미상",
        "source_type": _classify_source_type(doc.publisher if doc else ""),
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

    # KIA 통계 (전쟁 배너에 표시) + 근거 evidence
    _cas_result = _estimate_casualties(incident_pairs)
    casualties = _cas_result["stats"]
    cas_evidence = _cas_result["evidence"]

    # 핵심 사건 TOP 3 — ID만 추출하여 타임라인에서 별표 표시
    _sorted_by_conf = sorted(incidents, key=lambda x: x.get("confidence", 0), reverse=True)
    top_incident_ids = {x["id"] for x in _sorted_by_conf[:3]}
    # 타임라인 아이템에 is_top 플래그 부여
    for tev in timeline:
        tev["is_top"] = tev["id"] in top_incident_ids

    # Determine data mode
    report = read_status()
    doc_count = metrics.get("documents_in_window", 0)
    state = report.get("state", "idle")
    if doc_count > 0 and state == "completed":
        data_mode = "live"
    elif doc_count > 0:
        data_mode = "demo"
    else:
        data_mode = "offline"

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
            "report_status": report,
            "data_mode": data_mode,
            "public_mode": settings.public_mode,
            "site_title": settings.site_title,
            "casualties": casualties,
            "cas_evidence": cas_evidence,
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
    update_status(state="running", step="재처리 중", message="검증 재평가, 좌표 보정 및 출력물 재생성 중입니다.")

    # 1) 기존 사건의 검증 상태를 현재 로직으로 재평가
    from app.models.entities import Incident, SourceDocument
    from app.services.verifier import VerificationService
    verifier = VerificationService()
    reverified = 0
    all_incidents = db.query(Incident).all()
    for inc in all_incidents:
        doc = db.query(SourceDocument).filter(SourceDocument.id == inc.document_id).first()
        if not doc:
            continue
        incident_fields = {
            "actor": inc.actor, "means": inc.means, "target_type": inc.target_type,
            "location_name": inc.location_name, "damage_summary": inc.damage_summary,
        }
        new_conf, new_status = verifier.score(doc, incident_fields)
        if inc.verified_status != new_status or abs(inc.confidence - new_conf) > 0.01:
            inc.confidence = new_conf
            inc.verified_status = new_status
            inc.is_high_impact = new_conf >= 0.8 and any(
                k for k in [inc.damage_summary, inc.target_type] if k
            )
            reverified += 1
    db.commit()

    # 2) 좌표 보정
    backfilled = IncidentExtractor(db).backfill_missing_locations()

    # 3) 출력물 재생성
    map_path = MapService(db).build_map()
    brief_path = BriefingService(db).build_daily_html()
    metrics = build_dashboard_metrics(db)
    result = {
        "status": "ok",
        "message": f"출력물을 재생성했습니다. 재검증: {reverified}건, 좌표보정: {backfilled}건",
        "reverified": reverified,
        "location_backfilled": backfilled,
        "totals": metrics,
    }
    set_last_result(result)
    update_status(state="completed", step="완료", message=result["message"])
    return result


@router.get("/api/methodology")
def api_methodology():
    """OSINT 방법론 및 파이프라인 개요."""
    return {
        "methodology": {
            "ko": {
                "data_collection": "Google News RSS + GDELT 시간당 수집",
                "deduplication": "3단계 중복제거 (URL unique, 콘텐츠 해시, 피드 내장)",
                "extraction": "규칙 기반 키워드 매칭 (행위자, 수단, 대상, 위치)",
                "verification": "5단계 확정도 시스템 (확인됨/유력/주장/논쟁중/철회됨)",
                "confidence_scoring": "출처 신뢰도 + 증거 요소 기반 (0.05~0.99)",
                "location_inference": "96개 지점 지리 추론 (utils.py)",
            },
            "en": {
                "data_collection": "Hourly ingest from Google News RSS + GDELT",
                "deduplication": "3-layer dedup (URL unique, content hash, feed-level in-memory)",
                "extraction": "Rule-based keyword matching (actors, means, targets, locations)",
                "verification": "5-level verification system (confirmed/likely/claimed/disputed/retracted)",
                "confidence_scoring": "Source reliability + evidence factors (0.05-0.99)",
                "location_inference": "96-place geo lookup from utils.py",
            }
        }
    }


@router.get("/api/pipeline/status")
def api_pipeline_status(db: Session = Depends(get_db)):
    """파이프라인 상태 및 데이터베이스 통계."""
    from app.models.entities import Incident, SourceDocument
    from sqlalchemy import func

    status = read_status()
    doc_count = db.query(func.count(SourceDocument.id)).scalar() or 0
    inc_count = db.query(func.count(Incident.id)).scalar() or 0
    last_ingest = db.query(func.max(SourceDocument.ingestion_time)).scalar()

    return {
        "last_run_at": status.get("updated_at"),
        "last_success_at": status.get("last_success_at"),
        "last_failure_reason": status.get("last_failure_reason"),
        "current_state": status.get("state", "idle"),
        "documents_total": doc_count,
        "incidents_total": inc_count,
        "last_ingest_at": last_ingest.isoformat() if last_ingest else None,
    }


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
def submit_feedback(body: FeedbackIn, request: Request, db: Session = Depends(get_db)):
    feedback_limiter.check(request)
    import hashlib
    from app.models.entities import Feedback
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    fb = Feedback(category=body.category, message=body.message, rating=body.rating, ip_hash=ip_hash)
    db.add(fb)
    db.commit()
    return {"status": "ok", "message": "Thank you for your feedback!"}

@router.get("/api/feedback")
def list_feedback(db: Session = Depends(get_db)):
    """피드백 전체 목록 (최근 200건)."""
    from app.models.entities import Feedback
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(200).all()
    return [
        {"id": r.id, "category": r.category, "message": r.message,
         "rating": r.rating, "ip_hash": r.ip_hash,
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]

@router.get("/api/feedback/summary")
def feedback_summary(db: Session = Depends(get_db)):
    """피드백 통계 요약 — 관리자용."""
    from sqlalchemy import func
    from app.models.entities import Feedback
    total = db.query(Feedback).count()
    by_cat = dict(db.query(Feedback.category, func.count()).group_by(Feedback.category).all())
    avg_rating = db.query(func.avg(Feedback.rating)).filter(Feedback.rating.isnot(None)).scalar()
    return {
        "total": total,
        "by_category": by_cat,
        "average_rating": round(float(avg_rating), 1) if avg_rating else None,
    }


# ── 방문자 카운터 (초기값 12,457) ──
_VISITOR_BASE = 12457

@router.post("/api/pageview")
def record_pageview(request: Request, db: Session = Depends(get_db)):
    """페이지 방문 기록 (프론트에서 페이지 로드 시 호출)."""
    public_limiter.check(request)
    import hashlib
    from datetime import datetime as _dt, timezone
    from app.models.entities import PageView
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    ua = request.headers.get("user-agent", "")[:500]
    pv = PageView(ip_hash=ip_hash, user_agent=ua)
    db.add(pv)
    db.commit()
    total = db.query(PageView).count() + _VISITOR_BASE
    today_start = _dt.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today = db.query(PageView).filter(PageView.visited_at >= today_start).count()
    return {"total": total, "today": today}


@router.get("/api/pageview")
def get_pageview_stats(db: Session = Depends(get_db)):
    """방문 통계 조회."""
    from datetime import datetime as _dt, timezone
    from app.models.entities import PageView
    total = db.query(PageView).count() + _VISITOR_BASE
    today_start = _dt.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today = db.query(PageView).filter(PageView.visited_at >= today_start).count()
    return {"total": total, "today": today}


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
