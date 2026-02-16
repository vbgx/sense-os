#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

require_cmd uv

VENV="${VENV:-$REPO_ROOT/.venv}"

step "🐍 Create venv ($VENV)"
uv venv "$VENV"

# shellcheck disable=SC1090
source "$VENV/bin/activate"

step "📦 Install editable packages"
uv pip install -e "$REPO_ROOT/packages/application" \
  -e "$REPO_ROOT/packages/db" \
  -e "$REPO_ROOT/packages/domain" \
  -e "$REPO_ROOT/packages/queue" \
  -e "$REPO_ROOT/services/ingestion_worker" \
  -e "$REPO_ROOT/services/processing_worker" \
  -e "$REPO_ROOT/services/clustering_worker" \
  -e "$REPO_ROOT/services/trend_worker" \
  -e "$REPO_ROOT/services/scheduler" \
  -e "$REPO_ROOT/apps/api_gateway"

step "✅ Dev environment ready"
