from __future__ import annotations
import atexit
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
import app.models.entities  # noqa: F401 – register all models before create_all

# ── 로깅 설정 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("osint")

Base.metadata.create_all(bind=engine)

# ── 스키마 마이그레이션: 기존 DB에 새 컬럼 추가 ──
def _migrate_schema():
    """기존 테이블에 누락된 컬럼을 안전하게 추가한다 (ALTER TABLE)."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    migrations = [
        ("feedbacks", "ip_hash", "VARCHAR(64)"),
        ("page_views", "ip_hash", "VARCHAR(64)"),
        ("page_views", "user_agent", "VARCHAR(500)"),
    ]
    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if table in inspector.get_table_names():
                existing_cols = {c["name"] for c in inspector.get_columns(table)}
                if column not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    logger.info("Migration: added %s.%s", table, column)
        conn.commit()

try:
    _migrate_schema()
except Exception as e:
    logger.warning("Schema migration skipped: %s", e)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# ── 스케줄러 전역 참조 (graceful shutdown 용) ──
_scheduler = None


def _run_pipeline_job():
    """백그라운드 스케줄러에서 호출되는 파이프라인 실행 함수."""
    from datetime import datetime, timezone
    from app.services.news_ingestor import GoogleNewsRSSIngestor
    from app.services.extractor import IncidentExtractor
    from app.services.mapper import MapService
    from app.services.briefer import BriefingService

    logger.info("Pipeline run started at %s", datetime.now(timezone.utc).isoformat())
    db = SessionLocal()
    try:
        # 1) 뉴스 수집
        ingestor_stats = GoogleNewsRSSIngestor(db).ingest(max_per_query=30, days=7)
        logger.info("Ingest complete: inserted=%d, feed_seen=%d, dup_feed=%d, dup_db=%d",
                    ingestor_stats.get("inserted", 0),
                    ingestor_stats.get("feed_entries_seen", 0),
                    ingestor_stats.get("duplicate_in_feed", 0),
                    ingestor_stats.get("duplicate_in_db", 0))

        # 2) 사건 추출
        extractor = IncidentExtractor(db)
        extracted = extractor.extract_new_documents()
        logger.info("Extracted %d new incidents", extracted)

        # 3) 좌표 보정
        backfilled = extractor.backfill_missing_locations()
        logger.info("Backfilled %d locations", backfilled)

        # 4) 지도 + 브리핑 재생성
        MapService(db).build_map()
        BriefingService(db).build_daily_html()
        logger.info("Map + Briefing regenerated successfully")
    except Exception as e:
        logger.error("Pipeline failed: %s", e, exc_info=True)
    finally:
        db.close()


def _startup_seed():
    """Auto-seed verified data on startup."""
    from app.services.seed_data import seed_sample_data
    db = SessionLocal()
    try:
        result = seed_sample_data(db, force=True)
        logger.info("Seeded %d documents, %d incidents (force=True)",
                    result.get("documents_inserted", 0),
                    result.get("incidents_inserted", 0))
    except Exception as e:
        logger.error("Seed failed: %s", e, exc_info=True)
    finally:
        db.close()


def _startup_translation_warmup():
    """앱 시작 시 번역 캐시를 백그라운드 스레드로 채운다.

    누적된 모든 사건의 텍스트를 7개 언어로 미리 번역해 translations 테이블에
    저장한다. 한 번 채우면 재배포·재시작 후에도 DB에서 즉시 재사용된다.
    앱 부팅을 막지 않도록 데몬 스레드로 실행한다.
    """
    import threading

    def _worker():
        import time
        time.sleep(8)  # 시드/서버 기동 안정화 대기
        try:
            from app.services import translation_cache
            from app.models.entities import Incident

            db = SessionLocal()
            try:
                incidents = db.query(Incident).all()
                sentences: list[str] = []
                shorts: list[str] = []
                for inc in incidents:
                    for t in (inc.damage_summary, inc.tactical_assessment,
                              inc.strategic_assessment):
                        if t:
                            sentences.append(t)
                    for t in (inc.location_name, inc.means, inc.actor,
                              inc.target_actor):
                        if t:
                            shorts.append(t)
            finally:
                db.close()

            logger.info("번역 워밍업 시작 — 문장 %d건, 단문 %d건",
                        len(sentences), len(shorts))
            # 문장: 한국어 포함 6개 언어 / 단문: 한국어는 사전 사용하므로 5개 언어
            translation_cache.warmup(sentences, ["ko", "es", "zh", "ja", "fr", "de"])
            translation_cache.warmup(shorts, ["es", "zh", "ja", "fr", "de"])
            logger.info("번역 워밍업 종료 — 캐시 %d개 항목",
                        translation_cache.cache_size())
        except Exception as e:
            logger.warning("번역 워밍업 스레드 실패: %s", e, exc_info=True)

    threading.Thread(target=_worker, daemon=True, name="translation-warmup").start()
    logger.info("번역 워밍업 스레드 예약됨")


def _startup_scheduler():
    """앱 시작 시 백그라운드 스케줄러 등록."""
    global _scheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from datetime import datetime, timedelta, timezone

    interval_hours = int(os.getenv("PIPELINE_INTERVAL_HOURS", "6"))

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_pipeline_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id="pipeline_periodic",
        name=f"Pipeline (every {interval_hours}h)",
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=60),
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Background scheduler started — pipeline runs every %d hours", interval_hours)


def _shutdown_scheduler():
    """Graceful shutdown: 스케줄러 정리."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler shut down")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: startup/shutdown 대체 (deprecation 경고 해소)."""
    _startup_seed()
    _startup_translation_warmup()
    _startup_scheduler()
    yield
    _shutdown_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 프로세스 비정상 종료 시에도 스케줄러 정리
atexit.register(_shutdown_scheduler)
