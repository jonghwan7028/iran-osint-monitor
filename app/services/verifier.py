from __future__ import annotations

import re
from app.models.entities import SourceDocument


class VerificationService:
    """OSINT 사건 검증 서비스 — 5단계 확정도 시스템.

    Confirmed / Likely / Claimed / Disputed / Retracted
    """

    CONFIRMATION_KEYWORDS = {
        "confirmed": ["confirmed", "verified", "official statement", "pentagon confirmed",
                       "idf confirmed", "ministry confirmed"],
        "disputed":  ["denied", "disputed", "rejected", "contradicted", "unconfirmed reports"],
        "retracted": ["retracted", "correction:", "false alarm", "earlier report was incorrect"],
        "claimed":   ["claimed", "alleged", "unverified", "sources say", "reportedly"],
    }

    KNOWN_LOCATIONS = [
        "Tehran", "Isfahan", "Tabriz", "Bandar Abbas", "Saudi Arabia",
        "Prince Sultan Air Base", "Baghdad", "Damascus", "Persian Gulf", "Red Sea",
        "Natanz", "Fordow", "Bushehr", "Kharg Island", "Strait of Hormuz",
        "Al Udeid", "Beirut", "Haifa", "Tel Aviv", "Erbil",
    ]

    def _count_evidence_factors(self, document: SourceDocument, incident_fields: dict) -> dict:
        """검증 근거 요소들을 수집하여 반환."""
        text = (document.raw_text or "")
        lowered = text.lower()
        factors = []

        # 출처 신뢰도
        reliability = document.source_reliability
        if reliability >= 0.7:
            factors.append("trusted_source")
        elif reliability >= 0.4:
            factors.append("moderate_source")

        # 텍스트 충실도
        if len(text) > 400:
            factors.append("detailed_report")

        # 위치 정보
        if incident_fields.get("location_name"):
            factors.append("location_identified")

        # 행위자 + 수단 식별
        if incident_fields.get("actor") and incident_fields.get("means"):
            factors.append("actor_means_identified")

        # 피해 정보
        if incident_fields.get("damage_summary"):
            factors.append("damage_reported")

        # 공식 확인 키워드
        if any(k in lowered for k in self.CONFIRMATION_KEYWORDS["confirmed"]):
            factors.append("official_confirmation")

        # 반박/분쟁 키워드
        has_dispute = any(k in lowered for k in self.CONFIRMATION_KEYWORDS["disputed"])
        if has_dispute:
            factors.append("counter_report_exists")

        # 철회 키워드
        has_retraction = any(k in lowered for k in self.CONFIRMATION_KEYWORDS["retracted"])
        if has_retraction:
            factors.append("retraction_detected")

        # 주장 수준 키워드
        has_claim = any(k in lowered for k in self.CONFIRMATION_KEYWORDS["claimed"])
        if has_claim:
            factors.append("claim_only")

        return {
            "factors": factors,
            "factor_count": len(factors),
            "has_dispute": has_dispute,
            "has_retraction": has_retraction,
            "has_claim": has_claim,
            "reliability": reliability,
        }

    def score(self, document: SourceDocument, incident_fields: dict) -> tuple[float, str]:
        evidence = self._count_evidence_factors(document, incident_fields)
        factors = evidence["factors"]

        # 기본 점수 = 출처 신뢰도
        score = evidence["reliability"]

        # 증거 요소별 가산
        if "detailed_report" in factors:
            score += 0.05
        if "location_identified" in factors:
            score += 0.08
        if "actor_means_identified" in factors:
            score += 0.08
        if "damage_reported" in factors:
            score += 0.05
        if "official_confirmation" in factors:
            score += 0.06

        # 감산 요소
        if "counter_report_exists" in factors:
            score -= 0.10
        if "retraction_detected" in factors:
            score -= 0.30

        score = max(0.05, min(score, 0.99))

        # 5단계 확정도 판정
        if evidence["has_retraction"]:
            status = "retracted"
        elif evidence["has_dispute"]:
            status = "disputed"
        elif score >= 0.8 and "official_confirmation" in factors:
            status = "confirmed"
        elif score >= 0.6:
            status = "likely"
        else:
            status = "claimed"

        return score, status

    def get_verification_detail(self, document: SourceDocument, incident_fields: dict) -> dict:
        """사건 카드에 표시할 검증 상세 정보 반환."""
        evidence = self._count_evidence_factors(document, incident_fields)
        score, status = self.score(document, incident_fields)
        return {
            "confidence": round(score, 2),
            "status": status,
            "factors": evidence["factors"],
            "factor_count": evidence["factor_count"],
            "source_reliability": round(evidence["reliability"], 2),
            "has_counter_report": evidence["has_dispute"],
            "has_retraction": evidence["has_retraction"],
        }
