#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

FORCE="${FORCE:-0}"

if [ "$FORCE" != "1" ]; then
  die "Refusing to FLUSHALL without FORCE=1 (this wipes ALL redis data). Run: FORCE=1 $0"
fi

step "🧹 Flushing Redis (FLUSHALL)..."
dc_exec redis redis-cli FLUSHALL
echo "✅ Redis flushed"
