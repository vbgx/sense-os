#!/usr/bin/env bash
set -e

echo "🐍 Creating venv..."
python3.12 -m venv .venv

source .venv/bin/activate

echo "⬆ Upgrading pip..."
pip install -U pip

echo "📦 Installing core packages..."
pip install -e packages/application
pip install -e packages/db
pip install -e packages/domain
pip install -e packages/queue

echo "📦 Installing services..."
pip install -e services/ingestion_worker
pip install -e services/processing_worker
pip install -e services/clustering_worker
pip install -e services/trend_worker
pip install -e services/scheduler

echo "📦 Installing API..."
pip install -e apps/api_gateway

echo
echo "✅ Local environment ready."
echo "👉 Activate with: source .venv/bin/activate"
