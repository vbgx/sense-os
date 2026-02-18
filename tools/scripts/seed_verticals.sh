#!/usr/bin/env bash
set -euo pipefail

echo
echo "🌱 Seeding verticals (LOCAL, no docker)"
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://$(whoami)@localhost:5432/sense}"
PSQL_DSN="${DATABASE_URL/+psycopg/}"

VERT_DIR="${VERT_DIR:-$REPO_ROOT/config/verticals}"
INDEX_JSON="$VERT_DIR/verticals.json"

psql_exec() {
  psql "$PSQL_DSN" -v ON_ERROR_STOP=1 -qAt "$@"
}

# 0) sanity: table exists
psql_exec -c "select 1 from information_schema.tables where table_name='verticals' limit 1;" >/dev/null \
  || { echo "❌ table verticals not found (run make migrate)"; exit 1; }

# 1) collect candidate vertical ids
# - if config/verticals/verticals.json has {"verticals":[{"id":".."}, ...]} use it
# - else fallback to *.json in directory (excluding verticals.json, _taxonomy.json, etc.)
collect_ids() {
  python - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
vert_dir = Path(__import__("os").environ.get("VERT_DIR", str(root / "config" / "verticals")))
index_json = vert_dir / "verticals.json"

ids = []

def is_seedable_id(x):
  s = str(x or "").strip()
  if not s: return False
  if s.startswith("_"): return False
  return True

if index_json.exists():
  try:
    doc = json.loads(index_json.read_text(encoding="utf-8"))
    vs = doc.get("verticals")
    if isinstance(vs, list):
      for it in vs:
        if isinstance(it, dict) and "id" in it and is_seedable_id(it["id"]):
          ids.append(str(it["id"]).strip())
  except Exception:
    pass

if not ids:
  # fallback: every *.json file as id=stem (excluding verticals.json)
  for p in sorted(vert_dir.glob("*.json")):
    if p.name == "verticals.json": 
      continue
    if p.name.startswith("_"):
      continue
    ids.append(p.stem)

# de-dup, stable order
seen = set()
out = []
for x in ids:
  if x in seen: 
    continue
  seen.add(x)
  out.append(x)

print("\n".join(out))
PY
}

IDS="$(collect_ids || true)"
if [[ -z "${IDS// }" ]]; then
  echo "⚠️  No vertical ids found in $VERT_DIR"
  exit 0
fi

# 2) insert idempotently
# We only seed "name" because schema is (id, name, created_at)
# and name is UNIQUE.
echo "→ inserting verticals..."
# feed via stdin to avoid shell escaping drama
printf "%s\n" "$IDS" | psql_exec \
  -c "create temp table if not exists _seed_verticals(name text) on commit drop;" \
  >/dev/null

printf "%s\n" "$IDS" | psql "$PSQL_DSN" -v ON_ERROR_STOP=1 -qAt <<'SQL'
\copy _seed_verticals(name) from stdin
SQL

psql_exec -c "
insert into verticals(name)
select name from _seed_verticals
where name is not null and length(trim(name)) > 0
on conflict (name) do nothing;
" >/dev/null

count="$(psql_exec -c "select count(*) from verticals;")"
echo "✅ Seed OK (verticals.count=$count)"
