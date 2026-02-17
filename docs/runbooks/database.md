# Database Runbook

## Purpose
Defines schema, migrations, and connectivity for Postgres and test databases.

## Migrations
1. Alembic migrations (single source of truth):
`tools/scripts/migrate.sh`
2. Legacy SQL migrations (deprecated):
`docs/archive/legacy_sql/`

## Connection Settings
1. `POSTGRES_DSN` or `DATABASE_URL` for runtime.
2. Default local fallback is `postgresql+psycopg://postgres:postgres@localhost:5432/postgres`.

## Schema Initialization
1. The API and services call `db.init_db.init_db()` on startup to wait for DB connectivity only.
2. Schema is created by Alembic migrations.

## Common Tasks
1. Reset local Docker DB:
`docker compose down -v`
2. Apply migrations:
`tools/scripts/migrate.sh`

## Troubleshooting
1. Connection failures: verify `POSTGRES_DSN` and Postgres health.
2. Missing columns: ensure latest Alembic migrations were applied.
