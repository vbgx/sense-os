#!/usr/bin/env bash
set -euo pipefail

# Repo root = 2 niveaux au-dessus de tools/scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
COMPOSE_PATH="$REPO_ROOT/$COMPOSE_FILE"

# Local defaults for worker scripts (can be overridden by env)
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export REDIS_DSN="${REDIS_DSN:-$REDIS_URL}"
export POSTGRES_DSN="${POSTGRES_DSN:-postgresql+psycopg://postgres:postgres@localhost:5432/sense}"

die()  { printf '❌ %s\n' "$*" >&2; exit 1; }
step() { printf '\n%s\n' "$*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

dc() {
  require_cmd docker
  docker compose -f "$COMPOSE_PATH" "$@"
}

dc_exec() {
  local svc="$1"; shift
  dc exec -T "$svc" "$@"
}

dc_logs() {
  local svc="$1"; shift
  dc logs --no-color "$svc" "$@"
}

relpath() {
  # print path relative to repo root
  local abs="$1"
  echo "${abs#"$REPO_ROOT"/}"
}
