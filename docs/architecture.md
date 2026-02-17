# Architecture --- Sense-OS

## Overview

Sense-OS is a distributed market intelligence engine that transforms raw
community signals into ranked, explainable market opportunities.

The system is built around a strict separation of concerns:

1.  Signal Ingestion\
2.  Signal Processing\
3.  Pain Clustering\
4.  Trend Computation\
5.  Insight Surface (API)

The architecture enforces:

-   Deterministic scoring\
-   Idempotent workers\
-   Versioned domain logic\
-   No infrastructure leakage into domain\
-   Explainability at cluster level

------------------------------------------------------------------------

## System Flow

    External Sources
        ↓
    Ingestion Worker
        ↓
    Processing Worker
        ↓
    Clustering Worker
        ↓
    Trend Worker
        ↓
    Insight API

Each stage persists intermediate artifacts in PostgreSQL.

Redis is used for asynchronous orchestration.

------------------------------------------------------------------------

## Architectural Layers

### 1. Domain Layer (`packages/domain`)

Pure, deterministic logic.

Contains:

-   Pain scoring models\
-   Trend computation logic\
-   Exploitability formulas\
-   Competitive & saturation proxies\
-   Persona inference\
-   Risk flags\
-   Export payload builders

Constraints:

-   No DB imports\
-   No network calls\
-   Versioned scoring logic\
-   Fully unit-tested

This is the intelligence core.

------------------------------------------------------------------------

### 2. Application Layer (`packages/application`)

Orchestrates domain use-cases.

Responsible for:

-   Building cluster detail views\
-   Constructing insight payloads\
-   Aggregating cluster metrics\
-   Export formatting

No infrastructure logic inside.

------------------------------------------------------------------------

### 3. Infrastructure Layer

#### Workers (`services/`)

Each worker has a single responsibility:

**Ingestion Worker** - Fetches signals\
- Normalizes data\
- Applies spam and quality scoring\
- Applies freshness decay

**Processing Worker** - Extracts features\
- Computes initial pain signals

**Clustering Worker** - TF-IDF vectorization\
- Threshold clustering\
- Key phrase extraction\
- Representative signal selection\
- Persona inference\
- Pain severity & recurrence computation

**Trend Worker** - Velocity computation\
- Breakout detection\
- Declining detection\
- Half-life estimation\
- Opportunity window classification\
- Competitive heat scoring

**Scheduler** - Orchestrates jobs\
- Ensures idempotent processing\
- Maintains checkpoints

------------------------------------------------------------------------

## Cluster Intelligence Model

Clusters are the central intelligence unit.

Each cluster aggregates structural, timing and competitive metrics.

### Core Pain Intelligence

Clusters carry:

-   `severity_score` (0--100)\
-   `recurrence_score` (0--100)\
-   `recurrence_ratio` (0--1)\
-   `dominant_persona`\
-   `persona_confidence`\
-   `persona_distribution`\
-   `monetizability_score` (0--100)\
-   `contradiction_score` (0--100)\
-   `confidence_score` (0--100)

------------------------------------------------------------------------

### Trend Intelligence

Clusters additionally carry:

-   `breakout_score` (0--100)\
    Acceleration anomaly detection.

-   `saturation_score` (0--100)\
    Post-peak flattening detection.

-   `opportunity_window_score` (0--100)

-   `opportunity_window_status`\
    `EARLY | PEAK | SATURATING`

-   `half_life_days` (float \| null)\
    Post-peak decay half-life estimate.

-   `velocity_growth`\
    Relative week-over-week acceleration.

------------------------------------------------------------------------

### Competitive & Saturation Proxies

Clusters include competitive context:

-   `competitive_heat_score` (0--100)\
    Proxy derived from mentions of existing tools and alternatives.

-   `repo_density_score`\

-   `producthunt_overlap_score`\

-   `keyword_saturation_score`\

-   `external_solution_density_score`

------------------------------------------------------------------------

## Opportunity Window Logic

Opportunity window is driven by timing metrics:

-   Breakout strength\
-   Momentum\
-   Saturation level

Status rules:

**EARLY** - High breakout\
- Low saturation\
- Positive acceleration

**PEAK** - Strong velocity\
- Rising saturation

**SATURATING** - Declining acceleration\
- High competitive heat

The opportunity window score is mildly penalized when competitive heat
is high (v0 heuristic).

------------------------------------------------------------------------

## Exploitability Engine

Exploitability is a composite decision metric:

    Exploitability =
    Severity × Growth × Recurrence × Monetizability × Underserved × Confidence

Each component is normalized to 0--100.

Exploitability is versioned and deterministic.

Clusters are ranked into decision tiers.

------------------------------------------------------------------------

## Determinism & Versioning

All scoring algorithms are:

-   Versioned\
-   Pure\
-   Reproducible

Domain logic changes require:

-   Explicit version bump\
-   Test coverage\
-   Backward compatibility review

This ensures drift control and auditability.

------------------------------------------------------------------------

## Data Integrity Principles

Sense-OS enforces:

-   Idempotent job execution\
-   Double-consume protection\
-   Dead-letter replay validation\
-   Contract tests on API payloads\
-   No DB access from API layer without repository abstraction

------------------------------------------------------------------------

## Insight Surface

The API exposes structured decision endpoints:

-   `/insights/top_pains`
-   `/insights/emerging_opportunities`
-   `/insights/declining_risks`
-   `/insights/{cluster_id}`
-   `/insights/{cluster_id}/export`

The API does not expose raw noise.

It exposes ranked intelligence.

------------------------------------------------------------------------

## Non-Goals

Sense-OS does not:

-   Generate business plans\
-   Execute validation strategies\
-   Provide idea generation\
-   Replace strategic decision tools

It is strictly a sensing and ranking engine.
