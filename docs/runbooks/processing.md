# Processing Runbook

## Purpose
Processes signals into pain instances and writes to `pain_instances`.

## Startup
1. Ensure Postgres and Redis are running via Docker Compose.
2. Start the processing worker:
`docker compose up -d processing-worker`

## Triggering Work
1. Use the scheduler to publish process jobs:
`make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50`

## Logs
1. `docker compose logs -f processing-worker`
2. Look for `Processed` lines with counts and `pain_instances_created`.

## Data Checks
1. Verify pain instances:
`select count(*) from pain_instances where vertical_id=1;`

## Common Failures
1. No signals available for the target day or vertical.
2. DB connection issues.

## Validation
1. Full pipeline validation:
`make validate`
