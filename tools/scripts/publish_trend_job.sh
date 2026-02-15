#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
VERTICAL_ID="${VERTICAL_ID:-1}"
DAY="${DAY:-}"

# Default: today (host local), matches validate run day
if [ -z "${DAY}" ]; then
  DAY="$(date +%F)"
fi

payload="$(printf '{"type":"trend_job","day":"%s","vertical_id":%s,"cluster_version":"tfidf_v1","formula_version":"formula_v1"}' "$DAY" "$VERTICAL_ID")"

docker compose -f "${COMPOSE_FILE}" exec -T redis redis-cli LPUSH trend "${payload}" >/dev/null
echo "✅ trend job published (day=${DAY} vertical=${VERTICAL_ID})"
