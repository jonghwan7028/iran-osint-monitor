#!/usr/bin/env python3
"""로컬 SQLite DB → JSON 덤프.

사용:
    python3 scripts/export_local_db.py
    # → db_export.json 생성

산출물(JSON 구조):
    {
      "schema_version": 1,
      "exported_at": "2026-05-05T12:34:56Z",
      "documents": [
        {
          "title": "...",
          "url": "...",
          "publisher": "...",
          "published_at": "2026-04-30T08:15:00",   # ISO, naive-utc 가정
          "language": "en",
          "query_used": "...",
          "raw_text": "...",
          "content_hash": "...",
          "event_signature": "...",                 # 없을 수 있음
          "source_reliability": 0.9,
          "ingestion_time": "...",
          "incidents": [                             # 이 문서에서 추출된 사건들
            {
              "event_type": "...", "actor": "...", "target_actor": "...",
              "location_name": "...", "latitude": 32.07, "longitude": 34.78,
              "means": "...", "target_type": "...",
              "damage_summary": "...", "tactical_assessment": "...", "strategic_assessment": "...",
              "confidence": 0.85, "verified_status": "confirmed", "is_high_impact": true,
              "created_at": "..."
            }
          ]
        }
      ]
    }

이 JSON을 Render의 /admin/import 로 그대로 POST 하면 dedup 통과한 항목만 INSERT 됩니다.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_PATH = REPO / "app" / "data" / "osint.db"
OUT_PATH = REPO / "db_export.json"


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


def main() -> int:
    if not DB_PATH.exists():
        print(f"❌ SQLite DB 파일 없음: {DB_PATH}", file=sys.stderr)
        return 1

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    # 컬럼 존재 여부 확인 (event_signature 가 없는 구버전 DB 호환)
    doc_cols = {r["name"] for r in con.execute("PRAGMA table_info(source_documents)")}
    inc_cols = {r["name"] for r in con.execute("PRAGMA table_info(incidents)")}
    has_event_sig = "event_signature" in doc_cols

    # 문서별 사건 묶음 만들기
    incidents_by_doc: dict[int, list[dict]] = {}
    for row in con.execute("SELECT * FROM incidents"):
        d = _row_to_dict(row)
        doc_id = d.pop("document_id")
        # local id 는 import 쪽에서 새로 부여됨
        d.pop("id", None)
        incidents_by_doc.setdefault(doc_id, []).append(d)

    documents: list[dict] = []
    for row in con.execute("SELECT * FROM source_documents"):
        d = _row_to_dict(row)
        local_id = d.pop("id")
        if not has_event_sig:
            d["event_signature"] = None
        d["incidents"] = incidents_by_doc.get(local_id, [])
        documents.append(d)

    bundle = {
        "schema_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "documents": documents,
    }

    OUT_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    inc_total = sum(len(d["incidents"]) for d in documents)
    print(f"✅ Exported {len(documents)} documents, {inc_total} incidents")
    print(f"   → {OUT_PATH}")
    print(f"   ({OUT_PATH.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
