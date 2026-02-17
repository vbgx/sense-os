#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VENV="${VENV:-$REPO_ROOT/.venv}"
PY="$VENV/bin/python"

[ -x "$PY" ] || die "Missing virtualenv at $VENV. Run: $REPO_ROOT/tools/scripts/dev_install.sh"

exec "$PY" -m processing_worker.main
