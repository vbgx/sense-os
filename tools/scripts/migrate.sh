#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

MODE="${MODE:-auto}" # auto | docker | local
ALEMBIC_BIN="${ALEMBIC_BIN:-alembic}"
ALEMBIC_INI="${ALEMBIC_INI:-$REPO_ROOT/packages/db/alembic.ini}"

run_local() {
  step "🗄️  Alembic migrate (local)"
  (cd "$REPO_ROOT" && "$ALEMBIC_BIN" -c "$ALEMBIC_INI" upgrade head)
}

run_docker() {
  step "🗄️  Alembic migrate (docker)"
  if dc ps -q api-gateway >/dev/null 2>&1 && [ -n "$(dc ps -q api-gateway)" ]; then
    dc_exec api-gateway bash -lc "alembic -c /app/packages/db/alembic.ini upgrade head"
  else
    dc run --rm api-gateway bash -lc "alembic -c /app/packages/db/alembic.ini upgrade head"
  fi
}

if [ "$MODE" = "local" ]; then
  run_local
  exit 0
fi

if [ "$MODE" = "docker" ]; then
  run_docker
  exit 0
fi

# auto: prefer docker if api-gateway container exists, else local
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  run_docker
else
  run_local
fi
