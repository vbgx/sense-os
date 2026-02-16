#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../scripts/_lib.sh"

step "🧪 Double-consume idempotency check"

step "=== boot postgres ==="
dc up -d postgres

cid="$(dc ps -q postgres)"
if [ -z "$cid" ]; then
  die "Could not resolve postgres container id"
fi

for i in {1..90}; do
  status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$cid" 2>/dev/null || echo "missing")"
  if [ "$status" = "healthy" ] || [ "$status" = "no-healthcheck" ]; then
    echo "✅ postgres OK (status=$status)"
    break
  fi
  sleep 1
  if [ "$i" -eq 90 ]; then
    die "postgres not healthy after 90s (status=$status)"
  fi
done

COMPOSE_FILE="$COMPOSE_FILE" MODE=docker "$REPO_ROOT/tools/scripts/migrate.sh"

dc run --rm processing-worker bash -lc "python /app/tools/ci/check_double_consume.py"
