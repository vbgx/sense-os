#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../scripts/_lib.sh"

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

step "🧪 Alembic drift check"

# Start Postgres only
step "=== boot postgres ==="
dc up -d postgres

# Wait for postgres health
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

# Run migrations via Alembic (docker)
COMPOSE_FILE="$COMPOSE_FILE" MODE=docker "$REPO_ROOT/tools/scripts/migrate.sh"

# Compare current vs head
head_rev="$(dc run --rm api-gateway bash -lc "alembic -c /app/packages/db/alembic.ini heads -q | awk 'NR==1{print \$1}'")"
current_rev="$(dc run --rm api-gateway bash -lc "alembic -c /app/packages/db/alembic.ini current -q | awk 'NR==1{print \$1}'")"

if [ -z "$head_rev" ] || [ -z "$current_rev" ]; then
  die "Failed to resolve Alembic head/current revisions"
fi

if [ "$head_rev" != "$current_rev" ]; then
  die "Alembic drift detected: head=$head_rev current=$current_rev"
fi

echo "✅ Alembic current == head ($head_rev)"
