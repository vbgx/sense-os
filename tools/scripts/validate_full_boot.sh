#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Sense OS Full Stack Validation
#
# Purpose:
#   Boot the full stack (Postgres, Redis, API, workers), run migrations + seed,
#   execute the scheduler, verify ingestion/processing/clustering/trending, and
#   confirm API trend endpoints respond successfully.
#
# Usage:
#   ./tools/scripts/validate_full_boot.sh [options]
#
# Options:
#   --no-down         Do not run 'docker compose down -v' (keeps volumes)
#   --no-build        Do not rebuild images on 'up'
#   --skip-seed       Skip 'make seed'
#   --skip-scheduler  Skip 'make scheduler'
#   --skip-trends     Skip /trending, /emerging, /declining endpoint checks
#   --keep-running    Do not shut down services on success
#   --logfile <path>  Write output to this logfile
#
# Env (optional):
#   COMPOSE_FILE      Path to compose file (default: infra/docker/docker-compose.yml)
#   API_BASE_URL      Base URL for API (default: http://localhost:8000)
#   HEALTH_PATH       Health path (default: /health)
#   POSTGRES_WAIT_S   Postgres health wait seconds (default: 90)
#   API_WAIT_S        API health wait seconds (default: 90)
#   LOG_WAIT_S        Log match wait seconds (default: 45)
#   SCHEDULER_RETRIES Scheduler run attempts (default: 2)
#   VERTICAL_ID       Vertical id for trend endpoints (default: 1)
# -----------------------------------------------------------------------------

# disable history expansion (macOS bash/zsh oddities)
{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Shared helpers (dc, dc_exec, die, step, etc.)
source "$SCRIPT_DIR/_lib.sh"

# -------------------------------
# Defaults / Options
# -------------------------------
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"  # honored by _lib.sh too
LOGFILE_DEFAULT="sense_full_boot_$(date +%Y%m%d_%H%M%S).log"

NO_DOWN=0
NO_BUILD=0
SKIP_SEED=0
SKIP_SCHEDULER=0
SKIP_TRENDS=0
KEEP_RUNNING=0

LOGFILE="${LOGFILE:-$LOGFILE_DEFAULT}"

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
HEALTH_PATH="${HEALTH_PATH:-/health}"

POSTGRES_WAIT_S="${POSTGRES_WAIT_S:-90}"
API_WAIT_S="${API_WAIT_S:-90}"
LOG_WAIT_S="${LOG_WAIT_S:-45}"
SCHEDULER_RETRIES="${SCHEDULER_RETRIES:-2}"

VERTICAL_ID="${VERTICAL_ID:-1}"

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --no-down           Do not run 'docker compose down -v' (keeps volumes)
  --no-build          Do not rebuild images on 'up'
  --skip-seed         Skip 'make seed'
  --skip-scheduler    Skip 'make scheduler'
  --skip-trends       Skip /trending, /emerging, /declining endpoint checks
  --keep-running      Do not shut down services on success
  --logfile <path>    Write output to this logfile (default: $LOGFILE_DEFAULT)

Env (optional):
  COMPOSE_FILE        Path to compose file (default: infra/docker/docker-compose.yml)
  API_BASE_URL        Base URL for API (default: http://localhost:8000)
  HEALTH_PATH         Health path (default: /health)
  POSTGRES_WAIT_S     Postgres health wait seconds (default: 90)
  API_WAIT_S          API health wait seconds (default: 90)
  LOG_WAIT_S          Log match wait seconds (default: 45)
  SCHEDULER_RETRIES   Scheduler run attempts (default: 2)
  VERTICAL_ID         Vertical id for trend endpoints (default: 1)

Examples:
  $0
  $0 --no-down --no-build
  SKIP_SEED=1 $0
  API_BASE_URL=http://localhost:8000 $0 --logfile /tmp/boot.log
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --no-down)        NO_DOWN=1; shift ;;
    --no-build)       NO_BUILD=1; shift ;;
    --skip-seed)      SKIP_SEED=1; shift ;;
    --skip-scheduler) SKIP_SCHEDULER=1; shift ;;
    --skip-trends)    SKIP_TRENDS=1; shift ;;
    --keep-running)   KEEP_RUNNING=1; shift ;;
    --logfile)
      LOGFILE="${2:-}"
      [ -n "$LOGFILE" ] || die "--logfile requires a path"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1 (use --help)" ;;
  esac
