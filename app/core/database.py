from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

# SQLite: check_same_thread=False 필수
# PostgreSQL: 커넥션 풀 최적화 (pool_size, max_overflow, pool_pre_ping)
if _is_sqlite:
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
else:
    engine = create_engine(
        settings.database_url,
        future=True,
        pool_size=5,           # 기본 유지 커넥션 수
        max_overflow=10,       # 추가 허용 커넥션
        pool_pre_ping=True,    # 커넥션 유효성 자동 검사 (끊어진 연결 재생성)
        pool_recycle=1800,     # 30분마다 커넥션 재활용 (Render/Railway 유휴 타임아웃 대응)
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
