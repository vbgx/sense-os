#!/usr/bin/env bash
set -euo pipefail

{ set +H 2>/dev/null || true; } >/dev/null 2>&1
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

run_sql() {
  local path="$1"
  [ -f "$path" ] || return 0
  cat "$path" | docker compose -f "$COMPOSE_FILE" exec -T postgres \
    psql -U postgres -d postgres
}

run_sql infra/sql/001_init_schema.sql
run_sql infra/sql/002_indexes.sql
run_sql infra/sql/003_trends_patch.sql
