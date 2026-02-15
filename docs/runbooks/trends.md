# Trends Runbook

## Purpose
Computes daily trend metrics from clusters and exposes trend endpoints.

## Startup
1. Ensure Postgres and Redis are running via Docker Compose.
2. Start the trend worker:
`docker compose up -d trend-worker`

## Triggering Work
1. Run a trend job once:
`make trend-once DAY=$(date +%F)`
2. Scheduler pipeline also publishes trend jobs.

## Logs
1. `docker compose logs -f trend-worker`
2. Look for `trend_job day=... rows=... upserted=...`.

## Data Checks
1. Verify daily metrics:
`select count(*) from cluster_daily_metrics;`

## API Endpoints
1. `GET /trending?vertical_id=1`
2. `GET /emerging?vertical_id=1`
3. `GET /declining?vertical_id=1`

## Common Failures
1. Missing clusters for the day.
2. Inconsistent formula or cluster versions.
