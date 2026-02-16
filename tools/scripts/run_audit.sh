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
  poetry --version || true
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
  for f in Makefile pyproject.toml poetry.lock uv.lock requirements.txt package.json pnpm-lock.yaml turbo.json; do
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
