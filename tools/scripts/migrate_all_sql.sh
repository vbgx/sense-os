#!/usr/bin/env bash
set -euo pipefail

if [ "${ALLOW_LEGACY_SQL:-0}" != "1" ]; then
  echo "❌ Legacy SQL migrations are deprecated. Use tools/scripts/migrate.sh (Alembic)." >&2
  echo "Set ALLOW_LEGACY_SQL=1 to override." >&2
  exit 1
fi

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-sense}"

for f in tools/legacy_sql/infra_sql/*.sql; do
  echo "==> applying $f"
  cat "$f" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
done
