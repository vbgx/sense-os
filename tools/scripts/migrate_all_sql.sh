#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

for f in infra/sql/*.sql; do
  echo "==> applying $f"
  cat "$f" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U postgres -d postgres
done
