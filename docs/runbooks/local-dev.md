# Local Development Runbook

## Prerequisites
1. Docker and Docker Compose.
2. Python 3.12 for local tooling.
3. `make`.

## Quick Start
1. Create an `.env` file from `.env.example` and adjust if needed.
2. Boot and validate the stack:
`make validate`

## Useful Commands
1. Start all services:
`docker compose up -d`
2. Stop all services:
`docker compose down`
3. Run scheduler once:
`make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50`
4. Run trend job once:
`make trend-once DAY=$(date +%F)`

## Tests
1. Run all tests:
`pytest`
2. Run a service test subset:
`pytest services/ingestion_worker/tests`

## Troubleshooting
1. If containers fail to start, run:
`docker compose logs -f`
2. If DB schema is missing, run:
`tools/scripts/migrate_sql.sh`
