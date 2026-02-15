#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VERTICAL_ID="${VERTICAL_ID:-1}"
SOURCE="${SOURCE:-reddit}"
QUERY="${QUERY:-saas}"
LIMIT="${LIMIT:-}"
DAYS="${DAYS:-90}"
START="${START:-}"
END="${END:-}"
SERIES="${SERIES:-1}"

step "⏱️  Scheduler backfill (vertical=$VERTICAL_ID source=$SOURCE days=$DAYS series=$SERIES)"

args=(
  --mode backfill
  --vertical-id "$VERTICAL_ID"
  --source "$SOURCE"
)

if [ -n "$QUERY" ]; then
  args+=(--query "$QUERY")
fi
if [ -n "$LIMIT" ]; then
  args+=(--limit "$LIMIT")
fi
if [ -n "$START" ]; then
  args+=(--start "$START")
fi
if [ -n "$END" ]; then
  args+=(--end "$END")
fi
if [ -n "$DAYS" ]; then
  args+=(--days "$DAYS")
fi
if [ "$SERIES" = "0" ]; then
  args+=(--no-series)
fi

# Run inside api-gateway container for access to db/redis
# shellcheck disable=SC2086

dc_exec api-gateway env \
  PYTHONPATH=/app/services/scheduler/src:/app/packages/db/src:/app/packages/queue/src \
  python -m scheduler.main \
  "${args[@]}"

echo "✅ Backfill scheduler done"
