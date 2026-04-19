from __future__ import annotations

from app.models.entities import SourceDocument


class VerificationService:
    KNOWN_LOCATIONS = [
        "Tehran",
        "Isfahan",
        "Tabriz",
        "Bandar Abbas",
        "Saudi Arabia",
        "Prince Sultan Air Base",
        "Baghdad",
        "Damascus",
        "Persian Gulf",
        "Red Sea",
    ]

    def score(self, document: SourceDocument, incident_fields: dict) -> tuple[float, str]:
        score = document.source_reliability

        text = (document.raw_text or "")
        if len(text) > 400:
            score += 0.05
        if incident_fields.get("location_name"):
            score += 0.08
        if incident_fields.get("actor") and incident_fields.get("means"):
            score += 0.08
        if incident_fields.get("damage_summary"):
            score += 0.05
        if any(k.lower() in text.lower() for k in ["official", "confirmed", "according to", "reported"]):
            score += 0.04

        score = max(0.05, min(score, 0.99))

        if score >= 0.8:
            status = "verified"
        elif score >= 0.6:
            status = "partially_verified"
        elif score >= 0.4:
            status = "unverified"
        else:
            status = "likely_propaganda"
        return score, status
