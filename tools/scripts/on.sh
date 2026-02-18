#!/usr/bin/env bash
set -euo pipefail

echo
echo "🚀 SENSE-OS — LIVE MODE"
echo

# Default to repo-root docker-compose.yml, but allow override
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "❌ compose file not found: $COMPOSE_FILE"
  echo "   Tip: set COMPOSE_FILE=/path/to/docker-compose.yml"
  exit 1
fi

echo "▶ Docker up... (compose: $COMPOSE_FILE)"
docker compose -f "$COMPOSE_FILE" up -d --build

echo
echo "✅ Docker is up."
echo

echo "▶ Logs (ctrl+c to stop)..."
docker compose -f "$COMPOSE_FILE" logs -f \
  api-gateway \
  ingestion-worker \
  processing-worker \
  clustering-worker \
  trend-worker
