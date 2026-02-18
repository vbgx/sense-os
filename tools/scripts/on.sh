#!/usr/bin/env bash
set -euo pipefail
{ set +H 2>/dev/null || true; } >/dev/null 2>&1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# ---- Configuration (override via env) ----
export COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export HEALTH_PATH="${HEALTH_PATH:-/health}"

# if you want faster runs locally
export POSTGRES_WAIT_S="${POSTGRES_WAIT_S:-120}"
export API_WAIT_S="${API_WAIT_S:-120}"
export LOG_WAIT_S="${LOG_WAIT_S:-60}"
export SCHEDULER_RETRIES="${SCHEDULER_RETRIES:-2}"
export VERTICAL_ID="${VERTICAL_ID:-1}"

# keep your ingestion behavior
export INGEST_FAIL_FAST="${INGEST_FAIL_FAST:-0}"
export INGEST_FANOUT_MAX_WORKERS="${INGEST_FANOUT_MAX_WORKERS:-8}"
export INGEST_MAX_SIGNALS_PER_SOURCE="${INGEST_MAX_SIGNALS_PER_SOURCE:-200}"

VALIDATOR="${VALIDATOR:-tools/scripts/validate_full_boot.sh}"

echo ""
echo "=============================="
echo "  SENSE-OS — BUTTON ON"
echo "=============================="
echo ""
echo "ROOT=$ROOT"
echo "COMPOSE_FILE=$COMPOSE_FILE"
echo "VALIDATOR=$VALIDATOR"
echo ""

# ---- Preconditions ----
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "✖ compose file not found at: $COMPOSE_FILE"
  echo ""
  echo "Locate candidates:"
  echo "  find . -maxdepth 6 \\( -name 'docker-compose.yml' -o -name 'compose.yml' -o -name 'docker-compose.yaml' -o -name 'compose.yaml' \\) -print"
  echo ""
  echo "Then run:"
  echo "  COMPOSE_FILE=./path/to/docker-compose.yml ./tools/scripts/on.sh"
  exit 2
fi

if [ ! -f "$VALIDATOR" ]; then
  echo "✖ validator script not found at: $VALIDATOR"
  echo ""
  echo "Put your big full-boot script at that path, or run:"
  echo "  VALIDATOR=./path/to/your_script.sh ./tools/scripts/on.sh"
  exit 2
fi

chmod +x "$VALIDATOR" >/dev/null 2>&1 || true

# ---- Run ----
# By default: clean boot + build + seed + scheduler + trends checks + down
# You can override via extra args:
#   ./tools/scripts/on.sh --no-build --keep-running
exec bash "$VALIDATOR" "$@"
