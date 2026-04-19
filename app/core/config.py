from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "app" / "data" / "osint.db"

def _normalize_db_url(raw: str) -> str:
    """Render/Heroku 의 postgres:// prefix 를 SQLAlchemy 가 기대하는 postgresql+psycopg:// 로 보정."""
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw[len("postgres://"):]
    if raw.startswith("postgresql://") and "+" not in raw.split("://", 1)[0]:
        return "postgresql+psycopg://" + raw[len("postgresql://"):]
    return raw


@dataclass
class Settings:
    database_url: str = _normalize_db_url(os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"))
    app_name: str = "Iran-US War OSINT Monitor v14-noGPT"
    # 공개 모드: 관리자 버튼을 UI 에서 숨기고 /pipeline/* 호출엔 X-Admin-Token 필수.
    public_mode: bool = os.getenv("PUBLIC_MODE", "0").lower() in ("1", "true", "yes", "y")
    admin_token: str | None = os.getenv("ADMIN_TOKEN")
    site_title: str = os.getenv("SITE_TITLE", "이란-미국 전쟁 OSINT 모니터")
    http_timeout: int = int(os.getenv("HTTP_TIMEOUT", "20"))
    user_agent: str = os.getenv("HTTP_USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    default_queries: List[str] = field(
        default_factory=lambda: [
            '"Iran war" OR "Iran conflict" 2026',
            'Iran missile strike Israel OR US base 2026',
            'US strike Iran OR Israel strike Iran 2026',
            'Strait of Hormuz Iran 2026',
            'Iran war ceasefire OR diplomacy 2026',
            'Hezbollah Lebanon Israel 2026',
            'IRGC attack OR Iran drone 2026',
        ]
    )
    trusted_domains: List[str] = field(
        default_factory=lambda: [
            "reuters.com", "apnews.com", "bbc.com", "cnn.com", "nytimes.com",
            "washingtonpost.com", "theguardian.com", "aljazeera.com", "france24.com",
            "npr.org", "state.gov", "defense.gov", "whitehouse.gov", "iranintl.com",
            "nbcnews.com", "cbsnews.com", "timesofisrael.com", "britannica.com",
        ]
    )

settings = Settings()