done

# -------------------------------
# Helpers
# -------------------------------
svc_logs() {
  local svc="$1"
  local tail="${2:-200}"
  dc logs --no-color --tail="$tail" "$svc" 2>/dev/null || true
}

wait_http_ok() {
  local url="$1"
  local seconds="${2:-90}"
  local i=1
  while [ "$i" -le "$seconds" ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

wait_log_match() {
  local svc="$1"
  local regex="$2"
  local seconds="${3:-45}"
  local i=1
  while [ "$i" -le "$seconds" ]; do
    if svc_logs "$svc" 800 | grep -E "$regex" >/dev/null 2>&1; then return 0; fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

wait_service_healthy() {
  local svc="$1"
  local seconds="$2"
  local cid
  local i=1
  local status="unknown"

  cid="$(dc ps -q "$svc")"
  [ -n "$cid" ] || die "Could not resolve $svc container id"

  while [ "$i" -le "$seconds" ]; do
    status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$cid" 2>/dev/null || echo "missing")"
    if [ "$status" = "healthy" ] || [ "$status" = "no-healthcheck" ]; then
      echo "✅ $svc OK (status=$status)"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  die "$svc not healthy after ${seconds}s (status=$status)"
}

extract_last_int_from_text() {
  # Reads stdin; extracts last capture group 1 from regex
  local re="$1"
  local out
  out="$(sed -nE "s/.*${re}.*/\\1/p" | tail -n 1 || true)"
  [ -n "${out}" ] || return 1
  printf '%s' "${out}"
}

queues_snapshot() {
  local label="$1"
  if [ -x "$REPO_ROOT/tools/scripts/redis_queues_snapshot.sh" ]; then
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" "$REPO_ROOT/tools/scripts/redis_queues_snapshot.sh" "$label")
  else
    echo "⚠️  Missing tools/scripts/redis_queues_snapshot.sh (skipping queues snapshot)"
  fi
}

print_debug_context() {
  echo
  echo "------------------------------"
  echo "🧯 DEBUG CONTEXT"
  echo "------------------------------"
  echo "--- docker compose ps ---"
  dc ps || true
  echo
  echo "--- docker compose config (first lines) ---"
  dc config 2>/dev/null | head -n 120 || true
  echo
}

run_with_retry() {
  local attempts="$1"
  shift
  local i=1
  while [ "$i" -le "$attempts" ]; do
    if "$@"; then
      return 0
    fi
    echo "⚠️  Attempt $i/$attempts failed: $*"
    i=$((i + 1))
    sleep 3
  done
  return 1
}

on_failure() {
  local code=$?
  echo
  echo "==============================================="
  echo "❌ VALIDATION FAILED (exit=$code)"
  echo "==============================================="
  print_debug_context

  echo
  echo "--- logs: api-gateway ---"
  svc_logs api-gateway 300
  echo
  echo "--- logs: postgres ---"
  svc_logs postgres 300
  echo
  echo "--- logs: redis ---"
  svc_logs redis 200
  echo
  echo "--- logs: ingestion-worker ---"
  svc_logs ingestion-worker 350
  echo
  echo "--- logs: processing-worker ---"
  svc_logs processing-worker 350
  echo
  echo "--- logs: clustering-worker ---"
  svc_logs clustering-worker 350
  echo
  echo "--- logs: trend-worker ---"
  svc_logs trend-worker 350

  echo
  echo "📝 Log written to: $LOGFILE"
  exit "$code"
}

trap on_failure ERR

# -------------------------------
# Main (tee everything)
# -------------------------------
{
  echo "==============================================="
  echo "🧪 SENSE OS FULL STACK VALIDATION"
  echo "🗓️  DATE: $(date)"
  echo "📁 REPO_ROOT: $REPO_ROOT"
  echo "📁 PWD:  $(pwd)"
  echo "🐳 COMPOSE_FILE: $COMPOSE_FILE"
  echo "🌐 API_BASE_URL: $API_BASE_URL"
  echo "==============================================="
  echo

  step "=== 0️⃣  COMPOSE CONFIG (must succeed) ==="
  dc config >/dev/null
  echo "✅ OK"

  step "=== 1️⃣  TREE SNAPSHOT ==="
  if command -v tree >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && tree -a -I "__pycache__|*.pyc|.git|.venv|dist|build|.pytest_cache|.mypy_cache|node_modules")
  else
    echo "⚠️  tree not installed; showing repo root listing:"
    (cd "$REPO_ROOT" && ls -la)
  fi

  if [ "$NO_DOWN" -eq 0 ]; then
    step "=== 2️⃣  DOCKER DOWN (clean volumes) ==="
    dc down -v
  else
    step "=== 2️⃣  DOCKER DOWN (skipped) ==="
    echo "ℹ️  --no-down set"
  fi

  step "=== 3️⃣  BOOT CORE SERVICES (postgres + redis) ==="
  dc up -d postgres redis

  step "=== 4️⃣  WAIT FOR POSTGRES HEALTH (up to ${POSTGRES_WAIT_S}s) ==="
  wait_service_healthy postgres "$POSTGRES_WAIT_S"

  step "=== 4️⃣b WAIT FOR REDIS HEALTH (up to ${POSTGRES_WAIT_S}s) ==="
  wait_service_healthy redis "$POSTGRES_WAIT_S"

  step "=== 5️⃣  MIGRATE DB (via migrate_sql.sh) ==="
  COMPOSE_FILE="$COMPOSE_FILE" "$SCRIPT_DIR/migrate_sql.sh"

  step "=== 6️⃣  BOOT APP SERVICES (api + workers) ==="
  if [ "$NO_BUILD" -eq 1 ]; then
    echo "ℹ️  --no-build set"
    dc up -d
  else
    dc up --build -d
  fi

  step "=== 7️⃣  HEALTH CHECK API (up to ${API_WAIT_S}s) ==="
  HEALTH_URL="${API_BASE_URL}${HEALTH_PATH}"
  if ! wait_http_ok "$HEALTH_URL" "$API_WAIT_S"; then
    svc_logs api-gateway 250
    die "Health check failed after ${API_WAIT_S}s ($HEALTH_URL)"
  fi
  echo "✅ API healthy:"
  curl -fsS "$HEALTH_URL" || true
  echo

  if [ "$SKIP_SEED" -eq 0 ]; then
    step "=== 8️⃣  SEED (make seed) ==="
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make seed)
  else
    step "=== 8️⃣  SEED (skipped) ==="
    echo "ℹ️  --skip-seed set"
  fi

  # -------------------------------
  # Scheduler + queues snapshots
  # -------------------------------
  queues_snapshot "before scheduler"

  if [ "$SKIP_SCHEDULER" -eq 0 ]; then
    step "=== 9️⃣  SCHEDULER (make scheduler-once) ==="
    if ! run_with_retry "$SCHEDULER_RETRIES" bash -lc "cd '$REPO_ROOT' && COMPOSE_FILE='$COMPOSE_FILE' make scheduler"; then
      svc_logs api-gateway 250
      svc_logs ingestion-worker 250
      die "Scheduler failed after ${SCHEDULER_RETRIES} attempts"
    fi
  else
    step "=== 9️⃣  SCHEDULER (skipped) ==="
    echo "ℹ️  --skip-scheduler set"
  fi

  queues_snapshot "after scheduler"

  echo
  echo "⏳ Waiting 5 seconds for workers..."
  sleep 5

  step "=== 🔟 ASSERT PIPELINE DID WORK (logs) ==="

  if ! wait_log_match "ingestion-worker" "inserted=[1-9][0-9]*" "$LOG_WAIT_S"; then
    echo "⚠️  Ingestion did not insert signals yet. Retrying scheduler once..."
    if [ "$SKIP_SCHEDULER" -eq 0 ]; then
      (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) || true
      sleep 4
    fi
    if ! wait_log_match "ingestion-worker" "inserted=[1-9][0-9]*" "$LOG_WAIT_S"; then
      svc_logs ingestion-worker 250
      die "Ingestion did not insert any signals"
    fi
  fi
  echo "✅ Ingestion OK"

  if ! wait_log_match "processing-worker" "Processed .* signals=[0-9]+" "$LOG_WAIT_S"; then
    svc_logs processing-worker 250
    die "Processing did not log any 'Processed ...' line"
  fi

  proc_text="$(svc_logs processing-worker 900)"
  signals_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'Processed .* signals=([0-9]+)' || printf '0')"
  created_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'pain_instances_created=([0-9]+)' || printf '0')"

  if [ "${signals_n}" -eq 0 ] && [ "${created_n}" -eq 0 ]; then
    echo "⚠️  Processing saw 0/0. Re-running scheduler once…"
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) >/dev/null 2>&1 || true
    sleep 4
    proc_text="$(svc_logs processing-worker 900)"
    signals_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'Processed .* signals=([0-9]+)' || printf '0')"
    created_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'pain_instances_created=([0-9]+)' || printf '0')"
  fi

  [ "${signals_n}" -ne 0 ] || [ "${created_n}" -ne 0 ] || die "Processing saw 0 signals and created 0 pain instances"
  echo "✅ Processing OK (signals=${signals_n} created=${created_n})"

  if ! wait_log_match "clustering-worker" "cluster_job" "$LOG_WAIT_S"; then
    echo "⚠️  Clustering did not emit cluster_job yet. Retrying scheduler once..."
    if [ "$SKIP_SCHEDULER" -eq 0 ]; then
      (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) || true
      sleep 4
    fi
    if ! wait_log_match "clustering-worker" "cluster_job" "$LOG_WAIT_S"; then
      svc_logs clustering-worker 250
      die "Clustering did not emit cluster_job"
    fi
  fi
  echo "✅ Clustering OK"

  step "=== 1️⃣0️⃣b TREND (make trend-once) ==="
  (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" DAY="$(date +%F)" make trend-once)

  if ! wait_log_match "trend-worker" "trend_job" "$LOG_WAIT_S"; then
    echo "⚠️  Trend did not emit trend_job yet. Retrying trend-once..."
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" DAY="$(date +%F)" make trend-once) || true
    sleep 3
    if ! wait_log_match "trend-worker" "trend_job" "$LOG_WAIT_S"; then
      svc_logs trend-worker 250
      die "Trend did not emit trend_job"
    fi
  fi
  echo "✅ Trend OK"

  if [ "$SKIP_TRENDS" -eq 0 ]; then
    step "=== 1️⃣1️⃣ API TRENDS ENDPOINTS (must not 500) ==="
    curl -fsS "${API_BASE_URL}/trending?vertical_id=${VERTICAL_ID}"  >/dev/null || die "GET /trending 500"
    curl -fsS "${API_BASE_URL}/emerging?vertical_id=${VERTICAL_ID}"  >/dev/null || die "GET /emerging 500"
    curl -fsS "${API_BASE_URL}/declining?vertical_id=${VERTICAL_ID}" >/dev/null || die "GET /declining 500"
    echo "✅ Trends endpoints OK"
  else
    step "=== 1️⃣1️⃣ API TRENDS ENDPOINTS (skipped) ==="
    echo "ℹ️  --skip-trends set"
  fi

  echo
  echo "==============================================="
  echo "✅ VALIDATION FINISHED"
  echo "==============================================="

  if [ "$KEEP_RUNNING" -eq 0 ]; then
    step "=== 🧹 CLEANUP (down) ==="
    dc down >/dev/null 2>&1 || true
    echo "✅ Services stopped"
  else
    step "=== 🧷 KEEP RUNNING ==="
    echo "ℹ️  --keep-running set; services left up"
  fi

} 2>&1 | tee "$LOGFILE"

echo
echo "📝 Log written to: $LOGFILE"
