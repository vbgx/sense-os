#!/usr/bin/env bash
set -euo pipefail

# disable history expansion (macOS bash/zsh oddities)
{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Shared helpers (dc, dc_exec, die, step, etc.)
source "$SCRIPT_DIR/_lib.sh"

SOURCE="reddit"
LIMIT="50"

usage() {
  cat <<USAGE
Usage: $0 <path/to/vertical.yml> [--source reddit] [--limit 50]

Example:
  $0 tools/fixtures/verticals/saas_founders.yml
  $0 tools/fixtures/verticals/saas_founders.yml --source reddit --limit 80
USAGE
}

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

VERTICAL_YAML=""
while [ $# -gt 0 ]; do
  case "$1" in
    --source)
      SOURCE="${2:-}"
      [ -n "$SOURCE" ] || die "--source requires a value"
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      [ -n "$LIMIT" ] || die "--limit requires a value"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [ -z "$VERTICAL_YAML" ]; then
        VERTICAL_YAML="$1"
      else
        die "Unknown arg: $1"
      fi
      shift
      ;;
  esac
done

[ -n "$VERTICAL_YAML" ] || die "Missing YAML path"
[ -f "$VERTICAL_YAML" ] || die "YAML not found: $VERTICAL_YAML"

# Parse YAML (simple structure: name, description, default_queries)
parse_yaml_local() {
  python3 - <<'PY' "$VERTICAL_YAML"
import sys
path = sys.argv[1]
name = None
queries = []
in_queries = False

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        raw = line.rstrip("\n")
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("name:"):
            name = s.split(":", 1)[1].strip().strip("\"").strip("'")
            in_queries = False
            continue
        if s.startswith("default_queries:"):
            in_queries = True
            continue
        if in_queries:
            if s.startswith("-"):
                q = s[1:].strip().strip("\"").strip("'")
                if q:
                    queries.append(q)
                continue
            if not raw.startswith(" "):
                in_queries = False

if not name:
    raise SystemExit("YAML is missing 'name:'")

print(name)
for q in queries:
    print(q)
PY
}

parse_yaml_via_container() {
  # Read YAML content from stdin inside the api-gateway container
  cat "$VERTICAL_YAML" | dc_exec api-gateway python - <<'PY'
import sys
data = sys.stdin.read().splitlines()
name = None
queries = []
in_queries = False

for line in data:
    raw = line.rstrip("\n")
    s = raw.strip()
    if not s or s.startswith("#"):
        continue
    if s.startswith("name:"):
        name = s.split(":", 1)[1].strip().strip("\"").strip("'")
        in_queries = False
        continue
    if s.startswith("default_queries:"):
        in_queries = True
        continue
    if in_queries:
        if s.startswith("-"):
            q = s[1:].strip().strip("\"").strip("'")
            if q:
                queries.append(q)
            continue
        if not raw.startswith(" "):
            in_queries = False

if not name:
    raise SystemExit("YAML is missing 'name:'")

print(name)
for q in queries:
    print(q)
PY
}

if command -v python3 >/dev/null 2>&1; then
  mapfile -t PARSED < <(parse_yaml_local)
else
  step "ℹ️  python3 not found locally; parsing YAML inside api-gateway container"
  mapfile -t PARSED < <(parse_yaml_via_container)
fi

VERTICAL_NAME="${PARSED[0]:-}"
[ -n "$VERTICAL_NAME" ] || die "Failed to parse name from $VERTICAL_YAML"

QUERIES=("${PARSED[@]:1}")
if [ ${#QUERIES[@]} -eq 0 ]; then
  die "No default_queries found in $VERTICAL_YAML"
fi

step "🌱 Ensure vertical exists: $VERTICAL_NAME"
VERTICAL_ID=$(dc_exec api-gateway python - <<PY
from db.session import SessionLocal
from db.repos import verticals

name = "${VERTICAL_NAME}"

db = SessionLocal()
try:
    v = verticals.get_by_name(db, name)
    if v is None:
        v = verticals.create(db, name)
    print(v.id)
finally:
    db.close()
PY
)

[ -n "$VERTICAL_ID" ] || die "Failed to resolve vertical id for $VERTICAL_NAME"

step "🚀 Running scheduler for vertical_id=$VERTICAL_ID source=$SOURCE limit=$LIMIT"
for q in "${QUERIES[@]}"; do
  step "→ QUERY: $q"
  COMPOSE_FILE="$COMPOSE_FILE" VERTICAL_ID="$VERTICAL_ID" SOURCE="$SOURCE" QUERY="$q" LIMIT="$LIMIT" \
    "$SCRIPT_DIR/run_scheduler_once.sh"
  echo "✅ Done for query: $q"
  echo
  sleep 1
done

echo "✅ All queries completed for $VERTICAL_NAME (vertical_id=$VERTICAL_ID)"
