from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
import app.models.entities  # noqa: F401 – register all models before create_all

Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.on_event("startup")
def startup_seed():
    """Auto-seed verified data on startup.
    force=True 로 호출하므로 기존 DB 에 이미 저장된 URL/해시 는 건너뛰고
    seed_data.py 에 새로 추가된 검증 이벤트만 삽입된다.
    (v12e: 4/8 ~ 4/15 이벤트가 추가되어 있음)
    """
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
