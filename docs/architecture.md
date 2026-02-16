# Architecture

## EPIC 01 — Pain Intelligence V2

### 01.01 — Pain Severity Index
Clusters carry `severity_score` (0–100) computed from frequency/intensity/engagement/specificity.

### 01.02 — Recurrence Detection
Clusters carry `recurrence_score` (0–100) + `recurrence_ratio` (0–1) from multi-user + repeated phrases + time distribution.

### 01.03 — Persona Inference (rule-based v1)
Clusters carry `dominant_persona`, `persona_confidence` (0–1), and `persona_distribution`.

### 01.04 — Monetizability Proxy Score (rule-based v1)
Clusters carry `monetizability_score` (0–100), a proxy for business relevance:
- business/revenue markers
- operational inefficiency markers
- persona weighting (founder/freelancer boosted, hobbyist deboosted)
This is not TAM/pricing/market sizing; it is a stable heuristic for ranking.
