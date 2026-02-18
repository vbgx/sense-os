# Security & Compliance (Baseline)

This document defines the minimum security and compliance baseline for Sense OS.

## Data collected

Sense OS ingests public signals from external sources (e.g. forums, news, repositories) to detect and score pains.

Stored data may include:
- source name + external id
- title/text excerpt
- URL
- timestamps (created_at / ingested_at)
- derived features (language, spam, quality, scores)

We do not store user passwords. We do not require end-user accounts in the current stage.

## Secrets & configuration

- Secrets are provided **only** via environment variables (never committed).
- Local development uses `.env` files that are gitignored.
- Rotation strategy: update env vars, redeploy containers, invalidate old credentials where possible.

Required secret classes:
- Database DSN
- Redis URL
- External API keys (when applicable)

## Access control

- Database access is restricted to internal services only (compose network / private network).
- Each service should use the minimum privileges required.
- Future hardening: separate DB roles per service and restrict write access by table.

## Network & transport

- External fetches use a fixed User-Agent and polite rate limiting.
- Internal services communicate within the private network.
- Production should enforce TLS at the edge (gateway) and secure DB connections.

## Logging & PII

- Avoid logging full raw texts when possible.
- Never log secrets, tokens, or credentials.
- If PII is encountered in sources, treat it as incidental: minimize retention and avoid indexing PII fields.

## Dependency hygiene

- Dependencies are pinned via lockfiles.
- CI runs lint + tests on each change.
- Future hardening: SBOM generation and dependency scanning.

## Operational safety

- Idempotency keys and deduplication protect against re-processing.
- Retry policies must be bounded (avoid infinite retry loops).
- Queue DLQ mechanisms should be monitored and replayed intentionally.

## Data retention

Baseline:
- Keep raw signals as required for scoring reproducibility.
- Keep derived aggregates (daily metrics) for trend computation.
- Future: configurable TTL per dataset class and per source.

## Incident response (minimal)

If a secret leak is suspected:
1. Rotate secrets immediately.
2. Invalidate compromised tokens/keys at the provider.
3. Audit logs for access patterns.
4. Rebuild and redeploy services.

