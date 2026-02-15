#!/usr/bin/env bash
set -euo pipefail

f="tools/scripts/validate_full_boot.sh"

# Replace the trend step invocation to pass DAY explicitly
perl -0777 -i.bak -pe 's/\(cd "\$REPO_ROOT" && COMPOSE_FILE="\$COMPOSE_FILE" make trend-once\)/\(cd "\$REPO_ROOT" && COMPOSE_FILE="\$COMPOSE_FILE" DAY="\$(date +%F)" make trend-once\)/g' "$f"

echo "✅ patched $f to pass DAY=\$(date +%F) to make trend-once"
