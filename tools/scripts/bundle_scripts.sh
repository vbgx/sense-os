#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

TIMESTAMP="$(date +"%Y-%m-%d_%H%M")"
OUTPUT_FILE="$REPO_ROOT/scripts_bundle_${TIMESTAMP}.md"
GENERATED_AT="$(date +"%Y-%m-%d %H:%M:%S")"

SCRIPT_EXT_RE='\.(sh|bash|zsh|py|js|ts|rb|php|ps1|lua|sql|yml|yaml|toml)$'

is_script() {
  local f="$1"
  [ -x "$f" ] && return 0
  echo "$f" | grep -E "$SCRIPT_EXT_RE" >/dev/null 2>&1
}

# build file list once (avoid double find)
TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

find "$SCRIPT_DIR" -type f \
  ! -path "*/.git/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/__pycache__/*" \
  ! -name "scripts_bundle_*.md" \
  | sort > "$TMP_LIST"

# header
{
  echo "# Scripts Bundle — sense-os"
  echo
  echo "- Generated: **$GENERATED_AT**"
  echo "- Source folder: \`$SCRIPT_DIR\`"
  echo
  echo "---"
  echo
  echo "## Index"
  echo
} > "$OUTPUT_FILE"

COUNT=0
while IFS= read -r FILE; do
  if is_script "$FILE"; then
    COUNT=$((COUNT + 1))
    REL="$(relpath "$FILE")"
    echo "$COUNT. [$REL](#file-$COUNT)" >> "$OUTPUT_FILE"
  fi
done < "$TMP_LIST"

{
  echo
  echo "---"
  echo
} >> "$OUTPUT_FILE"

COUNT=0
while IFS= read -r FILE; do
  if is_script "$FILE"; then
    COUNT=$((COUNT + 1))
    REL="$(relpath "$FILE")"
    SIZE="$(stat -f%z "$FILE")"
    MODIFIED="$(date -r "$FILE" +"%Y-%m-%d %H:%M:%S")"
    HASH="$(shasum -a 256 "$FILE" | awk '{print $1}')"
    EXT="${FILE##*.}"

    {
      echo "## $COUNT. $REL"
      echo "<a id=\"file-$COUNT\"></a>"
      echo
      echo "- Path: \`$REL\`"
      echo "- Size: **$SIZE bytes**"
      echo "- Modified: **$MODIFIED**"
      echo "- SHA256: \`$HASH\`"
      echo
      echo "\`\`\`$EXT"
      cat "$FILE"
      echo
      echo "\`\`\`"
      echo
      echo "---"
      echo
    } >> "$OUTPUT_FILE"
  fi
done < "$TMP_LIST"

echo "OK: scripts bundled -> $OUTPUT_FILE"
