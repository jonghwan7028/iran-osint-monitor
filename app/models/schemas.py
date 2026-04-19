from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IncidentOut(BaseModel):
    id: int
    event_type: str
    actor: Optional[str] = None
    target_actor: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    means: Optional[str] = None
    target_type: Optional[str] = None
    damage_summary: Optional[str] = None
    tactical_assessment: Optional[str] = None
    strategic_assessment: Optional[str] = None
    confidence: float
    verified_status: str
    created_at: datetime

    class Config:
        from_attributes = True
