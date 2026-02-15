# API Runbook

## Purpose
The API gateway serves read-only endpoints for pains, trends, and verticals and provides a health check for orchestration.

## Startup
1. Ensure Postgres and Redis are running via Docker Compose.
2. Start the API service:
`docker compose up -d api-gateway`

## Health Check
1. Confirm the service is reachable:
`curl -fsS http://localhost:8000/health`
2. Expected response:
`{"status":"ok"}`

## Key Endpoints
1. `GET /pains?vertical_id=1&limit=10&offset=0`
2. `GET /pains/{id}`
3. `GET /trending?vertical_id=1`
4. `GET /emerging?vertical_id=1`
5. `GET /declining?vertical_id=1`

## Environment
1. `POSTGRES_DSN` or `DATABASE_URL`
2. `REDIS_URL`

## Logs
1. `docker compose logs -f api-gateway`
2. Look for FastAPI startup and request logs.

## Common Failures
1. `500` responses typically indicate missing migrations or empty upstream tables.
2. `422` on `/pains` usually means `vertical_id` was omitted.

## Validation
1. Run the full stack validation:
`make validate`
