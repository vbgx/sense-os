SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

API_BASE_URL ?= http://localhost:8000

VERTICAL_ID ?= 1
SOURCE ?= reddit
QUERY ?= saas
LIMIT ?= 50

VERTICAL ?= config/verticals/saas_founders.json

VERTICALS_DIR ?= config/verticals
VERTICALS_INDEX ?= $(VERTICALS_DIR)/verticals.json
BATCH ?= 100
SHUFFLE ?= 0
DRY_RUN ?= 0
TIER ?=
PRIORITY_MAX ?=
PRIORITY_MIN ?=

DAY ?=

BACKFILL_DAYS ?= 90
BACKFILL_START ?=
BACKFILL_END ?=
BACKFILL_SERIES ?= 1

LOGFILE ?=
SCRIPTS_DIR := ./tools/scripts

PYTEST ?= pytest -q
RUFF ?= uv run ruff

.DEFAULT_GOAL := help

.PHONY: help ON down ps logs \
	migrate seed seed-and-run \
	scheduler scheduler-once trend-once \
	redis-flush queues \
	lint test contracts ci \
	test-api test-ingestion test-processing test-clustering test-trend test-scheduler \
	lint-api lint-ingestion lint-processing lint-clustering lint-trend lint-scheduler \
	typecheck-web lint-web test-web e2e-web \
	deprecated verticals-validate verticals-compile verticals-check verticals-batch backfill

help:
	@printf "\nSense OS — Commands (LOCAL ONLY)\n\n"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nDefaults:\n"
	@printf "  API_BASE_URL=%s\n" "$(API_BASE_URL)"
	@printf "  VERTICAL_ID=%s SOURCE=%s QUERY=%s LIMIT=%s\n" "$(VERTICAL_ID)" "$(SOURCE)" "$(QUERY)" "$(LIMIT)"
	@printf "\nExamples:\n"
	@printf "  make ON\n"
	@printf "  make seed\n"
	@printf "  make scheduler-once\n"
	@printf "  make down\n\n"

# -----------------------------------------------------------------------------
# 🔥 ONE BUTTON — LIVE MODE (LOCAL)
# -----------------------------------------------------------------------------
ON: ## Live mode (local)
	@chmod +x tools/scripts/on.sh
	@./tools/scripts/on.sh

down: ## Stop local processes + clear queues (local)
	@chmod +x tools/scripts/down.sh
	@./tools/scripts/down.sh

ps: ## Show local worker PIDs (best-effort)
	@pgrep -fl "ingestion_worker/main.py|processing_worker/main.py|clustering_worker/main.py|trend_worker/main.py|api_gateway/main.py" || true

logs: ## Tail last validation log (if any)
	@ls -1t sense_full_boot_*.log 2>/dev/null | head -n 1 | xargs -I{} tail -n 200 -f {} || echo "No log file found."

# -----------------------------------------------------------------------------
# Data / pipeline (LOCAL)
# -----------------------------------------------------------------------------
migrate: ## Alembic migrate (local)
	@$(SCRIPTS_DIR)/migrate.sh

seed: ## Seed verticals (local)
	@$(SCRIPTS_DIR)/seed_verticals.sh

scheduler-once: ## Run scheduler once (LOCAL, 1 vertical)
	@VERTICAL_ID="$(VERTICAL_ID)" VERTICAL="$(VERTICAL)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" OFFSET="$(OFFSET)" DAY="$(DAY)" \
	  $(SCRIPTS_DIR)/run_scheduler_once.sh

trend-once: ## Publish trend job (local)
	@DAY="$(DAY)" $(SCRIPTS_DIR)/publish_trend_job.sh

redis-flush: ## Flush redis queues (local)
	@FORCE=1 $(SCRIPTS_DIR)/flush_redis.sh

queues: ## Redis queues snapshot (local)
	@$(SCRIPTS_DIR)/redis_queues_snapshot.sh "manual"

# -----------------------------------------------------------------------------
# Verticals tools (unchanged)
# -----------------------------------------------------------------------------
verticals-compile:
	@TARGET ?= 1000
	@PRUNE ?= 0
	@CHECK ?= 0
	@args="--dir $(VERTICALS_DIR) --target $(TARGET)"; \
	if [ "$(PRUNE)" = "1" ]; then args="$$args --prune"; fi; \
	if [ "$(CHECK)" = "1" ]; then args="$$args --check"; fi; \
	python tools/scripts/verticals_compile.py $$args

