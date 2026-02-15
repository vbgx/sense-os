# Sense OS Architecture

## Overview
Sense OS is a batch pipeline that ingests external signals, extracts pain instances, clusters them, and computes trend metrics for API consumers.

## Components
1. API Gateway: FastAPI service providing health, pains, trends, and verticals endpoints.
2. Ingestion Worker: Fetches external signals and writes to `signals`.
3. Processing Worker: Converts signals into `pain_instances`.
4. Clustering Worker: Builds `pain_clusters` and `cluster_signals` links.
5. Trend Worker: Computes `cluster_daily_metrics` and trend scores.
6. Scheduler: Orchestrates job publication and backfills.
7. Redis Queue: Routes jobs between services.
8. Postgres: Primary data store.

## Data Flow
1. Scheduler publishes an `ingest_vertical` job.
2. Ingestion worker inserts `signals`.
3. Scheduler publishes a `process_signals` job.
4. Processing worker inserts `pain_instances`.
5. Scheduler publishes a `cluster_vertical` job.
6. Clustering worker inserts `pain_clusters` and `cluster_signals`.
7. Scheduler publishes a `trend_day` job.
8. Trend worker inserts `cluster_daily_metrics`.
9. API gateway serves `/pains` and `/trending` endpoints.

## Operational Entry Points
1. Full validation: `make validate`
2. Scheduler once: `make scheduler-once`
3. Trend once: `make trend-once`

## Storage
1. Postgres tables are defined in `packages/db/src/db/models.py`.
2. SQL migrations live under `infra/sql`.

## Observability
1. Services log to stdout for Docker aggregation.
2. Key log markers include `published_jobs`, `cluster_job`, and `trend_job`.
