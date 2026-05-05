#!/bin/sh
# Render cron job: 매일 출력물 재생성 트리거.
# render.yaml 의 dockerCommand 가 이 스크립트를 호출한다.
set -u

if [ -z "${WEB_URL:-}" ]; then
  echo "[cron_refresh] WEB_URL is not set — abort" >&2
  exit 1
fi
if [ -z "${ADMIN_TOKEN:-}" ]; then
  echo "[cron_refresh] ADMIN_TOKEN is not set — abort" >&2
  exit 1
fi

echo "[cron_refresh] POST ${WEB_URL}/pipeline/refresh"
curl -fsS -X POST "${WEB_URL}/pipeline/refresh" \
  -H "X-Admin-Token: ${ADMIN_TOKEN}" \
  --max-time 120
status=$?
if [ $status -ne 0 ]; then
  echo "[cron_refresh] refresh call failed (curl exit=$status)" >&2
  exit $status
fi
echo "[cron_refresh] done"
