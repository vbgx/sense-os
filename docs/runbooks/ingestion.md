# Ingestion Runbook

## Purpose
Fetches external signals and writes them to the `signals` table.

## Startup
1. Ensure Postgres and Redis are running via Docker Compose.
2. Start the ingestion worker:
`docker compose up -d ingestion-worker`

## Triggering Work
1. Use the scheduler to publish ingest jobs:
`make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50`

## Logs
1. `docker compose logs -f ingestion-worker`
2. Look for `Ingested vertical_id=...` and `Ingestion persisted ...` messages.

## Data Checks
1. Verify signals:
`select count(*) from signals where vertical_id=1;`

## Common Failures
1. Network issues or source rate limits.
2. Missing env vars for database connectivity.

## Validation
1. Full pipeline validation:
`make validate`
