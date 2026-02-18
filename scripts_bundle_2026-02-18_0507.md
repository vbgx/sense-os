# Scripts Bundle — sense-os

- Generated: **2026-02-18 05:07:19**
- Source folder: `/Users/victorbergeroux/Desktop/sense-os/tools/scripts`

---

## Index

1. [tools/scripts/_lib.sh](#file-1)
2. [tools/scripts/_patch_validate_trend_day.sh](#file-2)
3. [tools/scripts/bootstrap.sh](#file-3)
4. [tools/scripts/bundle_scripts.sh](#file-4)
5. [tools/scripts/ci.sh](#file-5)
6. [tools/scripts/ci_all.sh](#file-6)
7. [tools/scripts/dev.sh](#file-7)
8. [tools/scripts/dev_install.sh](#file-8)
9. [tools/scripts/ensure_ui_node_modules.js](#file-9)
10. [tools/scripts/flush_redis.sh](#file-10)
11. [tools/scripts/migrate.sh](#file-11)
12. [tools/scripts/new_vertical.sh](#file-12)
13. [tools/scripts/patch_makefile_migrate.py](#file-13)
14. [tools/scripts/publish_trend_job.sh](#file-14)
15. [tools/scripts/redis_queue_snapshot.sh](#file-15)
16. [tools/scripts/redis_queues_snapshot.sh](#file-16)
17. [tools/scripts/run_audit.sh](#file-17)
18. [tools/scripts/run_clustering_worker.sh](#file-18)
19. [tools/scripts/run_e2e_api.py](#file-19)
20. [tools/scripts/run_ingestion_worker.sh](#file-20)
21. [tools/scripts/run_processing_worker.sh](#file-21)
22. [tools/scripts/run_scheduler_backfill.sh](#file-22)
23. [tools/scripts/run_scheduler_once.sh](#file-23)
24. [tools/scripts/run_trend_worker.sh](#file-24)
25. [tools/scripts/seed_and_run_vertical.sh](#file-25)
26. [tools/scripts/seed_verticals.sh](#file-26)
27. [tools/scripts/sense.sh](#file-27)
28. [tools/scripts/validate_full_boot.sh](#file-28)
29. [tools/scripts/verticals_compile.py](#file-29)

---

## 1. tools/scripts/_lib.sh
<a id="file-1"></a>

- Path: `tools/scripts/_lib.sh`
- Size: **1043 bytes**
- Modified: **2026-02-18 04:12:17**
- SHA256: `b4587a35267890b13983c9582d4678748ab5ab3ba7f23d3f9f065cf3ff6f82b7`

```sh
#!/usr/bin/env bash
set -euo pipefail

# Repo root = 2 niveaux au-dessus de tools/scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
COMPOSE_PATH="$REPO_ROOT/$COMPOSE_FILE"

# Local defaults for worker scripts (can be overridden by env)
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export REDIS_DSN="${REDIS_DSN:-$REDIS_URL}"
export POSTGRES_DSN="${POSTGRES_DSN:-postgresql+psycopg://postgres:postgres@localhost:5432/sense}"

die()  { printf '❌ %s\n' "$*" >&2; exit 1; }
step() { printf '\n%s\n' "$*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

dc() {
  require_cmd docker
  docker compose -f "$COMPOSE_PATH" "$@"
}

dc_exec() {
  local svc="$1"; shift
  dc exec -T "$svc" "$@"
}

dc_logs() {
  local svc="$1"; shift
  dc logs --no-color "$svc" "$@"
}

relpath() {
  # print path relative to repo root
  local abs="$1"
  echo "${abs#"$REPO_ROOT"/}"
}

```

---

## 2. tools/scripts/_patch_validate_trend_day.sh
<a id="file-2"></a>

- Path: `tools/scripts/_patch_validate_trend_day.sh`
- Size: **398 bytes**
- Modified: **2026-02-15 06:57:41**
- SHA256: `f680cceb5f4ab35d65df2fe232526f4f055e86bfa0d496afa650f5baba6a9cbe`

```sh
#!/usr/bin/env bash
set -euo pipefail

f="tools/scripts/validate_full_boot.sh"

# Replace the trend step invocation to pass DAY explicitly
perl -0777 -i.bak -pe 's/\(cd "\$REPO_ROOT" && COMPOSE_FILE="\$COMPOSE_FILE" make trend-once\)/\(cd "\$REPO_ROOT" && COMPOSE_FILE="\$COMPOSE_FILE" DAY="\$(date +%F)" make trend-once\)/g' "$f"

echo "✅ patched $f to pass DAY=\$(date +%F) to make trend-once"

```

---

## 3. tools/scripts/bootstrap.sh
<a id="file-3"></a>

- Path: `tools/scripts/bootstrap.sh`
- Size: **72 bytes**
- Modified: **2026-02-18 02:56:08**
- SHA256: `f48083831a3639fa087ef3d57eecf19980e9469d2b02e98da7145d9c46ee8265`

```sh
#!/usr/bin/env bash
set -euo pipefail

uv sync
cd apps/web
pnpm install

```

---

## 4. tools/scripts/bundle_scripts.sh
<a id="file-4"></a>

- Path: `tools/scripts/bundle_scripts.sh`
- Size: **1852 bytes**
- Modified: **2026-02-15 06:17:19**
- SHA256: `72d63a99683203c8d5453b0d2a114741685d0ed0106bcb031a97cd6ed3520bda`

```sh
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

```

---

## 5. tools/scripts/ci.sh
<a id="file-5"></a>

- Path: `tools/scripts/ci.sh`
- Size: **1125 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `ae792812af05420b0eb65615d222655a3cd15ff93730f190fb0d3099a592d801`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

require_cmd uv

VENV="${VENV:-$REPO_ROOT/.venv-ci}"
PY="$VENV/bin/python"

step "🐍 Create venv ($VENV)"
uv venv "$VENV"

# shellcheck disable=SC1090
source "$VENV/bin/activate"

step "📦 Install editable dependencies"
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

step "🧪 Lintable checks"
"$PY" "$REPO_ROOT/tools/ci/check_no_db_imports_in_api_gateway.py"

step "🧪 Unit tests"
"$PY" -m pytest -q

step "🧪 DB invariants (docker)"
COMPOSE_FILE="$COMPOSE_FILE" "$REPO_ROOT/tools/ci/check_alembic_head.sh"
COMPOSE_FILE="$COMPOSE_FILE" "$REPO_ROOT/tools/ci/check_double_consume.sh"
COMPOSE_FILE="$COMPOSE_FILE" "$REPO_ROOT/tools/ci/check_dlq_replay.sh"

step "✅ CI complete"

```

---

## 6. tools/scripts/ci_all.sh
<a id="file-6"></a>

- Path: `tools/scripts/ci_all.sh`
- Size: **117 bytes**
- Modified: **2026-02-18 02:56:08**
- SHA256: `4bf2d3df85da9adfd50ce2a55ebe964085c10a8edc1ca8a7e9896140ab813039`

```sh
#!/usr/bin/env bash
set -euo pipefail

make lint
make test
pytest -q tests/contract/inter_workers
make typecheck-web

```

---

## 7. tools/scripts/dev.sh
<a id="file-7"></a>

- Path: `tools/scripts/dev.sh`
- Size: **0 bytes**
- Modified: **2026-02-14 20:03:47**
- SHA256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

```sh

```

---

## 8. tools/scripts/dev_install.sh
<a id="file-8"></a>

- Path: `tools/scripts/dev_install.sh`
- Size: **793 bytes**
- Modified: **2026-02-18 04:17:25**
- SHA256: `bbdd6607668c457fde9cbcab87b72e0044b7cfc4e7f14603a1c05fbeed53761f`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

require_cmd uv

VENV="${VENV:-$REPO_ROOT/.venv}"

if [ -x "$VENV/bin/python" ]; then
  step "🐍 Reuse venv ($VENV)"
else
  step "🐍 Create venv ($VENV)"
  uv venv "$VENV"
fi

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

```

---

## 9. tools/scripts/ensure_ui_node_modules.js
<a id="file-9"></a>

- Path: `tools/scripts/ensure_ui_node_modules.js`
- Size: **1002 bytes**
- Modified: **2026-02-17 13:24:09**
- SHA256: `5e8183902124f67d4d29a1ce4962f4d3b2955aa2bfe0d545c5c32aa852f32114`

```js
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const appsNodeModules = path.join(root, "apps", "node_modules");
const webNodeModules = path.join(root, "apps", "web", "node_modules");

const packages = ["tailwindcss", "tw-animate-css"];

fs.mkdirSync(appsNodeModules, { recursive: true });

for (const pkg of packages) {
  const target = path.join(webNodeModules, pkg);
  const link = path.join(appsNodeModules, pkg);

  if (!fs.existsSync(target)) {
    // eslint-disable-next-line no-console
    console.warn(`ensure_ui_node_modules: missing ${target}`);
    continue;
  }

  try {
    const stat = fs.lstatSync(link);
    if (stat.isSymbolicLink() || stat.isDirectory()) continue;
  } catch (err) {
    // ignore and create link
  }

  try {
    fs.rmSync(link, { recursive: true, force: true });
  } catch (err) {
    // ignore
  }

  const type = process.platform === "win32" ? "junction" : "dir";
  fs.symlinkSync(target, link, type);
}

```

---

## 10. tools/scripts/flush_redis.sh
<a id="file-10"></a>

- Path: `tools/scripts/flush_redis.sh`
- Size: **315 bytes**
- Modified: **2026-02-15 06:16:09**
- SHA256: `d86f2734b170c16377b76716abcf3c16732f43e5792f9296fa14d4999999e328`

```sh
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

```

---

## 11. tools/scripts/migrate.sh
<a id="file-11"></a>

- Path: `tools/scripts/migrate.sh`
- Size: **1050 bytes**
- Modified: **2026-02-17 17:03:34**
- SHA256: `cd447b8fe497e3acfe65f543600a1bee2e5ebd5703bda81e490f24d8d0d34ef9`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

MODE="${MODE:-auto}" # auto | docker | local
ALEMBIC_BIN="${ALEMBIC_BIN:-alembic}"
ALEMBIC_INI="${ALEMBIC_INI:-$REPO_ROOT/packages/db/alembic.ini}"

run_local() {
  step "🗄️  Alembic migrate (local)"
  (cd "$REPO_ROOT" && "$ALEMBIC_BIN" -c "$ALEMBIC_INI" upgrade head)
}

run_docker() {
  step "🗄️  Alembic migrate (docker)"
  if dc ps -q api-gateway >/dev/null 2>&1 && [ -n "$(dc ps -q api-gateway)" ]; then
    dc_exec api-gateway bash -lc "python -m alembic -c /app/packages/db/alembic.ini upgrade head"
  else
    dc run --rm --build api-gateway bash -lc "python -m alembic -c /app/packages/db/alembic.ini upgrade head"
  fi
}

if [ "$MODE" = "local" ]; then
  run_local
  exit 0
fi

if [ "$MODE" = "docker" ]; then
  run_docker
  exit 0
fi

# auto: prefer docker if api-gateway container exists, else local
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  run_docker
else
  run_local
fi

```

---

## 12. tools/scripts/new_vertical.sh
<a id="file-12"></a>

- Path: `tools/scripts/new_vertical.sh`
- Size: **1933 bytes**
- Modified: **2026-02-17 13:24:09**
- SHA256: `5417b991b1f82a55824ecfb5cf24837b16984175a12c8942f9515e1ec94ae4de`

```sh
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

```

---

## 13. tools/scripts/patch_makefile_migrate.py
<a id="file-13"></a>

- Path: `tools/scripts/patch_makefile_migrate.py`
- Size: **612 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `25b99b52ac6263b9140b7f9998b9a0a47b7eddf9dea363abb99cdc445a962f15`

```py
from __future__ import annotations

import re
from pathlib import Path

MAKEFILE = Path("Makefile")
s = MAKEFILE.read_text(encoding="utf-8")

replacement = (
    "migrate:\n"
    "\t@COMPOSE_FILE=$(COMPOSE_FILE) ./tools/scripts/migrate.sh\n"
)

m = re.search(r"(?m)^[A-Za-z0-9_.-]+:\s*$", s)
# Replace only the migrate target block
pattern = re.compile(
    r"(?ms)^migrate:\s*\n(?:\t.*\n)*"
)

if not pattern.search(s):
    raise SystemExit("migrate target not found in Makefile")

s2 = pattern.sub(replacement, s, count=1)
MAKEFILE.write_text(s2, encoding="utf-8")
print("OK: Makefile migrate target updated")

```

---

## 14. tools/scripts/publish_trend_job.sh
<a id="file-14"></a>

- Path: `tools/scripts/publish_trend_job.sh`
- Size: **574 bytes**
- Modified: **2026-02-15 06:58:08**
- SHA256: `a0ec4100b33c0aecf0556c90e2662a2b805b27b4c32ea37503020d6d3f464d4e`

```sh
#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
VERTICAL_ID="${VERTICAL_ID:-1}"
DAY="${DAY:-}"

# Default: today (host local), matches validate run day
if [ -z "${DAY}" ]; then
  DAY="$(date +%F)"
fi

payload="$(printf '{"type":"trend_job","day":"%s","vertical_id":%s,"cluster_version":"tfidf_v1","formula_version":"formula_v1"}' "$DAY" "$VERTICAL_ID")"

docker compose -f "${COMPOSE_FILE}" exec -T redis redis-cli LPUSH trend "${payload}" >/dev/null
echo "✅ trend job published (day=${DAY} vertical=${VERTICAL_ID})"

```

---

## 15. tools/scripts/redis_queue_snapshot.sh
<a id="file-15"></a>

- Path: `tools/scripts/redis_queue_snapshot.sh`
- Size: **420 bytes**
- Modified: **2026-02-15 07:51:04**
- SHA256: `5a8b8b494a3925513955f24118b3c19fb90b377f9e35433306b6eecd9ad6f14d`

```sh
#!/usr/bin/env bash
set -euo pipefail
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

# queues Redis (lists) qu'on veut observer
QUEUES=("ingest" "process" "cluster" "trend")

echo "---- redis queues snapshot ----"
for q in "${QUEUES[@]}"; do
  n="$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli LLEN "$q" | tr -d '\r')"
  echo "queue=$q len=$n"
done
echo "--------------------------------"

```

---

## 16. tools/scripts/redis_queues_snapshot.sh
<a id="file-16"></a>

- Path: `tools/scripts/redis_queues_snapshot.sh`
- Size: **1537 bytes**
- Modified: **2026-02-15 08:10:13**
- SHA256: `5b749cba35787c1b8811aa6fbf90dc612b21edf915ae5c1ec9011757c73f0d4c`

```sh
#!/usr/bin/env bash
set -euo pipefail

{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Optional label for logs
LABEL="${1:-manual}"

# Try to use shared helpers if available
if [ -f "$SCRIPT_DIR/_lib.sh" ]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/_lib.sh"
fi

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

queues=("ingest" "process" "cluster" "trend")

echo "📦 QUEUES (${LABEL})"
echo "---- redis queues snapshot ----"

# Prefer dc_exec from _lib.sh (if defined), else fallback.
if command -v dc_exec >/dev/null 2>&1; then
  # Ensure redis service is running
  if ! dc ps --services 2>/dev/null | grep -q '^redis$'; then
    echo 'service "redis" not found in compose config' >&2
    exit 1
  fi
  if ! dc ps redis 2>/dev/null | grep -q 'Up'; then
    echo 'service "redis" is not running' >&2
    exit 1
  fi

  for q in "${queues[@]}"; do
    len="$(dc_exec redis redis-cli LLEN "$q" | tr -d '\r' | tail -n 1)"
    len="${len:-0}"
    echo "queue=${q} len=${len}"
  done
else
  # Fallback (no _lib.sh)
  if ! docker compose -f "$COMPOSE_FILE" ps redis 2>/dev/null | grep -q 'Up'; then
    echo 'service "redis" is not running' >&2
    exit 1
  fi

  for q in "${queues[@]}"; do
    len="$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli LLEN "$q" | tr -d '\r' | tail -n 1)"
    len="${len:-0}"
    echo "queue=${q} len=${len}"
  done
fi

echo "--------------------------------"

```

---

## 17. tools/scripts/run_audit.sh
<a id="file-17"></a>

- Path: `tools/scripts/run_audit.sh`
- Size: **4879 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `c4da96010686e6313b3f6613527f0b09cb495883723abadfe8eea82db2c32929`

```sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

OUT="${1:-audit.log}"

# Ensure required tools don't explode the script
command -v rg >/dev/null 2>&1 || {
  echo "ERROR: ripgrep (rg) is required. Install it, then re-run." >&2
  exit 1
}

(
  echo "==================== SENSE OS ARCHITECTURE AUDIT ===================="
  echo "Timestamp: $(date)"
  echo "Root: $ROOT"
  echo

  echo "==================== 0) CONTEXTE ===================="
  pwd
  git rev-parse --show-toplevel || true
  git status --porcelain=v1 || true
  git branch --show-current || true
  git log -1 --oneline --decorate || true
  echo
  python --version || true
  uv --version || true
  pip --version || true
  node --version || true
  pnpm --version || true

  echo
  echo "==================== 1) STRUCTURE ===================="
  find apps services packages infra tools tests -maxdepth 3 -type d 2>/dev/null | sort || true
  echo
  ls -la || true
  echo
  # Avoid zsh glob failures: use find instead of docker-compose*.yml
  for f in Makefile pyproject.toml uv.lock requirements.txt package.json pnpm-lock.yaml turbo.json; do
    [ -e "$f" ] && ls -la "$f" || true
  done
  find . -maxdepth 2 -type f \( -name "docker-compose.yml" -o -name "docker-compose.*.yml" -o -name "compose.yml" -o -name "compose.*.yml" \) -print -exec ls -la {} \; 2>/dev/null || true

  echo
  echo "==================== 2) DEPENDENCIES & BOUNDARIES ===================="
  find . -maxdepth 4 -name "pyproject.toml" -print || true
  echo
  rg -n "from packages\.|import packages\." -S apps services packages || true
  rg -n "from services\.|import services\." -S apps services packages || true
  rg -n "from apps\.|import apps\." -S apps services packages || true
  echo
  rg -n "sqlalchemy|fastapi|redis|celery|rq|dramatiq|psycopg|alembic|pydantic" -S packages/domain || true

  echo
  echo "==================== 3) DB & MIGRATIONS ===================="
  find packages/db -maxdepth 4 -type f 2>/dev/null | sort || true
  echo
  find . -maxdepth 6 \( -name "alembic.ini" -o -name "env.py" -o -path "*alembic/versions/*" \) 2>/dev/null | sort || true
  echo
  ls -lt packages/db 2>/dev/null || true
  echo
  find . -maxdepth 8 -path "*alembic/versions/*" -type f -print0 2>/dev/null | xargs -0 ls -lt 2>/dev/null | head -n 50 || true
  echo
  find infra -type f \( -name "*.sql" -o -name "*.sh" \) 2>/dev/null | sort || true
  rg -n "CREATE TABLE|ALTER TABLE|CREATE INDEX|DROP|GRANT|EXTENSION|MATERIALIZED" infra -S || true

  echo
  echo "==================== 4) QUEUE & WORKERS ===================="
  find packages/queue -maxdepth 4 -type f 2>/dev/null | sort || true
  echo
  find services -maxdepth 4 -type f \( -name "main.py" -o -name "__main__.py" -o -name "worker*.py" -o -name "run*.py" \) 2>/dev/null | sort || true
  echo
  rg -n "idempot|dedup|retry|backoff|ack|nack|dead.?letter|dlq|requeue|visibility|lease" -S services packages || true
  echo
  rg -n "asyncio|create_task|gather|ThreadPool|ProcessPool|multiprocessing|concurrency|parallel|uvicorn.*workers" -S apps services || true

  echo
  echo "==================== 5) API GATEWAY ===================="
  find apps/api_gateway -maxdepth 4 -type f 2>/dev/null | sort || true
  echo
  rg -n "APIRouter|Depends|startup|lifespan|middleware" -S apps/api_gateway || true
  echo
  rg -n "sqlalchemy|Session|engine|alembic" -S apps/api_gateway services || true

  echo
  echo "==================== 6) CONFIG & SECRETS ===================="
  find . -maxdepth 5 -type f \( -name "*.env*" -o -name "*settings*.py" -o -name "config*.py" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort || true
  echo
  rg -n "DATABASE_URL|POSTGRES|REDIS|QUEUE|BROKER|S3|OPENSEARCH|QDRANT|API_KEY|SECRET" -S . || true

  echo
  echo "==================== 7) TESTS ===================="
  find tests -maxdepth 4 -type f 2>/dev/null | sort || true
  echo
  rg -n "pytest\.mark|fixture|DATABASE_URL|POSTGRES|alembic|migrate|rollback|transaction|session" -S tests packages || true
  echo
  find tests -maxdepth 3 -type d 2>/dev/null | sort || true

  echo
  echo "==================== 8) OBSERVABILITY ===================="
  rg -n "structlog|loguru|logging\.|prometheus|opentelemetry|sentry|datadog|jaeger|trace" -S apps services packages infra || true
  echo
  find docs infra -maxdepth 5 -type f \( -iname "*runbook*" -o -iname "*ops*" -o -iname "*deploy*" \) 2>/dev/null | sort || true

  echo
  echo "==================== 9) HYGIENE (DRIFT SIGNALS) ===================="
  echo "---- egg-info present ----"
  find . -type d -name "*.egg-info" 2>/dev/null | sort || true
  echo
  echo "---- __pycache__ present ----"
  find . -type d -name "__pycache__" 2>/dev/null | head -n 200 || true
  echo
  echo "==================== END AUDIT ===================="

) &> "$OUT"

echo "Audit written to: $OUT"

```

---

## 18. tools/scripts/run_clustering_worker.sh
<a id="file-18"></a>

- Path: `tools/scripts/run_clustering_worker.sh`
- Size: **262 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `bd77b78c2b085d92a450693ba1b4194afa216654df67b0788c76c6a3e081cf42`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VENV="${VENV:-$REPO_ROOT/.venv}"
PY="$VENV/bin/python"

[ -x "$PY" ] || die "Missing virtualenv at $VENV. Run: $REPO_ROOT/tools/scripts/dev_install.sh"

exec "$PY" -m clustering_worker.main

```

---

## 19. tools/scripts/run_e2e_api.py
<a id="file-19"></a>

- Path: `tools/scripts/run_e2e_api.py`
- Size: **4361 bytes**
- Modified: **2026-02-17 13:24:09**
- SHA256: `24cb09716cff4e96acaf513cc9a6411175c7f022902edc087cf06d1ecb30e1f2`

```py
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Ensure local packages resolve without a virtualenv install.
for rel in (
    "apps/api_gateway/src",
    "packages/application/src",
    "packages/db/src",
    "packages/domain/src",
    "packages/queue/src",
    "services/scheduler/src",
):
    path = ROOT / rel
    if path.exists():
        sys.path.insert(0, str(path))


def _configure_env() -> Path:
    raw = os.getenv("E2E_DB_PATH")
    if raw:
        db_path = Path(raw).expanduser()
        if not db_path.is_absolute():
            db_path = (ROOT / db_path).resolve()
    else:
        db_path = ROOT / ".tmp" / "sense_os_e2e.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    dsn = f"sqlite+pysqlite:///{db_path}"
    os.environ["DATABASE_URL"] = dsn
    os.environ["POSTGRES_DSN"] = dsn
    return db_path


def _seed_data() -> None:
    from sqlalchemy.orm import sessionmaker

    from db.adapters.trends import reset_trends_adapter
    from db.engine import get_engine, reset_engine
    from db.models import Base, ClusterDailyHistory, PainCluster, Vertical

    reset_trends_adapter()
    reset_engine()
    engine = get_engine()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        vertical = Vertical(id=1, name="SaaS")
        session.add(vertical)

        cluster_a = PainCluster(
            vertical_id=1,
            cluster_version="v1",
            cluster_key="cluster-a",
            title="Onboarding drop-off",
            size=120,
            cluster_summary="Teams lose users during onboarding due to unclear activation steps.",
            exploitability_score=85,
            exploitability_tier="STRONG_BUILD",
            opportunity_window_status="EARLY",
            breakout_score=72,
            confidence_score=82,
            severity_score=65,
            recurrence_score=58,
            monetizability_score=61,
            saturation_score=22,
            contradiction_score=9,
            competitive_heat_score=34,
            dominant_persona="Product leader",
            key_phrases_json=json.dumps(["onboarding", "activation", "time-to-value"]),
            top_signal_ids_json=json.dumps([101, 102, 103]),
        )
        cluster_b = PainCluster(
            vertical_id=1,
            cluster_version="v1",
            cluster_key="cluster-b",
            title="Support backlog",
            size=80,
            cluster_summary="Support teams are overwhelmed and SLA breaches are rising.",
            exploitability_score=70,
            exploitability_tier="INVESTIGATE",
            opportunity_window_status="PEAK",
            breakout_score=41,
            confidence_score=63,
            severity_score=52,
            recurrence_score=47,
            monetizability_score=49,
            saturation_score=30,
            contradiction_score=14,
            competitive_heat_score=41,
            dominant_persona="Support lead",
            key_phrases_json=json.dumps(["support tickets", "triage", "sla"]),
            top_signal_ids_json=json.dumps([201, 202]),
        )

        session.add_all([cluster_a, cluster_b])
        session.flush()

        today = date.today()
        timeline = []
        for i in range(6):
            day = today - timedelta(days=6 - i)
            timeline.append(
                ClusterDailyHistory(
                    cluster_id=str(cluster_a.id),
                    day=day,
                    volume=12 + i,
                    growth_rate=0.08 * i,
                    velocity=0.12 * i,
                    breakout_flag=i >= 3,
                )
            )
        session.add_all(timeline)

        session.commit()
    finally:
        session.close()


def main() -> None:
    _configure_env()
    _seed_data()

    host = os.getenv("E2E_API_HOST", "127.0.0.1")
    port = int(os.getenv("E2E_API_PORT", "8000"))
    log_level = os.getenv("E2E_API_LOG_LEVEL", "info")

    import uvicorn

    uvicorn.run("api_gateway.main:app", host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()

```

---

## 20. tools/scripts/run_ingestion_worker.sh
<a id="file-20"></a>

- Path: `tools/scripts/run_ingestion_worker.sh`
- Size: **261 bytes**
- Modified: **2026-02-18 04:05:11**
- SHA256: `9af5147edbfa221e43e6e7e3b56655ed868cd09bf818d10537cf30b62a813b07`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VENV="${VENV:-$REPO_ROOT/.venv}"
PY="$VENV/bin/python"

[ -x "$PY" ] || die "Missing virtualenv at $VENV. Run: $REPO_ROOT/tools/scripts/dev_install.sh"

exec "$PY" -m ingestion_worker.main

```

---

## 21. tools/scripts/run_processing_worker.sh
<a id="file-21"></a>

- Path: `tools/scripts/run_processing_worker.sh`
- Size: **262 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `79727a54da71ef00a4dcf973596523e3c4438cb96ae22defcb17ee41a9f15c2c`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VENV="${VENV:-$REPO_ROOT/.venv}"
PY="$VENV/bin/python"

[ -x "$PY" ] || die "Missing virtualenv at $VENV. Run: $REPO_ROOT/tools/scripts/dev_install.sh"

exec "$PY" -m processing_worker.main

```

---

## 22. tools/scripts/run_scheduler_backfill.sh
<a id="file-22"></a>

- Path: `tools/scripts/run_scheduler_backfill.sh`
- Size: **1031 bytes**
- Modified: **2026-02-15 12:00:36**
- SHA256: `ff6baa506f39011210f212f1b82a4da5115d63ba4208ff1832f56e8e113585e8`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VERTICAL_ID="${VERTICAL_ID:-1}"
SOURCE="${SOURCE:-reddit}"
QUERY="${QUERY:-saas}"
LIMIT="${LIMIT:-}"
DAYS="${DAYS:-90}"
START="${START:-}"
END="${END:-}"
SERIES="${SERIES:-1}"

step "⏱️  Scheduler backfill (vertical=$VERTICAL_ID source=$SOURCE days=$DAYS series=$SERIES)"

args=(
  --mode backfill
  --vertical-id "$VERTICAL_ID"
  --source "$SOURCE"
)

if [ -n "$QUERY" ]; then
  args+=(--query "$QUERY")
fi
if [ -n "$LIMIT" ]; then
  args+=(--limit "$LIMIT")
fi
if [ -n "$START" ]; then
  args+=(--start "$START")
fi
if [ -n "$END" ]; then
  args+=(--end "$END")
fi
if [ -n "$DAYS" ]; then
  args+=(--days "$DAYS")
fi
if [ "$SERIES" = "0" ]; then
  args+=(--no-series)
fi

# Run inside api-gateway container for access to db/redis
# shellcheck disable=SC2086

dc_exec api-gateway env \
  PYTHONPATH=/app/services/scheduler/src:/app/packages/db/src:/app/packages/queue/src \
  python -m scheduler.main \
  "${args[@]}"

echo "✅ Backfill scheduler done"

```

---

## 23. tools/scripts/run_scheduler_once.sh
<a id="file-23"></a>

- Path: `tools/scripts/run_scheduler_once.sh`
- Size: **564 bytes**
- Modified: **2026-02-17 17:03:34**
- SHA256: `61e462124be49dcf16848183c0848085e12e671944d84b7eaa90556f625da545`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VERTICAL_ID="${VERTICAL_ID:-1}"
SOURCE="${SOURCE:-reddit}"
QUERY="${QUERY:-saas}"
LIMIT="${LIMIT:-50}"

step "⏱️  Scheduler once (vertical=$VERTICAL_ID source=$SOURCE query=$QUERY limit=$LIMIT)"

dc_exec api-gateway env \
  PYTHONPATH=/app/services/scheduler/src:/app/packages/db/src:/app/packages/queue/src \
  python -m scheduler.main \
    --mode once \
    --vertical-id "$VERTICAL_ID" \
    --source "$SOURCE" \
    --query "$QUERY" \
    --limit "$LIMIT"

echo "✅ Scheduler done"

```

---

## 24. tools/scripts/run_trend_worker.sh
<a id="file-24"></a>

- Path: `tools/scripts/run_trend_worker.sh`
- Size: **257 bytes**
- Modified: **2026-02-18 04:05:14**
- SHA256: `a80231ea1784f52c18617d1816f9d71cccb1c06e2c1ed047d82109da299a1021`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

VENV="${VENV:-$REPO_ROOT/.venv}"
PY="$VENV/bin/python"

[ -x "$PY" ] || die "Missing virtualenv at $VENV. Run: $REPO_ROOT/tools/scripts/dev_install.sh"

exec "$PY" -m trend_worker.main

```

---

## 25. tools/scripts/seed_and_run_vertical.sh
<a id="file-25"></a>

- Path: `tools/scripts/seed_and_run_vertical.sh`
- Size: **4490 bytes**
- Modified: **2026-02-17 17:03:34**
- SHA256: `b6ed6273444422c3d30e5c308cfe0c737073e1c1698475cc1e134799991bf1bc`

```sh
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
  $0 config/verticals/saas_founders.yml
  $0 config/verticals/saas_founders.yml --source reddit --limit 80
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

```

---

## 26. tools/scripts/seed_verticals.sh
<a id="file-26"></a>

- Path: `tools/scripts/seed_verticals.sh`
- Size: **164 bytes**
- Modified: **2026-02-15 06:16:23**
- SHA256: `9ea9271df8e8551ad315a2345141aa32b80d63db81ca7f9ea2b4e683efb58439`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

step "🌱 Seeding verticals..."
dc_exec api-gateway python -m db.seed
echo "✅ Seed done"

```

---

## 27. tools/scripts/sense.sh
<a id="file-27"></a>

- Path: `tools/scripts/sense.sh`
- Size: **921 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `e761821086f9b8cfbb3f890f536f53236762db779cfd6445fb1198b2ebc1147b`

```sh
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

cmd="${1:-}"
shift || true

case "$cmd" in
  migrate)   exec "$SCRIPT_DIR/migrate.sh" "$@" ;;
  seed)     exec "$SCRIPT_DIR/seed_verticals.sh" "$@" ;;
  flush-redis) exec "$SCRIPT_DIR/flush_redis.sh" "$@" ;;
  logs)
    svc="${1:-}"; [ -n "$svc" ] || die "Usage: $0 logs <service>"
    exec dc logs -f --tail=200 "$svc"
    ;;
  validate)  exec "$SCRIPT_DIR/validate_full_boot.sh" "$@" ;;
  bundle)    exec "$SCRIPT_DIR/bundle_scripts.sh" "$@" ;;
  *)
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  migrate         Alembic upgrade head"
    echo "  seed            Seed verticals"
    echo "  flush-redis     FLUSHALL (requires FORCE=1)"
    echo "  logs <service>  Follow docker compose logs"
    echo "  validate        Full boot validation"
    echo "  bundle          Generate scripts bundle md"
    exit 1
    ;;
esac

```

---

## 28. tools/scripts/validate_full_boot.sh
<a id="file-28"></a>

- Path: `tools/scripts/validate_full_boot.sh`
- Size: **14460 bytes**
- Modified: **2026-02-17 01:31:40**
- SHA256: `91b3bf79b98f432c7c2a2218ff7a501829391eadb2f2c8c1d0869bfb884987a8`

```sh
#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Sense OS Full Stack Validation
#
# Purpose:
#   Boot the full stack (Postgres, Redis, API, workers), run migrations + seed,
#   execute the scheduler, verify ingestion/processing/clustering/trending, and
#   confirm API trend endpoints respond successfully.
#
# Usage:
#   ./tools/scripts/validate_full_boot.sh [options]
#
# Options:
#   --no-down         Do not run 'docker compose down -v' (keeps volumes)
#   --no-build        Do not rebuild images on 'up'
#   --skip-seed       Skip 'make seed'
#   --skip-scheduler  Skip 'make scheduler'
#   --skip-trends     Skip /trending, /emerging, /declining endpoint checks
#   --keep-running    Do not shut down services on success
#   --logfile <path>  Write output to this logfile
#
# Env (optional):
#   COMPOSE_FILE      Path to compose file (default: infra/docker/docker-compose.yml)
#   API_BASE_URL      Base URL for API (default: http://localhost:8000)
#   HEALTH_PATH       Health path (default: /health)
#   POSTGRES_WAIT_S   Postgres health wait seconds (default: 90)
#   API_WAIT_S        API health wait seconds (default: 90)
#   LOG_WAIT_S        Log match wait seconds (default: 45)
#   SCHEDULER_RETRIES Scheduler run attempts (default: 2)
#   VERTICAL_ID       Vertical id for trend endpoints (default: 1)
# -----------------------------------------------------------------------------

# disable history expansion (macOS bash/zsh oddities)
{ set +H 2>/dev/null || true; } >/dev/null 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Shared helpers (dc, dc_exec, die, step, etc.)
source "$SCRIPT_DIR/_lib.sh"

# -------------------------------
# Defaults / Options
# -------------------------------
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"  # honored by _lib.sh too
LOGFILE_DEFAULT="sense_full_boot_$(date +%Y%m%d_%H%M%S).log"

NO_DOWN=0
NO_BUILD=0
SKIP_SEED=0
SKIP_SCHEDULER=0
SKIP_TRENDS=0
KEEP_RUNNING=0

LOGFILE="${LOGFILE:-$LOGFILE_DEFAULT}"

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
HEALTH_PATH="${HEALTH_PATH:-/health}"

POSTGRES_WAIT_S="${POSTGRES_WAIT_S:-90}"
API_WAIT_S="${API_WAIT_S:-90}"
LOG_WAIT_S="${LOG_WAIT_S:-45}"
SCHEDULER_RETRIES="${SCHEDULER_RETRIES:-2}"

VERTICAL_ID="${VERTICAL_ID:-1}"

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --no-down           Do not run 'docker compose down -v' (keeps volumes)
  --no-build          Do not rebuild images on 'up'
  --skip-seed         Skip 'make seed'
  --skip-scheduler    Skip 'make scheduler'
  --skip-trends       Skip /trending, /emerging, /declining endpoint checks
  --keep-running      Do not shut down services on success
  --logfile <path>    Write output to this logfile (default: $LOGFILE_DEFAULT)

Env (optional):
  COMPOSE_FILE        Path to compose file (default: infra/docker/docker-compose.yml)
  API_BASE_URL        Base URL for API (default: http://localhost:8000)
  HEALTH_PATH         Health path (default: /health)
  POSTGRES_WAIT_S     Postgres health wait seconds (default: 90)
  API_WAIT_S          API health wait seconds (default: 90)
  LOG_WAIT_S          Log match wait seconds (default: 45)
  SCHEDULER_RETRIES   Scheduler run attempts (default: 2)
  VERTICAL_ID         Vertical id for trend endpoints (default: 1)

Examples:
  $0
  $0 --no-down --no-build
  SKIP_SEED=1 $0
  API_BASE_URL=http://localhost:8000 $0 --logfile /tmp/boot.log
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --no-down)        NO_DOWN=1; shift ;;
    --no-build)       NO_BUILD=1; shift ;;
    --skip-seed)      SKIP_SEED=1; shift ;;
    --skip-scheduler) SKIP_SCHEDULER=1; shift ;;
    --skip-trends)    SKIP_TRENDS=1; shift ;;
    --keep-running)   KEEP_RUNNING=1; shift ;;
    --logfile)
      LOGFILE="${2:-}"
      [ -n "$LOGFILE" ] || die "--logfile requires a path"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1 (use --help)" ;;
  esac
done

# -------------------------------
# Helpers
# -------------------------------
svc_logs() {
  local svc="$1"
  local tail="${2:-200}"
  dc logs --no-color --tail="$tail" "$svc" 2>/dev/null || true
}

wait_http_ok() {
  local url="$1"
  local seconds="${2:-90}"
  local i=1
  while [ "$i" -le "$seconds" ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

wait_log_match() {
  local svc="$1"
  local regex="$2"
  local seconds="${3:-45}"
  local i=1
  while [ "$i" -le "$seconds" ]; do
    if svc_logs "$svc" 800 | grep -E "$regex" >/dev/null 2>&1; then return 0; fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

wait_service_healthy() {
  local svc="$1"
  local seconds="$2"
  local cid
  local i=1
  local status="unknown"

  cid="$(dc ps -q "$svc")"
  [ -n "$cid" ] || die "Could not resolve $svc container id"

  while [ "$i" -le "$seconds" ]; do
    status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$cid" 2>/dev/null || echo "missing")"
    if [ "$status" = "healthy" ] || [ "$status" = "no-healthcheck" ]; then
      echo "✅ $svc OK (status=$status)"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  die "$svc not healthy after ${seconds}s (status=$status)"
}

extract_last_int_from_text() {
  # Reads stdin; extracts last capture group 1 from regex
  local re="$1"
  local out
  out="$(sed -nE "s/.*${re}.*/\\1/p" | tail -n 1 || true)"
  [ -n "${out}" ] || return 1
  printf '%s' "${out}"
}

queues_snapshot() {
  local label="$1"
  if [ -x "$REPO_ROOT/tools/scripts/redis_queues_snapshot.sh" ]; then
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" "$REPO_ROOT/tools/scripts/redis_queues_snapshot.sh" "$label")
  else
    echo "⚠️  Missing tools/scripts/redis_queues_snapshot.sh (skipping queues snapshot)"
  fi
}

print_debug_context() {
  echo
  echo "------------------------------"
  echo "🧯 DEBUG CONTEXT"
  echo "------------------------------"
  echo "--- docker compose ps ---"
  dc ps || true
  echo
  echo "--- docker compose config (first lines) ---"
  dc config 2>/dev/null | head -n 120 || true
  echo
}

run_with_retry() {
  local attempts="$1"
  shift
  local i=1
  while [ "$i" -le "$attempts" ]; do
    if "$@"; then
      return 0
    fi
    echo "⚠️  Attempt $i/$attempts failed: $*"
    i=$((i + 1))
    sleep 3
  done
  return 1
}

on_failure() {
  local code=$?
  echo
  echo "==============================================="
  echo "❌ VALIDATION FAILED (exit=$code)"
  echo "==============================================="
  print_debug_context

  echo
  echo "--- logs: api-gateway ---"
  svc_logs api-gateway 300
  echo
  echo "--- logs: postgres ---"
  svc_logs postgres 300
  echo
  echo "--- logs: redis ---"
  svc_logs redis 200
  echo
  echo "--- logs: ingestion-worker ---"
  svc_logs ingestion-worker 350
  echo
  echo "--- logs: processing-worker ---"
  svc_logs processing-worker 350
  echo
  echo "--- logs: clustering-worker ---"
  svc_logs clustering-worker 350
  echo
  echo "--- logs: trend-worker ---"
  svc_logs trend-worker 350

  echo
  echo "📝 Log written to: $LOGFILE"
  exit "$code"
}

trap on_failure ERR

# -------------------------------
# Main (tee everything)
# -------------------------------
{
  echo "==============================================="
  echo "🧪 SENSE OS FULL STACK VALIDATION"
  echo "🗓️  DATE: $(date)"
  echo "📁 REPO_ROOT: $REPO_ROOT"
  echo "📁 PWD:  $(pwd)"
  echo "🐳 COMPOSE_FILE: $COMPOSE_FILE"
  echo "🌐 API_BASE_URL: $API_BASE_URL"
  echo "==============================================="
  echo

  step "=== 0️⃣  COMPOSE CONFIG (must succeed) ==="
  dc config >/dev/null
  echo "✅ OK"

  step "=== 1️⃣  TREE SNAPSHOT ==="
  if command -v tree >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && tree -a -I "__pycache__|*.pyc|.git|.venv|dist|build|.pytest_cache|.mypy_cache|node_modules")
  else
    echo "⚠️  tree not installed; showing repo root listing:"
    (cd "$REPO_ROOT" && ls -la)
  fi

  if [ "$NO_DOWN" -eq 0 ]; then
    step "=== 2️⃣  DOCKER DOWN (clean volumes) ==="
    dc down -v
    # Ensure stale containers from interrupted runs don't block startup
    for name in \
      docker-api-gateway-1 \
      docker-ingestion-worker-1 \
      docker-processing-worker-1 \
      docker-clustering-worker-1 \
      docker-trend-worker-1; do
      docker rm -f "$name" >/dev/null 2>&1 || true
    done
  else
    step "=== 2️⃣  DOCKER DOWN (skipped) ==="
    echo "ℹ️  --no-down set"
  fi

  step "=== 3️⃣  BOOT CORE SERVICES (postgres + redis) ==="
  dc up -d postgres redis

  step "=== 4️⃣  WAIT FOR POSTGRES HEALTH (up to ${POSTGRES_WAIT_S}s) ==="
  wait_service_healthy postgres "$POSTGRES_WAIT_S"

  step "=== 4️⃣b WAIT FOR REDIS HEALTH (up to ${POSTGRES_WAIT_S}s) ==="
  wait_service_healthy redis "$POSTGRES_WAIT_S"

  step "=== 5️⃣  MIGRATE DB (via Alembic) ==="
  COMPOSE_FILE="$COMPOSE_FILE" "$SCRIPT_DIR/migrate.sh"

  step "=== 6️⃣  BOOT APP SERVICES (api + workers) ==="
  if [ "$NO_BUILD" -eq 1 ]; then
    echo "ℹ️  --no-build set"
    dc up -d
  else
    dc up --build -d
  fi

  step "=== 7️⃣  HEALTH CHECK API (up to ${API_WAIT_S}s) ==="
  HEALTH_URL="${API_BASE_URL}${HEALTH_PATH}"
  if ! wait_http_ok "$HEALTH_URL" "$API_WAIT_S"; then
    svc_logs api-gateway 250
    die "Health check failed after ${API_WAIT_S}s ($HEALTH_URL)"
  fi
  echo "✅ API healthy:"
  curl -fsS "$HEALTH_URL" || true
  echo

  if [ "$SKIP_SEED" -eq 0 ]; then
    step "=== 8️⃣  SEED (make seed) ==="
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make seed)
  else
    step "=== 8️⃣  SEED (skipped) ==="
    echo "ℹ️  --skip-seed set"
  fi

  # -------------------------------
  # Scheduler + queues snapshots
  # -------------------------------
  queues_snapshot "before scheduler"

  if [ "$SKIP_SCHEDULER" -eq 0 ]; then
    step "=== 9️⃣  SCHEDULER (make scheduler-once) ==="
    if ! run_with_retry "$SCHEDULER_RETRIES" bash -lc "cd '$REPO_ROOT' && COMPOSE_FILE='$COMPOSE_FILE' make scheduler"; then
      svc_logs api-gateway 250
      svc_logs ingestion-worker 250
      die "Scheduler failed after ${SCHEDULER_RETRIES} attempts"
    fi
  else
    step "=== 9️⃣  SCHEDULER (skipped) ==="
    echo "ℹ️  --skip-scheduler set"
  fi

  queues_snapshot "after scheduler"

  echo
  echo "⏳ Waiting 5 seconds for workers..."
  sleep 5

  step "=== 🔟 ASSERT PIPELINE DID WORK (logs) ==="

  if ! wait_log_match "ingestion-worker" "inserted=[1-9][0-9]*" "$LOG_WAIT_S"; then
    echo "⚠️  Ingestion did not insert signals yet. Retrying scheduler once..."
    if [ "$SKIP_SCHEDULER" -eq 0 ]; then
      (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) || true
      sleep 4
    fi
    if ! wait_log_match "ingestion-worker" "inserted=[1-9][0-9]*" "$LOG_WAIT_S"; then
      svc_logs ingestion-worker 250
      die "Ingestion did not insert any signals"
    fi
  fi
  echo "✅ Ingestion OK"

  if ! wait_log_match "processing-worker" "Processed .* signals=[0-9]+" "$LOG_WAIT_S"; then
    svc_logs processing-worker 250
    die "Processing did not log any 'Processed ...' line"
  fi

  proc_text="$(svc_logs processing-worker 900)"
  signals_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'Processed .* signals=([0-9]+)' || printf '0')"
  created_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'pain_instances_created=([0-9]+)' || printf '0')"

  if [ "${signals_n}" -eq 0 ] && [ "${created_n}" -eq 0 ]; then
    echo "⚠️  Processing saw 0/0. Re-running scheduler once…"
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) >/dev/null 2>&1 || true
    sleep 4
    proc_text="$(svc_logs processing-worker 900)"
    signals_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'Processed .* signals=([0-9]+)' || printf '0')"
    created_n="$(printf "%s\n" "$proc_text" | extract_last_int_from_text 'pain_instances_created=([0-9]+)' || printf '0')"
  fi

  [ "${signals_n}" -ne 0 ] || [ "${created_n}" -ne 0 ] || die "Processing saw 0 signals and created 0 pain instances"
  echo "✅ Processing OK (signals=${signals_n} created=${created_n})"

  if ! wait_log_match "clustering-worker" "cluster_job" "$LOG_WAIT_S"; then
    echo "⚠️  Clustering did not emit cluster_job yet. Retrying scheduler once..."
    if [ "$SKIP_SCHEDULER" -eq 0 ]; then
      (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" make scheduler) || true
      sleep 4
    fi
    if ! wait_log_match "clustering-worker" "cluster_job" "$LOG_WAIT_S"; then
      svc_logs clustering-worker 250
      die "Clustering did not emit cluster_job"
    fi
  fi
  echo "✅ Clustering OK"

  step "=== 1️⃣0️⃣b TREND (make trend-once) ==="
  (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" DAY="$(date +%F)" make trend-once)

  if ! wait_log_match "trend-worker" "trend_job" "$LOG_WAIT_S"; then
    echo "⚠️  Trend did not emit trend_job yet. Retrying trend-once..."
    (cd "$REPO_ROOT" && COMPOSE_FILE="$COMPOSE_FILE" DAY="$(date +%F)" make trend-once) || true
    sleep 3
    if ! wait_log_match "trend-worker" "trend_job" "$LOG_WAIT_S"; then
      svc_logs trend-worker 250
      die "Trend did not emit trend_job"
    fi
  fi
  echo "✅ Trend OK"

  if [ "$SKIP_TRENDS" -eq 0 ]; then
    step "=== 1️⃣1️⃣ API TRENDS ENDPOINTS (must not 500) ==="
    curl -fsS "${API_BASE_URL}/trending?vertical_id=${VERTICAL_ID}"  >/dev/null || die "GET /trending 500"
    curl -fsS "${API_BASE_URL}/emerging?vertical_id=${VERTICAL_ID}"  >/dev/null || die "GET /emerging 500"
    curl -fsS "${API_BASE_URL}/declining?vertical_id=${VERTICAL_ID}" >/dev/null || die "GET /declining 500"
    echo "✅ Trends endpoints OK"
  else
    step "=== 1️⃣1️⃣ API TRENDS ENDPOINTS (skipped) ==="
    echo "ℹ️  --skip-trends set"
  fi

  echo
  echo "==============================================="
  echo "✅ VALIDATION FINISHED"
  echo "==============================================="

  if [ "$KEEP_RUNNING" -eq 0 ]; then
    step "=== 🧹 CLEANUP (down) ==="
    dc down >/dev/null 2>&1 || true
    echo "✅ Services stopped"
  else
    step "=== 🧷 KEEP RUNNING ==="
    echo "ℹ️  --keep-running set; services left up"
  fi

} 2>&1 | tee "$LOGFILE"

echo
echo "📝 Log written to: $LOGFILE"

```

---

## 29. tools/scripts/verticals_compile.py
<a id="file-29"></a>

- Path: `tools/scripts/verticals_compile.py`
- Size: **20404 bytes**
- Modified: **2026-02-17 13:24:09**
- SHA256: `58234ab812b912e76493cddf415c84f9d3f246e4884cfb202704ae4413b8b78d`

```py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ID_RE = re.compile(r"^[a-z0-9_]+$")
DEFAULT_TAXONOMY_FILE = "taxonomy.json"
FALLBACK_TAXONOMY_FILE = "_taxonomy.json"
INDEX_JSON = "verticals.json"
BULK_TSV_SUFFIX = "_bulk_seed.tsv"
DEFAULT_TIER = "core"
ALLOWED_TIERS = {"core", "experimental", "long_tail"}
META_KEYS = ("audience", "function", "industry", "cluster", "member", "persona", "variant")


def _die(msg: str) -> None:
    raise RuntimeError(msg)


def _read_json(path: Path) -> Any:
    if not path.exists():
        _die(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any, check: bool) -> bool:
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False
    if check:
        return True
    path.write_text(content, encoding="utf-8")
    return True


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _stable_pick(items: List[str], key: str) -> str:
    if not items:
        return ""
    h = int(_sha(key)[:16], 16)
    return items[h % len(items)]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_taxonomy(verticals_dir: Path) -> Dict[str, Any]:
    candidates = [
        verticals_dir / DEFAULT_TAXONOMY_FILE,
        verticals_dir / FALLBACK_TAXONOMY_FILE,
    ]
    tax_path = next((p for p in candidates if p.exists()), None)
    if tax_path is None:
        _die(f"Missing taxonomy file (expected taxonomy.json or _taxonomy.json) in: {verticals_dir}")

    data = _read_json(tax_path)
    if not isinstance(data, dict):
        _die("taxonomy must be a JSON object")

    if int(data.get("schema_version", 0)) < 1:
        _die("taxonomy missing/invalid schema_version")

    if "axes" not in data or "clusters" not in data:
        _die("taxonomy must include axes and clusters")

    rules = data.get("rules", {}) or {}
    gen = (rules.get("generation") or {})
    if "max_generate" not in gen:
        gen["max_generate"] = 20000
    rules["generation"] = gen
    data["rules"] = rules

    engine = data.get("engine", {}) or {}
    engine.setdefault("default_enabled", True)
    engine.setdefault("default_priority_step", 10)
    engine.setdefault("id_prefix", "")
    data["engine"] = engine

    return data


def _iter_axis_ids(tax: Dict[str, Any], axis: str) -> List[str]:
    axes = tax.get("axes", {}) or {}
    items = axes.get(axis) or []
    out: List[str] = []
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            out.append(str(it["id"]))
    return out


def _axis_label_map(tax: Dict[str, Any], axis: str) -> Dict[str, str]:
    axes = tax.get("axes", {}) or {}
    items = axes.get(axis) or []
    out: Dict[str, str] = {}
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            out[str(it["id"])] = str(it.get("label") or it["id"])
    return out


def _persona_map(tax: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p in (tax.get("personas") or []):
        if isinstance(p, dict) and p.get("id"):
            out[str(p["id"])] = p
    return out


def _validate_id(vid: str, max_len: int = 80) -> None:
    if len(vid) > max_len:
        _die(f"id too long ({len(vid)}>{max_len}): {vid}")
    if not ID_RE.match(vid):
        _die(f"invalid id format: {vid}")


@dataclass(frozen=True)
class Member:
    id: str
    label: str
    default_queries: List[str]


def _collect_members(tax: Dict[str, Any]) -> List[Member]:
    members: List[Member] = []
    for c in (tax.get("clusters") or []):
        if not isinstance(c, dict):
            continue
        for m in (c.get("members") or []):
            if not isinstance(m, dict):
                continue
            mid = str(m.get("id") or "").strip()
            if not mid:
                continue
            label = str(m.get("label") or mid)
            dq = m.get("default_queries") or []
            if not isinstance(dq, list):
                dq = []
            dq = [str(x) for x in dq if str(x).strip()]
            members.append(Member(id=mid, label=label, default_queries=dq))
    # stable ordering
    members.sort(key=lambda x: (_sha(x.id), x.id))
    return members


def _build_queries(member: Member, persona_keywords: List[str], suffixes: List[str], max_n: int = 12) -> List[str]:
    # deterministic query builder; avoid YAML colon issues by staying in JSON anyway.
    base: List[str] = []
    base.extend(member.default_queries[:max_n])
    # add deterministic expansions
    kw = [k.strip() for k in persona_keywords if k.strip()]
    seeds = [member.label] + kw[:6]
    out: List[str] = []
    for s in seeds:
        s = s.strip()
        if not s:
            continue
        out.append(s)
        for suf in suffixes:
            out.append(f"{s} {suf}".strip())

    # normalize & unique (case-insensitive)
    seen = set()
    uniq: List[str] = []
    for q in base + out:
        qn = q.strip()
        if not qn:
            continue
        key = qn.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(qn)
        if len(uniq) >= max_n:
            break
    return uniq


def _normalize_tier(value: Any) -> str:
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ALLOWED_TIERS:
            return v
    return DEFAULT_TIER


def _normalize_meta(
    meta: Any,
    axes: Dict[str, Any] | None,
    persona: Any,
) -> Dict[str, Optional[str]]:
    meta_in: Dict[str, Any] = meta if isinstance(meta, dict) else {}
    axes_in: Dict[str, Any] = axes if isinstance(axes, dict) else {}

    merged: Dict[str, Any] = dict(meta_in)
    for key in ("audience", "function", "industry", "cluster", "member", "variant"):
        if merged.get(key) in (None, ""):
            v = axes_in.get(key)
            if v not in (None, ""):
                merged[key] = v
    if merged.get("persona") in (None, "") and persona not in (None, ""):
        merged["persona"] = persona

    out: Dict[str, Optional[str]] = {}
    for key in META_KEYS:
        v = merged.get(key)
        if v is None:
            out[key] = None
            continue
        s = str(v).strip()
        out[key] = s if s else None
    return out


def _make_vertical_doc(
    *,
    vid: str,
    title: str,
    description: str,
    tags: List[str],
    default_queries: List[str],
    persona_id: str,
    axes: Dict[str, str],
    notes: str,
    enabled: bool,
    version: int = 1,
    meta: Optional[Dict[str, Any]] = None,
    tier: str = DEFAULT_TIER,
) -> Dict[str, Any]:
    return {
        "id": vid,
        "name": vid,
        "title": title,
        "description": description,
        "version": version,
        "enabled": enabled,
        "tags": tags,
        "default_queries": default_queries,
        "persona": persona_id,
        "axes": axes,
        "meta": _normalize_meta(meta, axes, persona_id),
        "tier": _normalize_tier(tier),
        "notes": notes,
    }


def _existing_ids(verticals_dir: Path) -> Tuple[List[str], Dict[str, Path]]:
    mapping: Dict[str, Path] = {}
    ids: List[str] = []
    for p in sorted(verticals_dir.glob("*.json")):
        if p.name in (INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE):
            continue
        if p.name.endswith(BULK_TSV_SUFFIX):
            continue
        try:
            d = _read_json(p)
        except Exception:
            # if a file is corrupt, we still want to surface deterministically
            continue
        if isinstance(d, dict):
            vid = str(d.get("id") or d.get("name") or p.stem)
            mapping[vid] = p
            ids.append(vid)
    ids = sorted(set(ids), key=lambda x: (_sha(x), x))
    return ids, mapping


def _candidate_ids(tax: Dict[str, Any], members: List[Member], target: int) -> List[Tuple[str, Dict[str, str], Member]]:
    """
    Deterministic combinator:
    - keep member ids as base
    - generate combinations with axes (audience/function/industry) if present
    - add suffix variants _vN for collisions / scaling
    """
    rules = (tax.get("rules") or {}).get("id_format") or {}
    max_len = int(rules.get("max_len", 80))

    gen = (tax.get("rules") or {}).get("generation") or {}
    max_generate = int(gen.get("max_generate", 20000))
    include_industry = bool(gen.get("include_industry_variants", True))
    suffix_base = str(gen.get("variant_suffix", "_v"))  # like "_v"
    persona_rotation = bool(gen.get("persona_rotation", True))

    audience = _iter_axis_ids(tax, "audience")
    function = _iter_axis_ids(tax, "function")
    industry = _iter_axis_ids(tax, "industry") if include_industry else []

    # base combos (axes order matters for id stability)
    combos: List[Tuple[Dict[str, str], str]] = []
    combos.append(({}, "base"))
    for a in audience:
        combos.append(({"audience": a}, "audience"))
    for f in function:
        combos.append(({"function": f}, "function"))
    if industry:
        for i in industry:
            combos.append(({"industry": i}, "industry"))
    for a in audience:
        for f in function:
            combos.append(({"audience": a, "function": f}, "audience_function"))
    if industry:
        for a in audience:
            for i in industry:
                combos.append(({"audience": a, "industry": i}, "audience_industry"))
        for f in function:
            for i in industry:
                combos.append(({"function": f, "industry": i}, "function_industry"))
        for a in audience:
            for f in function:
                for i in industry:
                    combos.append(({"audience": a, "function": f, "industry": i}, "audience_function_industry"))

    # stable order by hash of combo signature then name
    def _combo_key(x: Tuple[Dict[str, str], str]) -> Tuple[str, str]:
        axes, kind = x
        sig = kind + "|" + "|".join(f"{k}={axes[k]}" for k in sorted(axes.keys()))
        return (_sha(sig), sig)

    combos.sort(key=_combo_key)

    candidates: List[Tuple[str, Dict[str, str], Member]] = []
    prefix = str((tax.get("engine") or {}).get("id_prefix") or "")
    # deterministically generate until max_generate cap
    for m in members:
        for axes, _kind in combos:
            parts: List[str] = []
            if prefix:
                parts.append(prefix)
            # prefer explicit axis ordering for id
            if "audience" in axes:
                parts.append(axes["audience"])
            if "function" in axes:
                parts.append(axes["function"])
            if "industry" in axes:
                parts.append(axes["industry"])
            parts.append(m.id)
            base_id = "_".join(parts)
            base_id = _slug(base_id)
            # validate base id format; if too long we will hash-shorten deterministically
            if len(base_id) > max_len:
                short = base_id[: max(10, max_len - 13)]
                base_id = f"{short}_{_sha(base_id)[:12]}"
            _validate_id(base_id, max_len=max_len)
            candidates.append((base_id, axes, m))

    # de-duplicate base candidates by id (keep first occurrence stable)
    seen = set()
    uniq: List[Tuple[str, Dict[str, str], Member]] = []
    for cid, axes, m in sorted(candidates, key=lambda x: (_sha(x[0] + "|" + json.dumps(x[1], sort_keys=True)), x[0])):
        if cid in seen:
            continue
        seen.add(cid)
        uniq.append((cid, axes, m))

    # If we need more than base ids, expand with suffix variants deterministically.
    if len(uniq) < min(target, max_generate):
        expanded: List[Tuple[str, Dict[str, str], Member]] = uniq[:]
        # cycle variants over uniq base list
        v = 2
        while len(expanded) < min(target, max_generate):
            for cid, axes, m in uniq:
                vid = f"{cid}{suffix_base}{v}"
                if len(vid) > max_len:
                    short = cid[: max(10, max_len - (len(suffix_base) + len(str(v)) + 1 + 12))]
                    vid = f"{short}{suffix_base}{v}_{_sha(cid + str(v))[:12]}"
                vid = _slug(vid)
                if vid in seen:
                    continue
                _validate_id(vid, max_len=max_len)
                seen.add(vid)
                expanded.append((vid, axes, m))
                if len(expanded) >= min(target, max_generate):
                    break
            v += 1
            if v > 99999:
                break
        uniq = expanded

    # hard cap
    uniq = uniq[: min(target, max_generate)]
    return uniq


def compile_verticals(verticals_dir: Path, target: int, prune: bool, check: bool) -> bool:
    _ensure_dir(verticals_dir)
    tax = _load_taxonomy(verticals_dir)
    members = _collect_members(tax)

    if not members:
        _die("taxonomy has no cluster members")

    personas = _persona_map(tax)
    persona_ids = sorted(list(personas.keys()))
    # fall back persona list if taxonomy has none
    if not persona_ids:
        persona_ids = ["general"]

    audience_labels = _axis_label_map(tax, "audience")
    function_labels = _axis_label_map(tax, "function")
    industry_labels = _axis_label_map(tax, "industry")

    engine = tax.get("engine") or {}
    default_enabled = bool(engine.get("default_enabled", True))
    prio_step = int(engine.get("default_priority_step", 10))
    taxonomy_version = str(tax.get("taxonomy_version") or "").strip()
    if not taxonomy_version:
        taxonomy_version = "unknown"

    existing_ids, existing_map = _existing_ids(verticals_dir)
    existing_set = set(existing_ids)

    # choose candidates deterministically
    candidates = _candidate_ids(tax, members, target=target)

    # ensure we can hit target count (existing + new), unless prune is true (then we can shrink)
    if not prune and len(existing_set) > target:
        _die(f"existing verticals ({len(existing_set)}) > target ({target}); use --prune to shrink")
    if not prune:
        needed = target - len(existing_set)
        if needed < 0:
            needed = 0
    else:
        needed = max(0, target)  # will rebuild exactly target

    # Build final id list
    if prune:
        chosen = [c for c in candidates][:target]
        final_ids = [cid for cid, _axes, _m in chosen]
    else:
        # keep existing; fill with new from candidates
        final_ids = list(existing_ids)
        for cid, _axes, _m in candidates:
            if cid in existing_set:
                continue
            final_ids.append(cid)
            if len(final_ids) >= target:
                break

    if len(final_ids) != target:
        _die(f"Not enough unique candidates for target={target}. Got {len(final_ids)}. Expand taxonomy axes/clusters/members.")

    # Write vertical docs for ids that don't exist yet (or if prune, rewrite all deterministically)
    changed = False
    suffixes = ["pain", "bottleneck", "automation", "workflow", "tooling", "process", "best practices"]

    # map candidate -> metadata
    cand_map: Dict[str, Tuple[Dict[str, str], Member]] = {cid: (axes, m) for cid, axes, m in candidates}

    for cid in final_ids:
        axes, m = cand_map.get(cid, ({}, Member(id=cid, label=cid, default_queries=[])))

        # persona rotation: deterministic pick by id hash
        persona_id = _stable_pick(persona_ids, cid) if persona_ids else "general"
        persona_kw = (personas.get(persona_id, {}) or {}).get("keywords") or []
        if not isinstance(persona_kw, list):
            persona_kw = []
        persona_kw = [str(x) for x in persona_kw]

        # labels
        a = axes.get("audience")
        f = axes.get("function")
        i = axes.get("industry")
        parts_title: List[str] = []
        if a:
            parts_title.append(audience_labels.get(a, a).strip())
        if f:
            parts_title.append(function_labels.get(f, f).strip())
        if i:
            parts_title.append(industry_labels.get(i, i).strip())
        parts_title.append(m.label.strip())

        title = " — ".join([p for p in parts_title if p])
        desc_bits: List[str] = []
        if a:
            desc_bits.append(f"{audience_labels.get(a, a)}")
        if f:
            desc_bits.append(f"{function_labels.get(f, f)}")
        if i:
            desc_bits.append(f"{industry_labels.get(i, i)}")
        if not desc_bits:
            desc_bits = ["General"]
        description = f"{', '.join(desc_bits)} pains and workflows around {m.label}."

        tags: List[str] = []
        if a:
            tags.append(a)
        if f:
            tags.append(f)
        if i:
            tags.append(i)
        tags.append(_slug(m.id))

        default_queries = _build_queries(m, persona_kw, suffixes, max_n=12)
        notes = f"Generated deterministically from taxonomy (member={m.id}, persona={persona_id})."

        doc = _make_vertical_doc(
            vid=cid,
            title=title,
            description=description,
            tags=tags,
            default_queries=default_queries,
            persona_id=persona_id,
            axes=axes,
            notes=notes,
            enabled=default_enabled,
            version=1,
        )

        path = verticals_dir / f"{cid}.json"
        if prune or cid not in existing_map:
            changed |= _write_json(path, doc, check=check)

    # Prune extra json files if requested
    if prune:
        keep = set(final_ids) | {INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE}
        for p in sorted(verticals_dir.glob("*.json")):
            if p.name in (INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE):
                continue
            if p.stem not in keep:
                changed = True
                if not check:
                    p.unlink()

    # Write index verticals.json (source-of-truth for API router)
    index_items: List[Dict[str, Any]] = []
    prio = prio_step
    for cid in final_ids:
        meta = None
        tier = None
        doc_path = verticals_dir / f"{cid}.json"
        if doc_path.exists():
            doc = _read_json(doc_path)
            if isinstance(doc, dict):
                meta = _normalize_meta(doc.get("meta"), doc.get("axes"), doc.get("persona"))
                tier = _normalize_tier(doc.get("tier"))
        if meta is None:
            axes, _m = cand_map.get(cid, ({}, Member(id=cid, label=cid, default_queries=[])))
            persona_id = _stable_pick(persona_ids, cid) if persona_ids else "general"
            meta = _normalize_meta(None, axes, persona_id)
        if tier is None:
            tier = DEFAULT_TIER
        index_items.append(
            {
                "id": cid,
                "file": f"{cid}.json",
                "enabled": default_enabled,
                "priority": prio,
                "tier": tier,
                "meta": meta,
                "taxonomy_version": taxonomy_version,
            }
        )
        prio += prio_step

    index_doc = {"taxonomy_version": taxonomy_version, "verticals": index_items}
    changed |= _write_json(verticals_dir / INDEX_JSON, index_doc, check=check)

    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="config/verticals", help="verticals directory")
    ap.add_argument("--target", type=int, default=1000, help="target number of verticals")
    ap.add_argument("--prune", action="store_true", help="delete extra vertical json files to match target exactly")
    ap.add_argument("--check", action="store_true", help="dry-run (no writes), exit non-zero if changes needed")
    args = ap.parse_args()

    verticals_dir = Path(args.dir).resolve()
    changed = compile_verticals(verticals_dir, target=int(args.target), prune=bool(args.prune), check=bool(args.check))

    if args.check and changed:
        _die("verticals_compile: changes required (run without --check)")


if __name__ == "__main__":
    main()

```

---

