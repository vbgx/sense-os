#!/usr/bin/env bash
set -euo pipefail

echo
echo "🚀 SENSE-OS — LIVE MODE (LOCAL)"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Local defaults (override if you want)
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://$(whoami)@localhost:5432/sense}"
export POSTGRES_DSN="${POSTGRES_DSN:-$DATABASE_URL}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "==============================================="
echo "🧪 SENSE OS FULL STACK VALIDATION (LOCAL)"
echo "🗓️  DATE: $(date)"
echo "📁 REPO_ROOT: $REPO_ROOT"
echo "🌐 API_BASE_URL: $API_BASE_URL"
echo "🗄️  DATABASE_URL: $DATABASE_URL"
echo "🧰 REDIS_URL: $REDIS_URL"
echo "==============================================="
echo

exec "$REPO_ROOT/tools/scripts/validate_full_boot.sh" --keep-running
