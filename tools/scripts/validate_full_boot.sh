#!/usr/bin/env bash
set -euo pipefail

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOGFILE_DEFAULT="sense_full_boot_$(date +%Y%m%d_%H%M%S).log"
LOGFILE="${LOGFILE:-$LOGFILE_DEFAULT}"

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
HEALTH_PATH="${HEALTH_PATH:-/health}"

DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://$(whoami)@localhost:5432/sense}"
POSTGRES_DSN="${POSTGRES_DSN:-$DATABASE_URL}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

export DATABASE_URL POSTGRES_DSN REDIS_URL LOG_LEVEL

# default: keep running (matches your on.sh expectation)
KEEP_RUNNING=1
SKIP_SEED=0
SKIP_SCHEDULER=0

usage() {
  cat <<USAGE
Usage: $0 [options]
  --skip-seed
  --skip-scheduler
  --keep-running       (explicit; default)
  --no-keep-running    (stop processes at end)
  --logfile <path>
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-seed) SKIP_SEED=1; shift ;;
    --skip-scheduler) SKIP_SCHEDULER=1; shift ;;
    --keep-running) KEEP_RUNNING=1; shift ;;          # ✅ added
    --no-keep-running) KEEP_RUNNING=0; shift ;;
    --logfile)
      LOGFILE="${2:-}"
      [ -n "$LOGFILE" ] || { echo "ERROR: --logfile requires a path" >&2; exit 1; }
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

step(){ echo; echo "==> $*"; }
die(){ echo "❌ $*" >&2; exit 1; }

PID_INGEST=""; PID_PROCESS=""; PID_CLUSTER=""; PID_TREND=""

cleanup() {
  if [ "$KEEP_RUNNING" -eq 1 ]; then
    echo; echo "🧷 keep-running (processes left up)"
    return 0
  fi
  echo; echo "🧹 stopping workers..."
  for p in "$PID_TREND" "$PID_CLUSTER" "$PID_PROCESS" "$PID_INGEST"; do
    [ -n "${p}" ] && kill "$p" >/dev/null 2>&1 || true
  done
}

on_failure() {
  local code=$?
  echo; echo "==============================================="
  echo "❌ VALIDATION FAILED (exit=$code)"
  echo "==============================================="
  cleanup || true
  echo; echo "📝 Log written to: $LOGFILE"
  exit "$code"
}

trap on_failure ERR
trap 'cleanup; exit 0' INT

{
  echo "==============================================="
  echo "🧪 SENSE OS FULL STACK VALIDATION (LOCAL)"
  echo "🗓️  DATE: $(date)"
  echo "📁 REPO_ROOT: $REPO_ROOT"
  echo "🌐 API_BASE_URL: $API_BASE_URL"
  echo "🗄️  DATABASE_URL: $DATABASE_URL"
  echo "🧰 REDIS_URL: $REDIS_URL"
  echo "==============================================="

  step "0) Check Postgres"
  PSQL_DSN="$(printf "%s" "$DATABASE_URL" | sed 's/^postgresql+psycopg:\/\//postgresql:\/\//')"
  echo "DEBUG Using PSQL_DSN=$PSQL_DSN"
  psql "$PSQL_DSN" -c 'select 1;' >/dev/null || die "Cannot connect to Postgres ($PSQL_DSN)"
  echo "✅ Postgres OK"

  step "1) Check Redis"
  redis-cli ping >/dev/null || die "Cannot connect to Redis (localhost:6379)"
  echo "✅ Redis OK"

  step "2) Activate venv"
  [ -d "$REPO_ROOT/.venv" ] || die ".venv not found at repo root"
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
  echo "✅ venv OK ($(python --version))"

  step "3) Migrate"
  (cd "$REPO_ROOT" && make migrate)

  if [ "$SKIP_SEED" -eq 0 ]; then
    step "4) Seed"
    (cd "$REPO_ROOT" && make seed)
  else
    step "4) Seed (skipped)"
  fi

  step "5) Start workers"
  python "$REPO_ROOT/services/ingestion_worker/src/ingestion_worker/main.py" & PID_INGEST=$!
  python "$REPO_ROOT/services/processing_worker/src/processing_worker/main.py" & PID_PROCESS=$!
  python "$REPO_ROOT/services/clustering_worker/src/clustering_worker/main.py" & PID_CLUSTER=$!
  python "$REPO_ROOT/services/trend_worker/src/trend_worker/main.py" & PID_TREND=$!
  echo "✅ Workers started (ingest=$PID_INGEST process=$PID_PROCESS cluster=$PID_CLUSTER trend=$PID_TREND)"

  if [ "$SKIP_SCHEDULER" -eq 0 ]; then
    step "6) Scheduler once"
    (cd "$REPO_ROOT" && make scheduler)
  else
    step "6) Scheduler (skipped)"
  fi

  step "7) Wait 10s"
  sleep 10

  step "8) DB counts"
  psql "$PSQL_DSN" -c "select count(*) as signals from signals; select count(*) as pain_instances from pain_instances;" || true

  echo
  echo "==============================================="
  echo "✅ VALIDATION FINISHED"
  echo "==============================================="

  cleanup

} 2>&1 | tee "$LOGFILE"

echo; echo "📝 Log written to: $LOGFILE"
