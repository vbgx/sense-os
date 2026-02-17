SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

# ============================================================
# Sense OS — Makefile
# ============================================================

# ----------------------------
# Config (override per command)
# ----------------------------
COMPOSE_FILE ?= infra/docker/docker-compose.yml
API_BASE_URL ?= http://localhost:8000

VERTICAL_ID ?= 1
SOURCE ?= reddit
QUERY ?= saas
LIMIT ?= 50
VERTICAL ?=

# Trend job day (optional). If empty, publish_trend_job.sh may default internally.
DAY ?=

BACKFILL_DAYS ?= 90
BACKFILL_START ?=
BACKFILL_END ?=
BACKFILL_SERIES ?= 1

LOGFILE ?=
SCRIPTS_DIR := ./tools/scripts

.DEFAULT_GOAL := help

.PHONY: help \
	bundle \
	up up-core up-app rebuild down ps \
	logs logs-api logs-postgres logs-redis logs-clustering logs-trend \
	migrate migrate-list migrate-file \
	seed \
	seed-and-run \
	scheduler scheduler-once \
	backfill \
	trend-once \
	redis-flush \
	queues \
	validate validate-log validate-fast validate-keep \
	dev-install ci \
	workers-local \
	deprecated

# ============================================================
# Help
# ============================================================

help: ## Show all commands with usage + current variable defaults
	@printf "\nSense OS — Commands (Makefile)\n\n"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\n"
	@printf "Current defaults:\n"
	@printf "  COMPOSE_FILE=%s\n" "$(COMPOSE_FILE)"
	@printf "  API_BASE_URL=%s\n" "$(API_BASE_URL)"
	@printf "  VERTICAL_ID=%s SOURCE=%s QUERY=%s LIMIT=%s\n" "$(VERTICAL_ID)" "$(SOURCE)" "$(QUERY)" "$(LIMIT)"
	@printf "  VERTICAL=%s\n" "$(VERTICAL)"
	@printf "  DAY=%s\n" "$(DAY)"
	@printf "  BACKFILL_DAYS=%s BACKFILL_START=%s BACKFILL_END=%s BACKFILL_SERIES=%s\n" "$(BACKFILL_DAYS)" "$(BACKFILL_START)" "$(BACKFILL_END)" "$(BACKFILL_SERIES)"
	@printf "\nExamples:\n"
	@printf "  make up\n"
	@printf "  make migrate\n"
	@printf "  make seed\n"
	@printf "  make queues\n"
	@printf "  make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=200\n"
	@printf "  make seed-and-run VERTICAL=config/verticals/saas_founders.yml\n"
	@printf "  make trend-once VERTICAL_ID=1 DAY=2026-02-15\n"
	@printf "  make backfill BACKFILL_SERIES=1\n"
	@printf "  make validate-fast\n\n"

# ============================================================
# Meta / bundle
# ============================================================

bundle: ## Usage: make bundle — Generates a euro-dated Markdown bundle of tools/scripts/* at repo root
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/bundle_scripts.sh

# ============================================================
# Docker lifecycle
# ============================================================

up: ## Usage: make up — Starts full stack (all compose services) detached
	@docker compose -f "$(COMPOSE_FILE)" up -d

up-core: ## Usage: make up-core — Starts only core services (postgres + redis) detached
	@docker compose -f "$(COMPOSE_FILE)" up -d postgres redis

up-app: ## Usage: make up-app — Starts app services (api + workers) detached
	@docker compose -f "$(COMPOSE_FILE)" up -d api-gateway ingestion-worker processing-worker clustering-worker trend-worker

rebuild: ## Usage: make rebuild — Rebuilds images then starts all services detached
	@docker compose -f "$(COMPOSE_FILE)" up --build -d

down: ## Usage: make down — Stops stack and removes containers + volumes (DESTRUCTIVE)
	@docker compose -f "$(COMPOSE_FILE)" down -v

ps: ## Usage: make ps — Shows compose services status
	@docker compose -f "$(COMPOSE_FILE)" ps

# ============================================================
# Logs
# ============================================================

logs: ## Usage: make logs — Follows logs for all services (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200

logs-api: ## Usage: make logs-api — Follows api-gateway logs (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 api-gateway

logs-postgres: ## Usage: make logs-postgres — Follows postgres logs (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 postgres

logs-redis: ## Usage: make logs-redis — Follows redis logs (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 redis

logs-clustering: ## Usage: make logs-clustering — Follows clustering-worker logs (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 clustering-worker

logs-trend: ## Usage: make logs-trend — Follows trend-worker logs (tail=200)
	@docker compose -f "$(COMPOSE_FILE)" logs -f --tail=200 trend-worker

# ============================================================
# DB / migrations
# ============================================================

migrate: ## Usage: make migrate — Alembic upgrade head (single source of truth)
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/migrate.sh

migrate-list: ## Deprecated: legacy SQL migration list (use Alembic)
	@echo "DEPRECATED: legacy SQL migrations moved to (archived legacy SQL). Use Alembic (make migrate)." >&2
	@exit 1

migrate-file: ## Deprecated: legacy SQL migration file (use Alembic)
	@echo "DEPRECATED: legacy SQL migrations moved to (archived legacy SQL). Use Alembic (make migrate)." >&2
	@exit 1

seed: ## Usage: make seed — Seeds verticals via api-gateway container (python -m db.seed)
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/seed_verticals.sh

