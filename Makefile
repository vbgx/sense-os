SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

COMPOSE_FILE ?= infra/docker/docker-compose.yml
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

.PHONY: help bundle ON \
	up up-core up-app rebuild down ps \
	logs logs-api logs-postgres logs-redis logs-clustering logs-trend \
	migrate migrate-list migrate-file \
	seed seed-and-run \
	scheduler scheduler-once \
	verticals-compile verticals-check verticals-batch \
	backfill trend-once redis-flush queues \
	validate validate-log validate-fast validate-keep \
	workers-local dev-install \
	bootstrap ci lint test contracts \
	test-api test-ingestion test-processing test-clustering test-trend test-scheduler \
	lint-api lint-ingestion lint-processing lint-clustering lint-trend lint-scheduler \
	typecheck-web lint-web test-web e2e-web \
	deprecated verticals-validate


help:
	@printf "\nSense OS — Commands (Makefile)\n\n"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\n"
	@printf "Current defaults:\n"
	@printf "  COMPOSE_FILE=%s\n" "$(COMPOSE_FILE)"
	@printf "  API_BASE_URL=%s\n" "$(API_BASE_URL)"
	@printf "  VERTICAL_ID=%s SOURCE=%s QUERY=%s LIMIT=%s\n" "$(VERTICAL_ID)" "$(SOURCE)" "$(QUERY)" "$(LIMIT)"
	@printf "  VERTICAL=%s\n" "$(VERTICAL)"
	@printf "  VERTICALS_DIR=%s\n" "$(VERTICALS_DIR)"
	@printf "  VERTICALS_INDEX=%s\n" "$(VERTICALS_INDEX)"
	@printf "  BATCH=%s SHUFFLE=%s DRY_RUN=%s TIER=%s\n" "$(BATCH)" "$(SHUFFLE)" "$(DRY_RUN)" "$(TIER)"
	@printf "  PRIORITY_MIN=%s PRIORITY_MAX=%s\n" "$(PRIORITY_MIN)" "$(PRIORITY_MAX)"
	@printf "  DAY=%s\n" "$(DAY)"
	@printf "  BACKFILL_DAYS=%s BACKFILL_START=%s BACKFILL_END=%s BACKFILL_SERIES=%s\n" "$(BACKFILL_DAYS)" "$(BACKFILL_START)" "$(BACKFILL_END)" "$(BACKFILL_SERIES)"
	@printf "\nExamples:\n"
	@printf "  make bootstrap\n"
	@printf "  make ci\n"
	@printf "  make up\n"
	@printf "  make migrate\n"
	@printf "  make seed\n"
	@printf "  make validate-fast\n\n"

bundle:
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/bundle_scripts.sh

up:
	@docker compose -f "$(COMPOSE_FILE)" up -d

up-core:
	@docker compose -f "$(COMPOSE_FILE)" up -d postgres redis

up-app:
	@docker compose -f "$(COMPOSE_FILE)" up -d api-gateway ingestion-worker processing-worker clustering-worker trend-worker

rebuild:
	@docker compose -f "$(COMPOSE_FILE)" up --build -d

down:
	@docker compose -f "$(COMPOSE_FILE)" down -v

ps:
	@docker compose -f "$(COMPOSE_FILE)" ps

logs:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200

logs-api:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 api-gateway

logs-postgres:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 postgres

logs-redis:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 redis

logs-clustering:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 clustering-worker

logs-trend:
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 trend-worker

migrate:
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/migrate.sh

migrate-list:
	@echo "DEPRECATED: legacy SQL migrations moved to (archived legacy SQL). Use Alembic (make migrate)." >&2
	@exit 1

migrate-file:
	@echo "DEPRECATED: legacy SQL migrations moved to (archived legacy SQL). Use Alembic (make migrate)." >&2
	@exit 1

seed:
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/seed_verticals.sh

seed-and-run:
	@[ -n "$(VERTICAL)" ] || (echo "ERROR: VERTICAL is required. Example: make seed-and-run VERTICAL=config/verticals/saas_founders.json" >&2; exit 1)
	@COMPOSE_FILE="$(COMPOSE_FILE)" SOURCE="$(SOURCE)" LIMIT="$(LIMIT)" \
	  $(SCRIPTS_DIR)/seed_and_run_vertical.sh "$(VERTICAL)"

