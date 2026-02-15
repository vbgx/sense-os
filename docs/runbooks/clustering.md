# Clustering Runbook

## Purpose
Consumes pain instances and creates clusters and cluster-signal links used by the trends pipeline.

## Startup
1. Ensure Postgres and Redis are running via Docker Compose.
2. Start the clustering worker:
`docker compose up -d clustering-worker`

## Inputs
1. `pain_instances` rows must exist for the target vertical.
2. Jobs arrive on the `cluster` queue.

## Triggering Work
1. Use the scheduler to publish a cluster job:
`make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50`

## Logs
1. `docker compose logs -f clustering-worker`
2. Expected logs include `cluster_job` and `clusters_persisted` entries.

## Data Checks
1. Verify clusters:
`select count(*) from pain_clusters where vertical_id=1;`
2. Verify cluster links:
`select count(*) from cluster_signals;`

## Common Failures
1. No pain instances for the day or vertical.
2. Empty vectorization due to missing signal content.

## Validation
1. Run full validation:
`make validate`