seed-and-run: ## Usage: make seed-and-run VERTICAL=path/to.yml [SOURCE=reddit LIMIT=50]
	@[ -n "$(VERTICAL)" ] || (echo "ERROR: VERTICAL is required. Example: make seed-and-run VERTICAL=config/verticals/saas_founders.yml" >&2; exit 1)
	@COMPOSE_FILE="$(COMPOSE_FILE)" SOURCE="$(SOURCE)" LIMIT="$(LIMIT)" \
	  $(SCRIPTS_DIR)/seed_and_run_vertical.sh "$(VERTICAL)"

# ============================================================
# Redis queues snapshot
# ============================================================

queues: ## Usage: make queues — Snapshot Redis queues (ingest/process/cluster/trend)
	@COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/redis_queues_snapshot.sh "manual"

# ============================================================
# Scheduler
# ============================================================

scheduler-once: ## Usage: make scheduler-once [VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50] — Runs scheduler once
	@COMPOSE_FILE="$(COMPOSE_FILE)" \
	  VERTICAL_ID="$(VERTICAL_ID)" SOURCE="$(SOURCE)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" \
	  $(SCRIPTS_DIR)/run_scheduler_once.sh

scheduler: scheduler-once ## Alias: runs scheduler once (compat)

# ============================================================
# Backfill
# ============================================================

backfill: ## Usage: make backfill [BACKFILL_DAYS=90] [BACKFILL_START=YYYY-MM-DD] [BACKFILL_END=YYYY-MM-DD] [BACKFILL_SERIES=1]
	@COMPOSE_FILE="$(COMPOSE_FILE)" \
	  VERTICAL_ID="$(VERTICAL_ID)" SOURCE="$(SOURCE)" QUERY="$(QUERY)" LIMIT="$(LIMIT)" \
	  DAYS="$(BACKFILL_DAYS)" START="$(BACKFILL_START)" END="$(BACKFILL_END)" SERIES="$(BACKFILL_SERIES)" \
	  $(SCRIPTS_DIR)/run_scheduler_backfill.sh

# ============================================================
# Trend
# ============================================================

trend-once: ## Usage: make trend-once [VERTICAL_ID=1] [DAY=YYYY-MM-DD] — Publish one trend job
	@COMPOSE_FILE="$(COMPOSE_FILE)" VERTICAL_ID="$(VERTICAL_ID)" DAY="$(DAY)" $(SCRIPTS_DIR)/publish_trend_job.sh

# ============================================================
# Redis
# ============================================================

redis-flush: ## Usage: make redis-flush — FLUSHALL Redis (DESTRUCTIVE)
	@FORCE=1 COMPOSE_FILE="$(COMPOSE_FILE)" $(SCRIPTS_DIR)/flush_redis.sh

# ============================================================
# Validation (end-to-end)
# ============================================================

validate: ## Usage: make validate — Full boot validation
	@echo "==> validate (COMPOSE_FILE=$(COMPOSE_FILE), API_BASE_URL=$(API_BASE_URL))"
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" $(SCRIPTS_DIR)/validate_full_boot.sh

validate-log: ## Usage: make validate-log LOGFILE=/tmp/boot.log — Same as validate, but writes to logfile
	@[ -n "$(LOGFILE)" ] || (echo "ERROR: LOGFILE is required. Example: make validate-log LOGFILE=/tmp/boot.log" >&2; exit 1)
	@echo "==> validate (logfile=$(LOGFILE))"
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" $(SCRIPTS_DIR)/validate_full_boot.sh --logfile "$(LOGFILE)"

validate-fast: ## Usage: make validate-fast — Skips down + build
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" \
	  $(SCRIPTS_DIR)/validate_full_boot.sh --no-down --no-build

validate-keep: ## Usage: make validate-keep — Keeps services running on success
	@COMPOSE_FILE="$(COMPOSE_FILE)" API_BASE_URL="$(API_BASE_URL)" \
	  $(SCRIPTS_DIR)/validate_full_boot.sh --keep-running

# ============================================================
# Local workers (host / .venv)
# ============================================================

workers-local: ## Usage: make workers-local — Prints commands to run local workers
	@echo "Run in separate terminals:"
	@echo "  $(SCRIPTS_DIR)/dev_install.sh"
	@echo "  source .venv/bin/activate"
	@echo "  export POSTGRES_DSN=postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
	@echo "  export REDIS_URL=redis://localhost:6379/0"
	@echo "  # start workers"
	@echo "  $(SCRIPTS_DIR)/run_ingestion_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_processing_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_clustering_worker.sh"
	@echo "  $(SCRIPTS_DIR)/run_trend_worker.sh"

# ============================================================
# Toolchain / CI
# ============================================================

dev-install: ## Usage: make dev-install — Creates .venv and installs editable deps via uv
	@$(SCRIPTS_DIR)/dev_install.sh

ci: ## Usage: make ci — Run checks + tests (requires docker + uv)
	@$(SCRIPTS_DIR)/ci.sh

# ============================================================
# Deprecated / legacy scripts
# ============================================================

deprecated: ## Usage: make deprecated — Shows legacy scripts you should delete/stop using
	@echo "Deprecated:"
	@echo "  - tools/scripts/migrate_sql.sh"
	@echo "  - tools/scripts/migrate_all_sql.sh"
	@echo "  - tools/scripts/patch_makefile_migrate.py (legacy SQL)"
	@echo "  - (archived legacy SQL)/* (do not use)"

verticals-validate: ## Validate YAML in config/verticals
	@python tools/scripts/validate_verticals_yaml.py
