# Queue Runbook

## Purpose
Defines job queues and retry/DLQ behavior for worker pipelines.

## Queues
1. `ingest`
2. `process`
3. `cluster`
4. `trend`

## Retry and DLQ
1. Retry uses a sorted set key: `<queue>:retry`.
2. Dead-letter queue uses a list key: `<queue>:dlq`.
3. Jobs include `_attempt` and error metadata on failure.

## Inspecting Queues
1. Queue length:
`redis-cli llen ingest`
2. Retry size:
`redis-cli zcard ingest:retry`
3. DLQ size:
`redis-cli llen ingest:dlq`
4. Snapshot helper:
`tools/scripts/redis_queues_snapshot.sh`

## Common Failures
1. Jobs stuck in retry due to worker outages.
2. Jobs in DLQ due to repeated failures.

## Recovery
1. Inspect DLQ payloads and requeue if safe:
`redis-cli lrange ingest:dlq 0 10`
