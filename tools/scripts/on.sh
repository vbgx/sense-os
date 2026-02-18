#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SENSE-OS — BUTTON ON (✨fun edition✨)
#
# One command. Full stack boot. Migrate. Seed. Scheduler. Trends.
# With extra morale, emojis, and questionable jokes.
# =============================================================================

# disable history expansion (macOS bash/zsh oddities)
{ set +H 2>/dev/null || true; } >/dev/null 2>&1

# -----------------------------
# Colors (best-effort)
# -----------------------------
if [ -t 1 ]; then
  RED="$(printf '\033[31m')"
  GRN="$(printf '\033[32m')"
  YLW="$(printf '\033[33m')"
  BLU="$(printf '\033[34m')"
  MAG="$(printf '\033[35m')"
  CYN="$(printf '\033[36m')"
  BOLD="$(printf '\033[1m')"
  DIM="$(printf '\033[2m')"
  RST="$(printf '\033[0m')"
else
  RED=""; GRN=""; YLW=""; BLU=""; MAG=""; CYN=""; BOLD=""; DIM=""; RST=""
fi

# -----------------------------
# Fun helpers
# -----------------------------
banner() {
  echo
  echo "${BOLD}${CYN}╔══════════════════════════════════════════════╗${RST}"
  echo "${BOLD}${CYN}║            SENSE-OS — BUTTON  ON             ║${RST}"
  echo "${BOLD}${CYN}╚══════════════════════════════════════════════╝${RST}"
  echo "${DIM}💡 Tip: ON_FAST=1 ./tools/scripts/on.sh  (quick loop)${RST}"
  echo
}

joke() {
  # portable “random”: use $RANDOM if bash provides it, else time-based
  local n
  if [ -n "${RANDOM:-}" ]; then
    n=$((RANDOM % 10))
  else
    n=$(( $(date +%s) % 10 ))
  fi

  case "$n" in
    0) echo "🧠 Joke: Why do programmers hate nature? Too many bugs." ;;
    1) echo "🐳 Joke: Docker walked into a bar… the bartender said: 'I can’t serve you, you’re already contained.'" ;;
    2) echo "🧵 Joke: I told my thread to relax. It said: 'I can't, I'm running in parallel'." ;;
    3) echo "🧪 Joke: I wrote a test so good it passed… in production only." ;;
    4) echo "📦 Joke: My package.json and I are in a relationship. It’s complicated." ;;
    5) echo "🧯 Joke: The fire extinguisher is there because of… merge conflicts." ;;
    6) echo "🔁 Joke: I tried recursion once. I tried recursion once." ;;
    7) echo "🗃️ Joke: I love databases. They really know how to commit." ;;
    8) echo "🧊 Joke: My cache is like my motivation: invalidated often." ;;
    9) echo "⚡ Joke: I wanted to tell a UDP joke… but I’m not sure you’d get it." ;;
  esac
}

say() { echo "${BOLD}${BLU}▶${RST} $*"; }
ok()  { echo "${BOLD}${GRN}✓${RST} $*"; }
warn(){ echo "${BOLD}${YLW}⚠${RST} $*"; }
fail(){ echo "${BOLD}${RED}✖${RST} $*"; }

# -----------------------------
# Locate repo + validate script
# -----------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VALIDATE="$REPO_ROOT/tools/scripts/validate_full_boot.sh"
if [ ! -x "$VALIDATE" ]; then
  fail "missing or non-executable: $VALIDATE"
  echo "  fix: chmod +x tools/scripts/validate_full_boot.sh"
  exit 1
fi

# -----------------------------
# Defaults (safe)
# -----------------------------
export COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export VERTICAL_ID="${VERTICAL_ID:-1}"
export POSTGRES_WAIT_S="${POSTGRES_WAIT_S:-120}"
export API_WAIT_S="${API_WAIT_S:-120}"
export LOG_WAIT_S="${LOG_WAIT_S:-60}"
export SCHEDULER_RETRIES="${SCHEDULER_RETRIES:-2}"

# Logfile default (always produce a file)
if [ -z "${LOGFILE:-}" ]; then
  export LOGFILE="sense_on_$(date +%Y%m%d_%H%M%S).log"
fi

# -----------------------------
# Build args for validate script
# -----------------------------
args=()

# "Fast loop" preset
if [ "${ON_FAST:-0}" = "1" ]; then
  args+=(--no-down --no-build --skip-trends)
fi

if [ "${ON_NO_DOWN:-0}" = "1" ]; then args+=(--no-down); fi
if [ "${ON_NO_BUILD:-0}" = "1" ]; then args+=(--no-build); fi
if [ "${ON_SKIP_SEED:-0}" = "1" ]; then args+=(--skip-seed); fi
if [ "${ON_SKIP_SCHED:-0}" = "1" ] || [ "${ON_SKIP_SCHEDULER:-0}" = "1" ]; then args+=(--skip-scheduler); fi
if [ "${ON_SKIP_TRENDS:-0}" = "1" ]; then args+=(--skip-trends); fi
if [ "${ON_KEEP:-0}" = "1" ] || [ "${ON_KEEP_RUNNING:-0}" = "1" ]; then args+=(--keep-running); fi

args+=(--logfile "$LOGFILE")

# -----------------------------
# Showtime
# -----------------------------
banner
joke
echo

say "repo        = ${BOLD}$REPO_ROOT${RST}"
say "compose     = ${BOLD}$COMPOSE_FILE${RST}"
say "api         = ${BOLD}$API_BASE_URL${RST}"
say "vertical_id = ${BOLD}$VERTICAL_ID${RST}"
say "logfile     = ${BOLD}$LOGFILE${RST}"
echo

if [ "${ON_FAST:-0}" = "1" ]; then
  warn "FAST mode enabled 🏎️  (no-down, no-build, skip-trends)"
fi
if [ "${ON_KEEP:-0}" = "1" ] || [ "${ON_KEEP_RUNNING:-0}" = "1" ]; then
  warn "KEEP mode enabled 🧷 (services will stay up after success)"
fi
echo

say "Ignition sequence…"
echo "  3… 🚀"
sleep 0.2
echo "  2… 🔥"
sleep 0.2
echo "  1… ⚡"
sleep 0.2
echo "  ON! ✅"
echo

# Run validate script (real work happens there)
exec "$VALIDATE" "${args[@]}"
