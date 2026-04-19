from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
STATUS_PATH = BASE_DIR / 'static' / 'report_status.json'
_LOCK = Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_status() -> dict[str, Any]:
    return {
        'state': 'idle',
        'step': '대기 중',
        'message': '파이프라인이 아직 실행되지 않았습니다.',
        'updated_at': _now(),
        'history': [],
        'last_result': None,
    }


def read_status() -> dict[str, Any]:
    with _LOCK:
        if not STATUS_PATH.exists():
            STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = _default_status()
            STATUS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return data
        try:
            return json.loads(STATUS_PATH.read_text(encoding='utf-8'))
        except Exception:
            data = _default_status()
            STATUS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return data


def write_status(data: dict[str, Any]) -> None:
    with _LOCK:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def update_status(*, state: str, step: str, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = read_status()
    history = list(data.get('history', []))
    history.append({
        'time': _now(),
        'state': state,
        'step': step,
        'message': message,
    })
    data.update({
        'state': state,
        'step': step,
        'message': message,
        'updated_at': _now(),
        'history': history[-50:],
    })
    if extra:
        data.update(extra)
    write_status(data)
    return data


def set_last_result(result: dict[str, Any]) -> dict[str, Any]:
    data = read_status()
    data['last_result'] = result
    data['updated_at'] = _now()
    write_status(data)
    return data
