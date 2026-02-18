#!/usr/bin/env bash
set -euo pipefail

echo "🧹 stopping local workers (best-effort)..."
pkill -f "services/ingestion_worker/src/ingestion_worker/main.py" 2>/dev/null || true
pkill -f "services/processing_worker/src/processing_worker/main.py" 2>/dev/null || true
pkill -f "services/clustering_worker/src/clustering_worker/main.py" 2>/dev/null || true
pkill -f "services/trend_worker/src/trend_worker/main.py" 2>/dev/null || true
pkill -f "apps/api_gateway/src/api_gateway/main.py" 2>/dev/null || true

echo "🧹 clearing redis queues..."
redis-cli DEL ingest process cluster trend ingest:retry process:retry cluster:retry trend:retry ingest:dlq process:dlq cluster:dlq trend:dlq >/dev/null 2>&1 || true

echo "✅ down (local) done."
