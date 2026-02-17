#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   tools/scripts/new_vertical.sh <id> "<Title>" "<Description>" [priority] [tags_csv]
#
# Example:
#   tools/scripts/new_vertical.sh fitness_coaches "Fitness Coaches" "Coaches selling programs and managing clients" 70 "fitness,coaching,b2c"

ID="${1:-}"
TITLE="${2:-}"
DESC="${3:-}"
PRIORITY="${4:-80}"
TAGS_CSV="${5:-}"

if [[ -z "$ID" || -z "$TITLE" || -z "$DESC" ]]; then
  echo "ERROR: missing args." >&2
  echo 'Usage: tools/scripts/new_vertical.sh <id> "<Title>" "<Description>" [priority] [tags_csv]' >&2
  exit 1
fi

DIR="config/verticals"
INDEX="${DIR}/verticals.json"
FILE="${DIR}/${ID}.yml"

if [[ ! -f "$INDEX" ]]; then
  echo "ERROR: index not found: $INDEX" >&2
  exit 1
fi

if [[ -f "$FILE" ]]; then
  echo "ERROR: vertical file already exists: $FILE" >&2
  exit 1
fi

# Basic safety: id format
if ! [[ "$ID" =~ ^[a-z0-9_]+$ ]]; then
  echo "ERROR: id must match ^[a-z0-9_]+$ (got: $ID)" >&2
  exit 1
fi

# Tags YAML array (optional)
TAGS_YAML=""
if [[ -n "$TAGS_CSV" ]]; then
  # shellcheck disable=SC2206
  IFS=',' read -r -a tags <<< "$TAGS_CSV"
  TAGS_YAML="tags: [$(printf "%s" "${tags[0]}"; for t in "${tags[@]:1}"; do printf ", %s" "$t"; done)]"
fi

mkdir -p "$DIR"

cat > "$FILE" <<YAML
id: ${ID}
name: ${ID}
title: ${TITLE}
description: ${DESC}

version: 1
enabled: true
priority: ${PRIORITY}
${TAGS_YAML}

# Backward-compatible field used by current code paths
default_queries:
  - "${ID} pain"
  - "${TITLE} tools"
  - "${TITLE} workflow"

# Optional richer ingestion defaults (workers may ignore safely)
ingestion:
  sources:
    - name: reddit
      query: "${ID}"
      limit: 80

defaults:
  language_allowlist: ["en"]
  min_signal_quality: 0.2
YAML

# Append to index (simple + safe)
cat >> "$INDEX" <<YAML

  - id: ${ID}
    file: ${ID}.yml
    enabled: true
    priority: ${PRIORITY}
YAML

echo "[OK] created: $FILE"
echo "[OK] updated index: $INDEX"