queues:
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/redis_queues_snapshot.sh "manual"

scheduler-once:
	@COMPOSE_FILE="$(COMPOSE_FILE)" \
	  VERTICAL_ID="$(VERTICAL_ID)" SOURCE="$(SOURCE)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" \
	  $(SCRIPTS_DIR)/run_scheduler_once.sh

scheduler: scheduler-once

verticals-compile:
	@TARGET ?= 1000
	@PRUNE ?= 0
	@CHECK ?= 0
	@args="--dir $(VERTICALS_DIR) --target $(TARGET)"; \
	if [ "$(PRUNE)" = "1" ]; then args="$$args --prune"; fi; \
	if [ "$(CHECK)" = "1" ]; then args="$$args --check"; fi; \
	python tools/scripts/verticals_compile.py $$args

verticals-check:
	@pytest -q tests/test_verticals_taxonomy.py

verticals-batch:
	@COMPOSE_FILE="$(COMPOSE_FILE)" \
	  VERTICALS_DIR="$(VERTICALS_DIR)" VERTICALS_INDEX="$(VERTICALS_INDEX)" \
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
	@COMPOSE_FILE="$(COMPOSE_FILE)" \
	  VERTICAL_ID="$(VERTICAL_ID)" SOURCE="$(SOURCE)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" \
	  DAYS="$(BACKFILL_DAYS)" START="$(BACKFILL_START)" END="$(BACKFILL_END)" SERIES="$(BACKFILL_SERIES)" \
	  $(SCRIPTS_DIR)/run_scheduler_backfill.sh

trend-once:
	@COMPOSE_FILE="$(COMPOSE_FILE)" VERTICAL_ID="$(VERTICAL_ID)" DAY="$(DAY)" $(SCRIPTS_DIR)/publish_trend_job.sh

redis-flush:
	@FORCE=1 COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/flush_redis.sh

validate:
	@echo "==> validate (COMPOSE_FILE=$(COMPOSE_FILE), API_BASE_URL=$(API_BASE_URL))"
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" $(SCRIPTS_DIR)/validate_full_boot.sh

validate-log:
	@[ -n "$(LOGFILE)" ] || (echo "ERROR: LOGFILE is required. Example: make validate-log LOGFILE=/tmp/boot.log" >&2; exit 1)
	@echo "==> validate (logfile=$(LOGFILE))"
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" $(SCRIPTS_DIR)/validate_full_boot.sh --logfile "$(LOGFILE)"

validate-fast:
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" \
	  $(SCRIPTS_DIR)/validate_full_boot.sh --no-down --no-build

validate-keep:
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" \
	  $(SCRIPTS_DIR)/validate_full_boot.sh --keep-running

workers-local:
	@echo "Run in separate terminals:"
	@echo "  $(SCRIPTS_DIR)/dev_install.sh"
	@echo "  source .venv/bin/activate"
	@echo "  export POSTGRES_DSN=postgresql+psycopg://20 20 12 61 79 80 81 98 701 33 100 204 250 395 398 399 400whoami)@localhost:5432/sense\n  export DATABASE_URL=\"
	@echo "  export REDIS_URL=redis://localhost:6379/0"
	@echo "  $(SCRIPTS_DIR)/run_ingestion_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_processing_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_clustering_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_trend_worker.sh"

dev-install:
	@$(SCRIPTS_DIR)/dev_install.sh

bootstrap:
	@$(SCRIPTS_DIR)/bootstrap.sh

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
	@echo "Deprecated:"
	@echo "  - tools/scripts/migrate_sql.sh"
	@echo "  - tools/scripts/migrate_all_sql.sh"
	@echo "  - tools/scripts/patch_makefile_migrate.py (legacy SQL)"
	@echo "  - (archived legacy SQL)/* (do not use)"

verticals-validate:
	@echo "DEPRECATED: YAML vertical validation removed. Verticals are JSON-only." >&2
	@exit 1

# -----------------------------------------------------------------------------
# 🔥 ONE BUTTON — PERMANENT LIVE MODE
# -----------------------------------------------------------------------------
ON:
	@chmod +x tools/scripts/on.sh
	@./tools/scripts/on.sh