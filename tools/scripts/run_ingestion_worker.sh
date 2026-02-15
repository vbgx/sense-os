#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

step "📜 Logs ingestion-worker"
dc logs -f --tail=200 ingestion-worker
