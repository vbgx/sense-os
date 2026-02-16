# Architecture

## Overview

This repository is a monorepo composed of:

- `apps/api_gateway`: HTTP API (FastAPI) exposing read endpoints for verticals, signals, pains, clusters, trends.
- `services/*_worker`: background workers (ingestion, processing, clustering, trend, scheduler).
- `packages/domain`: pure domain logic (models, rules, scoring).
- `packages/db`: SQLAlchemy models, repos, Alembic migrations.
- `packages/queue`: queue client/contracts/idempotency.

## EPIC 01 — Pain Intelligence V2

### Issue 01.01 — Pain Severity Index

Goal: clusters become *measurable strategic objects* by carrying a normalized severity score (0–100).

**Inputs (cluster-level aggregation)**
- Frequency: number of signals in the cluster
- Intensity: negative sentiment magnitude proxy (from per-signal sentiment)
- Engagement: upvotes/comments/replies proxy
- Specificity: text length proxy

**Implementation**
- Domain function: `domain/scoring/pain_severity.py` computes a stable severity index (0–100).
- Persistence: `pain_clusters.severity_score` (DB column, indexed).
- Exposure: API includes `severity_score` on cluster responses.

**Notes**
- Uses log-normalization and caps to keep score stable and avoid domination by outliers.
