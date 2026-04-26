"""
osint.db 의 incidents/source_documents 행을 seed_data.py 가 사용하는
딕셔너리 리터럴 형태로 출력한다.

용도:
- onrender 컨테이너에서 osint.db 를 다운받은 뒤, 새로 수집·분석된 사건 중
  교수님이 검증한 항목들만 골라 시드 데이터에 박제할 때 사용.

사용법:
    python tools/db_to_seed.py path/to/osint.db --since 2026-04-25
    python tools/db_to_seed.py path/to/osint.db --ids 35,36,37
    python tools/db_to_seed.py path/to/osint.db --min-id 34

옵션을 안 주면 전체 사건을 출력한다.

출력은 stdout — 검토 후 직접 seed_data.py 의 VERIFIED_EVENTS 리스트에
복사해 넣으면 된다. 자동 추출은 부정확한 항목(엉뚱한 actor/location 등)이
섞여있을 수 있으므로 항상 사람이 한 번 검토한 뒤 넣는 것을 전제로 한다.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def fmt_dt(s: str) -> str:
    """SQLite ISO datetime → datetime(...) 호출 코드."""
    if not s:
        return "None"
    # SQLite stores as "2026-04-25 21:00:00.000000"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return f"# UNPARSED: {s!r}"
    return (
        f"datetime({dt.year}, {dt.month}, {dt.day}, "
        f"{dt.hour}, {dt.minute}, tzinfo=timezone.utc)"
    )


def py_repr(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    return repr(value)


def actor_side(actor: str) -> str:
    a = (actor or "").lower()
    if any(k in a for k in ["iran", "hezbollah", "houthi", "irgc", "proxy"]):
        return "iran"
    if any(k in a for k in ["united states", "us ", "israel", "idf", "centcom"]):
        return "us_israel"
    return "other"


def emit_event(row: sqlite3.Row) -> str:
    raw_text = row["raw_text"] or ""
    if len(raw_text) > 1500:
        raw_text = raw_text[:1500] + " [...]"
    out: list[str] = []
    out.append("    {")
    out.append(f"        # incident.id = {row['incident_id']} | doc.id = {row['document_id']}")
    out.append(f"        \"title\": {py_repr(row['title'])},")
    out.append(f"        \"url\": {py_repr(row['url'])},")
    out.append(f"        \"publisher\": {py_repr(row['publisher'])},")
    out.append(f"        \"published_at\": {fmt_dt(row['published_at'])},")
    out.append(f"        \"raw_text\": {py_repr(raw_text)},")
    out.append(f"        \"source_reliability\": {py_repr(row['source_reliability'])},")
    out.append("        \"incident\": {")
    out.append(f"            \"event_type\": {py_repr(row['event_type'])},")
    out.append(f"            \"actor\": {py_repr(row['actor'])},")
    out.append(f"            \"target_actor\": {py_repr(row['target_actor'])},")
    out.append(f"            \"location_name\": {py_repr(row['location_name'])},")
    out.append(f"            \"latitude\": {py_repr(row['latitude'])},")
    out.append(f"            \"longitude\": {py_repr(row['longitude'])},")
    out.append(f"            \"means\": {py_repr(row['means'])},")
    out.append(f"            \"target_type\": {py_repr(row['target_type'])},")
    out.append(f"            \"damage_summary\": {py_repr(row['damage_summary'])},")
    out.append(f"            \"tactical_assessment\": {py_repr(row['tactical_assessment'])},")
    out.append(f"            \"strategic_assessment\": {py_repr(row['strategic_assessment'])},")
    out.append(f"            \"confidence\": {py_repr(round(row['confidence'] or 0.0, 3))},")
    out.append(f"            \"verified_status\": {py_repr(row['verified_status'])},")
    out.append(f"            \"is_high_impact\": {py_repr(bool(row['is_high_impact']))},")
    out.append(f"            \"actor_side\": {py_repr(actor_side(row['actor']))},")
    out.append("        },")
    out.append("    },")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db", help="SQLite DB 파일 경로 (osint.db)")
    ap.add_argument("--ids", help="콤마 구분 incident.id 목록 (예: 35,36,37)")
    ap.add_argument("--min-id", type=int, help="이 id 이상만 출력")
    ap.add_argument("--since", help="이 published_at 이상만 (YYYY-MM-DD)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] DB not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT i.id AS incident_id, i.document_id,
               d.title, d.url, d.publisher, d.published_at,
               d.raw_text, d.source_reliability,
               i.event_type, i.actor, i.target_actor, i.location_name,
               i.latitude, i.longitude, i.means, i.target_type,
               i.damage_summary, i.tactical_assessment, i.strategic_assessment,
               i.confidence, i.verified_status, i.is_high_impact
        FROM incidents i
        LEFT JOIN source_documents d ON i.document_id = d.id
        WHERE 1=1
    """
    params: list = []
    if args.ids:
        ids = [int(s.strip()) for s in args.ids.split(",") if s.strip()]
        sql += f" AND i.id IN ({','.join('?' * len(ids))})"
        params.extend(ids)
    if args.min_id is not None:
        sql += " AND i.id >= ?"
        params.append(args.min_id)
    if args.since:
        sql += " AND date(d.published_at) >= ?"
        params.append(args.since)
    sql += " ORDER BY d.published_at, i.id"

    rows = conn.execute(sql, params).fetchall()
    if not rows:
        print("# No matching events.", file=sys.stderr)
        sys.exit(0)

    print(f"# === {len(rows)} events from {db_path.name} ===")
    print("# Review carefully and only paste verified entries into")
    print("# app/services/seed_data.py VERIFIED_EVENTS list.")
    print("# Don't forget to add Korean translations to ko_sentences.SENTENCE_KO")
    print("# for the damage_summary / tactical / strategic fields.")
    print()
    for row in rows:
        print(emit_event(row))
        print()

    conn.close()


if __name__ == "__main__":
    main()
