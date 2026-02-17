# Architecture

## EPIC 01 — Pain Intelligence V2

Clusters carry:
- severity_score (0–100)
- recurrence_score (0–100) + recurrence_ratio (0–1)
- dominant_persona + persona_confidence + persona_distribution
- monetizability_score (0–100)
- contradiction_score (0–100)

## EPIC 02 — Trend Engine Pro

Clusters additionally carry:
- breakout_score (0–100) — acceleration anomaly
- saturation_score (0–100) — post-peak flattening detection
- opportunity_window_score (0–100) + opportunity_window_status (EARLY/PEAK/SATURATING)
- half_life_days (float | null) — post-peak decay half-life estimate
- competitive_heat_score (0–100) — v0 proxy from mentions of existing solutions/alternatives

Opportunity Window:
- Status is driven by timing (breakout/saturation/momentum).
- Score is mildly penalized when competitive_heat is high (v0 heuristic).
