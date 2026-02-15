#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

step "🌱 Seeding verticals..."
dc_exec api-gateway python -m db.seed
echo "✅ Seed done"
