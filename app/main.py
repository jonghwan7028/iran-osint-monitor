from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
import app.models.entities  # noqa: F401 – register all models before create_all

Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)  # 프로덕션에서 빈 폴더 자동 생성

app = FastAPI(title=settings.app_name)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _run_pipeline_job():
    """백그라운드 스케줄러에서 호출되는 파이프라인 실행 함수."""
    from datetime import datetime, timezone
    from app.services.news_ingestor import GoogleNewsRSSIngestor
    from app.services.extractor import IncidentExtractor
    from app.services.mapper import MapService
    from app.services.briefer import BriefingService
    print(f"[Scheduler] Pipeline run started at {datetime.now(timezone.utc).isoformat()}")
    db = SessionLocal()
    try:
        # 1) 뉴스 수집
        ingestor_stats = GoogleNewsRSSIngestor(db).ingest(max_per_query=30, days=7)
        print(f"[Scheduler] Ingest: {ingestor_stats}")

        # 2) 사건 추출
        extractor = IncidentExtractor(db)
        extracted = extractor.extract_new_documents()
        print(f"[Scheduler] Extracted: {extracted} new incidents")

        # 3) 좌표 보정
        backfilled = extractor.backfill_missing_locations()
        print(f"[Scheduler] Backfilled: {backfilled} locations")

        # 4) 지도 + 브리핑 재생성
        MapService(db).build_map()
        BriefingService(db).build_daily_html()
        print(f"[Scheduler] Map + Briefing regenerated")
    except Exception as e:
        print(f"[Scheduler] Pipeline failed: {e}")
    finally:
        db.close()


@app.on_event("startup")
def startup_seed():
    """Auto-seed verified data on startup."""
    from app.services.seed_data import seed_sample_data
    db = SessionLocal()
    try:
        result = seed_sample_data(db, force=True)
        print(
            f"[Startup] Seeded {result.get('documents_inserted', 0)} new documents, "
            f"{result.get('incidents_inserted', 0)} new incidents (force=True)"
        )
    except Exception as e:
        print(f"[Startup] Seed failed: {e}")
    finally:
        db.close()


@app.on_event("startup")
def startup_scheduler():
    """앱 시작 시 백그라운드 스케줄러 등록.

    - 시작 직후 1회 파이프라인 실행 (30초 지연)
    - 이후 6시간마다 자동 실행
    - Render 무료 플랜의 cron job 미지원 문제를 해결
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from datetime import datetime, timedelta, timezone

    # 스케줄러 간격 (환경변수로 조정 가능, 기본 6시간)
    interval_hours = int(os.getenv("PIPELINE_INTERVAL_HOURS", "6"))

    scheduler = BackgroundScheduler(timezone="UTC")

    # 주기적 실행
    scheduler.add_job(
        _run_pipeline_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id="pipeline_periodic",
        name=f"Pipeline (every {interval_hours}h)",
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=60),  # 시작 후 60초 뒤 1회 실행
        replace_existing=True,
    )

    scheduler.start()
    print(f"[Startup] Background scheduler started — pipeline runs every {interval_hours} hours")
