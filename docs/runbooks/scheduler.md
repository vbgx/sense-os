# Scheduler Runbook

## Purpose
Plans and publishes ingest, processing, clustering, and trend jobs.

## One-Off Run
1. Run a single vertical pipeline:
`make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50`

## Backfill
1. Run 7-day then 90-day backfill:
`make backfill VERTICAL_ID=1 SOURCE=reddit`
2. Run a custom window:
`docker compose exec api-gateway python -m scheduler.main --mode backfill --start YYYY-MM-DD --end YYYY-MM-DD`

## Logs
1. `docker compose logs -f api-gateway`
2. Look for `published_jobs` and `metric` log lines.

## Checkpoints
1. Scheduler checkpoints are stored in `scheduler_checkpoints`.
2. A failed backfill can be resumed by rerunning the same command.

## Common Failures
1. Missing upstream data for a day (no signals or pains).
2. Database connectivity issues.
