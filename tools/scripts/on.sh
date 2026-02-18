#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.yml}"

echo
echo "🚀 SENSE-OS — LIVE MODE"
echo

# Start stack
echo "▶ Docker up..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo "▶ Waiting services..."
sleep 3

echo "▶ Migrate..."
make migrate

echo "▶ Seed..."
make seed || true

echo
echo "===================================================="
echo "🔥 SYSTEM RUNNING — Press Ctrl+C to stop"
echo "===================================================="
echo

# Run scheduler in background loop
(
  while true; do
    make scheduler-once
    sleep 5
  done
) &

SCHED_PID=$!

# Stream worker logs live
docker compose -f "$COMPOSE_FILE" logs -f \
  ingestion-worker \
  processing-worker \
  clustering-worker \
  trend-worker

# If logs stop, kill scheduler loop
kill "$SCHED_PID" 2>/dev/null || true
