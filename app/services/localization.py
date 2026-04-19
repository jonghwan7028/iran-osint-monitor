"""Localization — passthrough (v12e: 한글은 템플릿에서 직접 처리)."""
from __future__ import annotations
from typing import Any


def translate_text(text: str | None) -> str | None:
    return text


def translate_status(status: str | None) -> str | None:
    return status


def localize_incident_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return fields
