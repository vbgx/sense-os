#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VERTICAL_ID="${VERTICAL_ID:-1}"
SOURCE="${SOURCE:-reddit}"
QUERY="${QUERY:-saas}"
LIMIT="${LIMIT:-50}"

step "⏱️  Scheduler once (vertical=$VERTICAL_ID source=$SOURCE query=$QUERY limit=$LIMIT)"

dc_exec api-gateway env \
  PYTHONPATH=/app/services/scheduler/src:/app/packages/db/src:/app/packages/queue/src \
  python -m scheduler.main \
    --mode once \
    --vertical-id "$VERTICAL_ID" \
    --source "$SOURCE" \
    --query "$QUERY" \
    --limit "$LIMIT"

echo "✅ Scheduler done"
