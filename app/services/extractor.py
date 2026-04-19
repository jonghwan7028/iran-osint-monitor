from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import Incident, SourceDocument
from app.services.utils import first_match, infer_location_from_text
from app.services.verifier import VerificationService


class IncidentExtractor:
    """규칙 기반 사건 추출기 (OpenAI 미사용 버전).

    키워드 매칭 + 정규식으로 행위자, 수단, 표적, 위치, 피해 정보를 추출한다.
    """

    ACTORS = ["United States", "US", "Iran", "Israel", "Houthis", "Saudi Arabia"]
    MEANS = ["missile", "drone", "airstrike", "strike", "rocket", "fighter jet", "bombing", "cyberattack"]
    TARGET_TYPES = ["air base", "military base", "oil facility", "nuclear site", "port", "airport", "embassy", "base"]

    def __init__(self, db: Session):
        self.db = db
        self.verifier = VerificationService()

    def _simple_extract(self, doc: SourceDocument) -> dict[str, Any]:
        text = f"{doc.title}. {doc.raw_text}"
        actor = first_match(text, self.ACTORS)
        target_actor = "Iran" if actor in ["United States", "US"] else "United States" if actor == "Iran" else None
        means = first_match(text, self.MEANS)
        target_type = first_match(text, self.TARGET_TYPES)

        location_name, lat, lon = infer_location_from_text(text)

        damage_summary = None
        damage_patterns = [
            r"([^.]{0,60}(wounded|injured|killed|damaged|destroyed|casualties)[^.]{0,180})",
            r"([^.]{0,60}(no casualties|minor damage|major damage|severe damage)[^.]{0,180})",
        ]
        for pattern in damage_patterns:
            m = re.search(pattern, text, flags=re.IGNORECASE)
            if m:
                damage_summary = m.group(1).strip()
                break

        tactical = None
        strategic = None
        lowered = text.lower()
        if target_type in ["air base", "military base", "nuclear site", "base"]:
            tactical = "Likely intended to degrade military operational capability or signal deterrence."
        if any(k in lowered for k in ["talks", "negotiation", "ceasefire", "pressure", "deterrence"]):
            strategic = "Likely linked to coercive diplomacy, deterrence signaling, or escalation management."

        tactical = tactical or ("Likely intended to disrupt military activity or signaling." if means else tactical)

        return {
            "event_type": "strike" if means else "security_event",
            "actor": actor,
            "target_actor": target_actor,
            "location_name": location_name,
            "latitude": lat,
            "longitude": lon,
            "means": means,
            "target_type": target_type,
            "damage_summary": damage_summary,
            "tactical_assessment": tactical,
            "strategic_assessment": strategic,
        }

    def extract_new_documents(self) -> int:
        docs = (
            self.db.query(SourceDocument)
            .outerjoin(Incident, SourceDocument.id == Incident.document_id)
            .filter(Incident.id.is_(None))
            .all()
        )
        count = 0
        for doc in docs:
            incident_fields = self._simple_extract(doc)
            confidence, status = self.verifier.score(doc, incident_fields)
            incident = Incident(
                document_id=doc.id,
                confidence=confidence,
                verified_status=status,
                is_high_impact=confidence >= 0.8 and any(
                    k for k in [incident_fields.get("damage_summary"), incident_fields.get("target_type")] if k
                ),
                **incident_fields,
            )
            self.db.add(incident)
            count += 1
        self.db.commit()
        return count

    def backfill_missing_locations(self) -> int:
        incidents = self.db.query(Incident).filter((Incident.latitude.is_(None)) | (Incident.longitude.is_(None))).all()
        updated = 0
        for inc in incidents:
            doc = self.db.query(SourceDocument).filter(SourceDocument.id == inc.document_id).first()
            text = " ".join(filter(None, [inc.location_name, doc.title if doc else None, doc.raw_text if doc else None]))
            location_name, lat, lon = infer_location_from_text(text)
            if lat is not None and lon is not None:
                inc.location_name = inc.location_name or location_name
                inc.latitude = lat
                inc.longitude = lon
                updated += 1
        self.db.commit()
        return updated

    def count_unextracted_documents(self) -> int:
        return (
            self.db.query(SourceDocument)
            .outerjoin(Incident, SourceDocument.id == Incident.document_id)
            .filter(Incident.id.is_(None))
            .count()
        )
