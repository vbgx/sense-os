#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"
SERVICE="${SERVICE:-clustering-worker}"

# Monorepo python paths inside container
PYTHONPATH_IN_CONTAINER="/app/services/clustering_worker/src:/app/packages/queue/src:/app/packages/db/src:/app/packages/domain/src"

docker compose -f "$COMPOSE_FILE" run --rm \
  -e PYTHONPATH="$PYTHONPATH_IN_CONTAINER" \
  "$SERVICE" \
  python -m clustering_worker.main
