#!/usr/bin/env bash
set -euo pipefail

# LOCAL scheduler runner (NO docker).
# Runs EXACTLY ONE vertical using scheduler --mode once.

VERTICAL_ID="${VERTICAL_ID:-}"
VERTICAL="${VERTICAL:-}"
QUERY="${QUERY:-}"
LIMIT="${LIMIT:-}"
OFFSET="${OFFSET:-}"
DAY="${DAY:-}"

# If user gave VERTICAL_ID only, we use legacy DB id.
# Otherwise we prefer --vertical (config id like "ae", "analytics"...).

args=(python -m scheduler.main --mode once)

if [[ -n "${VERTICAL}" ]]; then
  args+=(--vertical "${VERTICAL}")
elif [[ -n "${VERTICAL_ID}" ]]; then
  args+=(--vertical-id "${VERTICAL_ID}")
else
  echo "❌ Need VERTICAL or VERTICAL_ID"
  echo "   Example: VERTICAL=ae make scheduler-once"
  echo "   Example: VERTICAL_ID=1 make scheduler-once"
  exit 1
fi

# Optional knobs
if [[ -n "${QUERY}" ]]; then args+=(--query "${QUERY}"); fi
if [[ -n "${LIMIT}" ]]; then args+=(--limit "${LIMIT}"); fi
if [[ -n "${OFFSET}" ]]; then args+=(--offset "${OFFSET}"); fi
if [[ -n "${DAY}" ]]; then args+=(--day "${DAY}"); fi

echo "⏱️  Scheduler once (LOCAL) => ${args[*]}"
exec "${args[@]}"
