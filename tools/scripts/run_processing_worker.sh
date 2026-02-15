#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
SERVICE="${SERVICE:-processing-worker}"

PYTHONPATH_IN_CONTAINER="/app/services/processing_worker/src:/app/packages/queue/src:/app/packages/db/src:/app/packages/domain/src"

docker compose -f "$COMPOSE_FILE" run --rm \
  -e PYTHONPATH="$PYTHONPATH_IN_CONTAINER" \
  "$SERVICE" \
  python -m processing_worker.main
