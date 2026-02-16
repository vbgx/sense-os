# VentureOS Export Payload — v1

Status: Draft  
Owner: API / Insights  
Version: 1.0.0  
Related: hypothesis_v1.md  

---

## 🎯 Purpose

Define the canonical, versioned JSON payload exported by Sense and directly importable into VentureOS.

This payload must be:

- Deterministic  
- Fully derived from existing cluster metrics  
- Stable across runs  
- Versioned  
- Importable without manual transformation  

This is **not** a presentation layer.  
This is a strict integration contract.

---

## 📡 Endpoint

GET `/insights/{cluster_id}/export`

---

## 📦 Canonical Payload Structure — v1

```json
{
  "export_version": "ventureos_export_v1",
  "hypothesis_id": "string",
  "persona": "string",
  "pain": "string",
  "wedge": "string",
  "monetization": "string",
  "validation_plan": [
    "string",
    "string",
    "string"
  ],
  "opportunity_score": 0,
  "timing_status": "emerging|stable|declining|breakout",
  "risks": [
    "string"
  ]
}
🔹 Field Definitions
export_version
Constant string identifying payload schema version.

Current value:

ventureos_export_v1

Must not change within v1.

hypothesis_id
Deterministic ID derived from:

cluster_id

export_version

Must:

Be stable across runs

Not depend on timestamps

Not depend on random values

persona
Derived from Target Persona Generator (Issue 06.02)

Constraints:

Specific

Non-generic

No “business owner”

Deterministic

pain
Derived from Core Pain Statement Generator (Issue 06.03)

Must follow strict format:

"[Persona] struggle with [pain] because [root cause]"

No narrative variation allowed.

wedge
Derived from Suggested Wedge Generator (Issue 06.04)

Constraints:

Specific micro-angle

Persona-aligned

No “Build SaaS”

No generic phrasing

monetization
Derived from Monetization Angle Generator (Issue 06.05)

Allowed values:

subscription

usage-based

per-seat

premium add-on

api-based

one-off

Must match deterministic mapping logic.

validation_plan
Derived from Early Validation Path Generator (Issue 06.06)

Constraints:

Exactly 3 steps

Actionable in < 1 week

Persona-specific

No vague wording

opportunity_score
Numeric scalar (int).

Derived from existing cluster metrics:

exploitability_score

severity_score

recurrence_score

monetizability_score

Must not introduce new scoring logic.

Recommended range:

0–100 (normalized).

timing_status
Derived strictly from:

trend classification

breakout_score

opportunity_window_status

Allowed values:

emerging

stable

declining

breakout

No interpretation layer allowed.

risks
Derived from Risk Flags Aggregator (Issue 06.07)

Must:

Reflect only existing metrics

Be direct and explicit

Avoid vague language

Examples:

"High competition density"

"Trend showing early saturation"

"Low cluster confidence"

🔒 Determinism Rules
The export payload must:

Contain no generated randomness

Contain no timestamps

Contain no LLM content

Be reproducible from cluster state alone

Be stable across identical DB states

If cluster data does not change, the payload must not change.

🔁 Versioning Policy
Any structural modification requires:

New version (ventureos_export_v2)

Backward compatibility statement

Explicit migration documentation

Breaking changes are not allowed within v1.

🚀 Strategic Role
This payload bridges:

Sense → Opportunity Detection
VentureOS → Venture Decision Engine

It transforms:

Investment-grade cluster
→ Structured venture bet
→ Comparable decision object