verticals-check:
	@$(PYTEST) tests/test_verticals_taxonomy.py

verticals-batch:
	@VERTICALS_DIR="$(VERTICALS_DIR)" VERTICALS_INDEX="$(VERTICALS_INDEX)" \
	  BATCH="$(BATCH)" SHUFFLE="$(SHUFFLE)" DRY_RUN="$(DRY_RUN)" \
	  TIER="$(TIER)" PRIORITY_MIN="$(PRIORITY_MIN)" PRIORITY_MAX="$(PRIORITY_MAX)" \
	  SOURCE="$(SOURCE)" LIMIT="$(LIMIT)" \
	  python tools/scripts/run_scheduler_batch_from_index.py \
	    --dir "$(VERTICALS_DIR)" \
	    --index "$(VERTICALS_INDEX)" \
	    --batch "$(BATCH)" \
	    --source "$(SOURCE)" \
	    --limit "$(LIMIT)" \
	    $(if $(filter 1,$(SHUFFLE)),--shuffle,) \
	    $(if $(filter 1,$(DRY_RUN)),--dry-run,) \
	    $(if $(TIER),--tier "$(TIER)",) \
	    $(if $(PRIORITY_MIN),--priority-min "$(PRIORITY_MIN)",) \
	    $(if $(PRIORITY_MAX),--priority-max "$(PRIORITY_MAX)",)

backfill:
	@VERTICAL_ID="$(VERTICAL_ID)" SOURCE="$(SOURCE)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" \
	  DAYS="$(BACKFILL_DAYS)" START="$(BACKFILL_START)" END="$(BACKFILL_END)" SERIES="$(BACKFILL_SERIES)" \
	  $(SCRIPTS_DIR)/run_scheduler_backfill.sh

# -----------------------------------------------------------------------------
# Quality gates
# -----------------------------------------------------------------------------
lint:
	@$(MAKE) lint-api
	@$(MAKE) lint-ingestion
	@$(MAKE) lint-processing
	@$(MAKE) lint-clustering
	@$(MAKE) lint-trend
	@$(MAKE) lint-scheduler

test:
	@$(MAKE) test-api
	@$(MAKE) test-ingestion
	@$(MAKE) test-processing
	@$(MAKE) test-clustering
	@$(MAKE) test-trend
	@$(MAKE) test-scheduler

contracts:
	@$(PYTEST) tests/contract/inter_workers

ci:
	@$(SCRIPTS_DIR)/ci_all.sh

test-api:
	@$(PYTEST) apps/api_gateway/tests

test-ingestion:
	@$(PYTEST) services/ingestion_worker/tests

test-processing:
	@$(PYTEST) services/processing_worker/tests

test-clustering:
	@$(PYTEST) services/clustering_worker/tests

test-trend:
	@$(PYTEST) services/trend_worker/tests

test-scheduler:
	@$(PYTEST) services/scheduler/tests

lint-api:
	@$(RUFF) check apps/api_gateway/src apps/api_gateway/tests

lint-ingestion:
	@$(RUFF) check services/ingestion_worker/src services/ingestion_worker/tests

lint-processing:
	@$(RUFF) check services/processing_worker/src services/processing_worker/tests

lint-clustering:
	@$(RUFF) check services/clustering_worker/src services/clustering_worker/tests

lint-trend:
	@$(RUFF) check services/trend_worker/src services/trend_worker/tests

lint-scheduler:
	@$(RUFF) check services/scheduler/src services/scheduler/tests

typecheck-web:
	@cd apps/web && pnpm typecheck

lint-web:
	@cd apps/web && pnpm lint

test-web:
	@cd apps/web && pnpm test

e2e-web:
	@cd apps/web && pnpm playwright test

deprecated:
	@echo "Deprecated docker targets removed (LOCAL ONLY)."

verticals-validate:
	@echo "DEPRECATED: YAML vertical validation removed. Verticals are JSON-only." >&2
	@exit 1
