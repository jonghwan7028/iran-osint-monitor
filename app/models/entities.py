from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), default="en")
    query_used: Mapped[str | None] = mapped_column(String(300), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_reliability: Mapped[float] = mapped_column(Float, default=0.5)
    ingestion_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    incidents: Mapped[list[Incident]] = relationship(back_populates="document")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), default="military_event")
    actor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_actor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    means: Mapped[str | None] = mapped_column(String(300), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    damage_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tactical_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategic_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    verified_status: Mapped[str] = mapped_column(String(50), default="partially_verified")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_high_impact: Mapped[bool] = mapped_column(Boolean, default=False)

    document: Mapped[SourceDocument] = relationship(back_populates="incidents")


class PageView(Base):
    """페이지 방문 기록."""
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    visited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 익명화된 IP
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Feedback(Base):
    """사용자 피드백 / 건의사항."""
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(50), default="general")  # general, translation, data_error, feature_request
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 익명화된 IP
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
