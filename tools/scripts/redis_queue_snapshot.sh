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
