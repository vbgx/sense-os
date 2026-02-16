# Hypothesis Framework Specification — v1

Status: Draft  
Owner: Domain  
Version: 1.0.0  
Related: exploitability_v1.md  

---

## 🎯 Purpose

Define the canonical structure used to transform an investment-grade pain cluster into a structured, comparable business hypothesis.

This is NOT:
- a business plan
- an AI-generated narrative
- speculative content

This IS:
- a deterministic transformation layer
- grounded in cluster metrics
- compatible with VentureOS import format

---

# 🔹 Hypothesis Object — v1

All hypothesis payloads MUST follow this structure.

```json
{
  "cluster_id": "string",
  "target_persona": {},
  "core_pain_statement": "string",
  "why_now": {},
  "suggested_wedge": {},
  "monetization_angle": {},
  "early_validation_path": {},
  "risk_flags": [],
  "opportunity_strength": {},
  "import_payload_for_ventureos": {}
}
1️⃣ Target Persona
Derived from:

persona inference score

recurrence patterns

vertical context

Structure:

{
  "primary_persona": "string",
  "confidence_score": "0-1",
  "supporting_personas": []
}
Rules:

Must be traceable to persona inference logic

No invented personas

Must map to domain/models/persona.py

2️⃣ Core Pain Statement
Structured synthesis of:

cluster summary

top key phrases

severity score

recurrence score

Format:

"Specific actor struggles with X because Y, resulting in Z friction."

Must be:

concrete

falsifiable

non-generic

3️⃣ Why Now (Timing Intelligence)
Derived from:

breakout score

velocity

opportunity window

half-life

trend classification

Structure:

{
  "trend_type": "emerging|declining|stable|breakout",
  "timing_signal_strength": "0-5",
  "window_estimate": "short|medium|long",
  "supporting_metrics": {}
}
4️⃣ Suggested Wedge
Smallest actionable product surface.

Structure:

{
  "wedge_type": "automation|aggregation|workflow|monitoring|tooling",
  "entry_point": "string",
  "why_this_wedge": "string"
}
Constraints:

Must align with pain severity

Must reduce friction in a single step

No platform fantasies

5️⃣ Monetization Angle
Heuristic inference from:

monetizability score

competitive heat

persona type

Structure:

{
  "model": "subscription|usage|transactional|one-off",
  "pricing_power_estimate": "low|medium|high",
  "rationale": "string"
}
6️⃣ Early Validation Path
Must be executable within 14–30 days.

Structure:

{
  "validation_type": "landing|manual_service|scraper|notion_ops|concierge",
  "test_description": "string",
  "success_metric": "string"
}
Must avoid:

building full product

technical overreach

7️⃣ Risk Flags
Array of structured risk objects:

[
  {
    "type": "legal|platform_dependency|saturation|weak_signal",
    "severity": "low|medium|high",
    "reason": "string"
  }
]
Derived from:

competitive heat

contradiction index

signal volume stability

legal keywords

8️⃣ Opportunity Strength
Composite representation of cluster quality.

{
  "pain_score": 0,
  "exploitability_score": 0,
  "confidence_score": 0,
  "tier": "A|B|C|D"
}
Must map to exploitability_v1 scoring.

9️⃣ VentureOS Import Payload
Strict compatibility layer.

{
  "pain_statement": "string",
  "persona": "string",
  "initial_wedge": "string",
  "validation_plan": "string",
  "risk_summary": "string"
}
This payload must be:

minimal

normalized

VentureOS-compatible

🔒 Determinism Rules
No LLM required

All fields must be derivable from cluster + metrics

No hallucinated claims

No market size fantasies

All numeric signals must be traceable

🔁 Versioning Policy
Any breaking structure change requires:

Version bump (v2)

Migration note

Explicit compatibility statement with VentureOS

