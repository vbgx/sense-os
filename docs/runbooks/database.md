# Database Runbook

## Purpose
Defines schema, migrations, and connectivity for Postgres and test databases.

## Migrations
1. SQL migrations (used by validate script):
`tools/scripts/migrate_sql.sh`
2. Legacy SQL migration shortcut:
`tools/scripts/migrate.sh`

## Connection Settings
1. `POSTGRES_DSN` or `DATABASE_URL` for runtime.
2. Default local fallback is `postgresql+psycopg://postgres:postgres@localhost:5432/postgres`.

## Schema Initialization
1. The API and services call `db.init_db.init_db()` on startup to ensure tables exist.
2. Tests use SQLite and create tables via SQLAlchemy metadata.

## Common Tasks
1. Reset local Docker DB:
`docker compose down -v`
2. Apply migrations:
`tools/scripts/migrate_sql.sh`

## Troubleshooting
1. Connection failures: verify `POSTGRES_DSN` and Postgres health.
2. Missing columns: ensure latest SQL files were applied.
