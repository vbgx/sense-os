#!/usr/bin/env bash
set -euo pipefail

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Optional label for logs
LABEL="${1:-manual}"

# Try to use shared helpers if available
if [ -f "$SCRIPT_DIR/_lib.sh" ]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/_lib.sh"
fi

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

queues=("ingest" "process" "cluster" "trend")

echo "📦 QUEUES (${LABEL})"
echo "---- redis queues snapshot ----"

# Prefer dc_exec from _lib.sh (if defined), else fallback.
if command -v dc_exec >/dev/null 2>&1; then
  # Ensure redis service is running
  if ! dc ps --services 2>/dev/null | grep -q '^redis$'; then
    echo 'service "redis" not found in compose config' >&2
    exit 1
  fi
  if ! dc ps redis 2>/dev/null | grep -q 'Up'; then
    echo 'service "redis" is not running' >&2
    exit 1
  fi

  for q in "${queues[@]}"; do
    len="$(dc_exec redis redis-cli LLEN "$q" | tr -d '\r' | tail -n 1)"
    len="${len:-0}"
    echo "queue=${q} len=${len}"
  done
else
  # Fallback (no _lib.sh)
  if ! docker compose -f "$COMPOSE_FILE" ps redis 2>/dev/null | grep -q 'Up'; then
    echo 'service "redis" is not running' >&2
    exit 1
  fi

  for q in "${queues[@]}"; do
    len="$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli LLEN "$q" | tr -d '\r' | tail -n 1)"
    len="${len:-0}"
    echo "queue=${q} len=${len}"
  done
fi

echo "--------------------------------"
