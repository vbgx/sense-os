from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml

ROOT = Path(__file__).resolve().parents[2]
CFG_DIR = ROOT / "config" / "verticals"
INDEX_PATH_JSON = CFG_DIR / "verticals.json"
INDEX_PATH = INDEX_PATH_JSONdef slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def titleize(s: str) -> str:
    return " ".join(w.capitalize() for w in s.replace("_", " ").split())


def load_index() -> Dict[str, Any]:
    data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    if "verticals" not in data or not isinstance(data["verticals"], list):
        raise RuntimeError("config/verticals/verticals.json must contain a top-level 'verticals:' list")
    return data


def existing_ids(index: Dict[str, Any]) -> set[str]:
    ids = set()
    for v in index["verticals"]:
        if isinstance(v, dict) and "id" in v:
            ids.add(str(v["id"]))

    # also read per-file ids for safety
    for p in CFG_DIR.glob("*.yml"):
        if p.name == "verticals.json" or p.name.endswith("_bulk_seed.tsv"):
            continue
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if isinstance(d, dict) and d.get("id"):
            ids.add(str(d["id"]))
    return ids


def max_priority(index: Dict[str, Any]) -> int:
    prios = []
    for v in index["verticals"]:
        if isinstance(v, dict) and "priority" in v:
            try:
                prios.append(int(v["priority"]))
            except Exception:
                pass
    return max(prios) if prios else 0


def unique_id(base: str, ids: set[str]) -> str:
    """Guarantee uniqueness by suffixing _v2, _v3... if needed."""
    base = slug(base)
    if base not in ids:
        return base
    n = 2
    while True:
        cand = f"{base}_v{n}"
        if cand not in ids:
            return cand
        n += 1


# ------------------------------------------------------------
# Combinatorial catalog (scales to thousands)
# ------------------------------------------------------------

# Dimensions
SEGMENTS = [
    ("b2b", "B2B"),
    ("b2c", "B2C"),
]

FUNCTIONS = [
    ("ops", "Operations", ["ops"]),
    ("dev", "Engineering", ["dev"]),
    ("sales", "Sales", ["sales"]),
    ("marketing", "Marketing", ["marketing"]),
    ("finance", "Finance", ["finance"]),
    ("hr", "HR", ["hr"]),
    ("legal", "Legal", ["legal"]),
    ("security", "Security", ["security"]),
    ("product", "Product", ["product"]),
    ("data", "Data", ["data"]),
]

# Common subdomains (keep generic but combinable)
SUBDOMAINS = {
    "ops": [
        ("procurement", ["procurement", "vendors"]),
        ("logistics", ["logistics", "shipping"]),
        ("inventory", ["inventory", "warehouse"]),
        ("returns", ["returns", "reverse_logistics"]),
        ("support_ops", ["support", "tickets"]),
        ("billing_ops", ["billing", "payments"]),
        ("onboarding_ops", ["onboarding", "training"]),
        ("compliance_ops", ["compliance", "controls"]),
        ("project_delivery", ["delivery", "projects"]),
        ("documentation", ["docs", "knowledge"]),
        ("scheduling", ["scheduling", "field_service"]),
        ("travel_expenses", ["travel", "expenses"]),
        ("risk_ops", ["risk", "controls"]),
        ("privacy_ops", ["privacy", "gdpr"]),
    ],
    "dev": [
        ("ci_cd", ["ci", "build"]),
        ("observability", ["logs", "metrics", "tracing"]),
        ("platform", ["platform", "k8s"]),
        ("api_design", ["api", "contracts"]),
        ("testing", ["tests", "quality"]),
        ("migrations", ["db", "migrations"]),
        ("release", ["release", "deploy"]),
        ("monorepo", ["monorepo", "workspace"]),
        ("sre", ["sre", "reliability"]),
        ("llmops", ["ai", "llmops"]),
        ("security_eng", ["appsec", "secrets"]),
    ],
    "sales": [
        ("prospecting", ["outbound", "personalization"]),
        ("lead_gen", ["leads", "routing"]),
        ("crm_ops", ["crm", "hygiene"]),
        ("deal_desk", ["pricing", "approvals"]),
        ("enablement", ["enablement", "training"]),
        ("renewals", ["renewals", "retention"]),
        ("rev_intel", ["analytics", "pipeline"]),
        ("partners", ["partners", "co_selling"]),
        ("forecasting", ["forecast", "quota"]),
        ("inbound", ["inbound", "speed_to_lead"]),
    ],
    "marketing": [
        ("seo", ["seo", "content"]),
        ("paid_search", ["paid", "search"]),
        ("paid_social", ["paid", "social"]),
        ("content_ops", ["content", "workflow"]),
        ("lifecycle", ["email", "automation"]),
        ("brand_ops", ["brand", "assets"]),
        ("pr", ["pr", "media"]),
        ("events", ["events", "sponsors"]),
        ("community", ["community", "moderation"]),
        ("attribution", ["attribution", "utm"]),
        ("creative_ops", ["creative", "production"]),
        ("webops", ["web", "cms"]),
    ],
    "finance": [
        ("accounts_payable", ["ap", "invoices"]),
        ("accounts_receivable", ["ar", "collections"]),
        ("billing", ["billing", "subscriptions"]),
        ("expense_mgmt", ["expenses", "policy"]),
        ("close_ops", ["close", "checklists"]),
        ("fpna", ["forecast", "variance"]),
        ("revrec", ["revrec", "contracts"]),
        ("treasury", ["cash", "reconciliation"]),
        ("tax_ops", ["tax", "filings"]),
    ],
    "hr": [
        ("recruiting", ["recruiting", "interviews"]),
        ("onboarding", ["onboarding", "access"]),
        ("performance", ["reviews", "calibration"]),
        ("comp_benefits", ["benefits", "eligibility"]),
        ("learning", ["training", "certification"]),
        ("people_analytics", ["people_analytics", "surveys"]),
        ("offboarding", ["offboarding", "assets"]),
        ("hris_ops", ["hris", "workflows"]),
    ],
    "legal": [
        ("contracts", ["contracts", "redlines"]),
        ("legal_intake", ["intake", "triage"]),
        ("privacy", ["privacy", "dsar"]),
        ("policy_mgmt", ["policies", "reviews"]),
        ("risk_mgmt", ["risk", "registry"]),
        ("vendor_contracts", ["vendors", "renewals"]),
        ("compliance", ["audit", "evidence"]),
    ],
    "security": [
        ("iam", ["iam", "access_reviews"]),
        ("vuln_mgmt", ["vuln", "patching"]),
        ("grc", ["soc2", "controls"]),
        ("soc", ["alerts", "triage"]),
        ("secrets", ["secrets", "rotation"]),
        ("endpoint", ["mdm", "devices"]),
        ("appsec", ["sast", "deps"]),
        ("third_party_risk", ["vendor_risk", "questionnaires"]),
        ("incident_response", ["ir", "runbooks"]),
    ],
    "product": [
        ("product_ops", ["release_notes", "stakeholders"]),
        ("user_research", ["research", "recruiting"]),
        ("feedback_ops", ["feedback", "routing"]),
        ("analytics_ops", ["events", "taxonomy"]),
        ("pricing_packaging", ["pricing", "packaging"]),
        ("launch_ops", ["launch", "checklists"]),
        ("spec_quality", ["specs", "handoffs"]),
        ("design_ops", ["design", "assets"]),
    ],
    "data": [
        ("data_quality", ["dq", "freshness"]),
        ("etl_ops", ["pipelines", "orchestration"]),
        ("warehouse_ops", ["warehouse", "cost"]),
        ("lineage", ["lineage", "ownership"]),
        ("governance", ["catalog", "policies"]),
        ("experimentation", ["ab_tests", "analysis"]),
        ("mlops", ["models", "monitoring"]),
        ("feature_store", ["features", "offline_online"]),
    ],
}

# Industries (big multiplier)
INDUSTRIES = [
    ("saas", "SaaS"),
    ("ecommerce", "E-commerce"),
    ("healthcare", "Healthcare"),
    ("fintech", "FinTech"),
    ("real_estate", "Real Estate"),
    ("construction", "Construction"),
    ("manufacturing", "Manufacturing"),
    ("retail", "Retail"),
    ("education", "Education"),
    ("travel", "Travel"),
    ("hospitality", "Hospitality"),
    ("logistics", "Logistics"),
    ("insurance", "Insurance"),
    ("agencies", "Agencies"),
    ("accounting", "Accounting Firms"),
    ("it_services", "IT Services"),
    ("creative_studios", "Creative Studios"),
    ("consulting", "Consulting"),
    ("nonprofits", "Nonprofits"),
    ("media", "Media"),
    ("energy", "Energy"),
]

# Persona templates (varies “personae”)
PERSONA_BY_FUNCTION = {
    "ops": ["Ops Manager", "COO", "Head of Ops", "Operations Analyst"],
    "dev": ["Staff Engineer", "Engineering Manager", "Platform Lead", "CTO"],
    "sales": ["SDR Manager", "VP Sales", "Sales Ops", "RevOps Lead"],
    "marketing": ["Growth Lead", "Demand Gen", "Content Lead", "Head of Marketing"],
    "finance": ["Controller", "Finance Ops", "CFO", "Billing Lead"],
    "hr": ["Head of People", "HR Ops", "Recruiter", "People Partner"],
    "legal": ["Legal Ops", "GC", "Compliance Lead", "Contracts Manager"],
    "security": ["Security Engineer", "GRC Lead", "CISO", "IT Admin"],
    "product": ["PM", "Head of Product", "Product Ops", "Design Lead"],
    "data": ["Data Engineer", "Analytics Lead", "Data PM", "ML Lead"],
}

# Query building
QUERY_PATTERNS = [
    "{industry} {topic}",
    "{topic} workflow {industry}",
    "{topic} best practices",
    "{topic} automation",
    "{topic} pain points",
    "{topic} checklist",
    "{topic} template",
    "{topic} tools",
]

TOPICS_BY_FUNCTION = {
    "ops": ["handoff", "SLA", "standard operating procedure", "routing", "approvals", "exceptions"],
    "dev": ["build pipeline", "deployment failures", "incident", "dependency conflicts", "test flakiness", "api versioning"],
    "sales": ["pipeline hygiene", "prospecting", "lead routing", "deal approvals", "forecast accuracy", "quota attainment"],
    "marketing": ["attribution", "conversion rate", "creative fatigue", "content pipeline", "utm hygiene", "seo audit"],
    "finance": ["invoice disputes", "collections workflow", "month-end close", "expense policy", "subscription billing", "reconciliation"],
    "hr": ["onboarding checklist", "interview scheduling", "performance review", "benefits administration", "offboarding workflow", "survey insights"],
    "legal": ["contract redlines", "renewal tracking", "policy review", "audit evidence", "risk register", "DSAR workflow"],
    "security": ["access reviews", "vulnerability triage", "SOC2 evidence", "incident response", "secret rotation", "vendor risk"],
    "product": ["roadmap prioritization", "user feedback", "event taxonomy", "launch checklist", "spec drift", "pricing packaging"],
    "data": ["data freshness", "schema drift", "pipeline failures", "warehouse cost", "lineage", "ab test analysis"],
}

SOURCES_ROTATION = [
    ["reddit"],
    ["reddit", "hackernews"],
    ["reddit", "indiehackers"],
    ["reddit", "hackernews", "indiehackers"],
    ["reddit", "producthunt"],
]


def make_queries(function: str, industry: str, subdomain_title: str) -> List[str]:
    topics = TOPICS_BY_FUNCTION.get(function, ["workflow", "automation", "pain points"])
    # pick a stable-but-varied subset
    seed = (hash(function + industry + subdomain_title) % 1000)
    picks = []
    for i in range(3):
        picks.append(topics[(seed + i) % len(topics)])
    out = []
    for t in picks:
        for pat in QUERY_PATTERNS[:2]:  # keep short; we only need default_queries(3)
            out.append(pat.format(industry=industry, topic=t))
    # dedup + take 3
    dedup = []
    for q in out:
        q = q.strip()
        if q and q not in dedup:
            dedup.append(q)
    return dedup[:3]


def write_vertical_file(payload: Dict[str, Any]) -> None:
    vid = payload["id"]
    path = CFG_DIR / f"{vid}.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def build_payload(vid: str, seg: str, fn_id: str, fn_title: str, sub_id: str, sub_tags: List[str],
                  ind_id: str, ind_title: str) -> Dict[str, Any]:
    sub_title = titleize(sub_id)
    persona_list = PERSONA_BY_FUNCTION.get(fn_id, ["Operator"])
    persona_role = persona_list[hash(vid) % len(persona_list)]
    sources = SOURCES_ROTATION[hash(vid) % len(SOURCES_ROTATION)]

    tags = [seg, "generated", fn_id, ind_id] + sub_tags
    # unique order + cleanup
    tags2 = []
    for t in tags:
        t = slug(t)
        if t and t not in tags2:
            tags2.append(t)

    default_queries = make_queries(fn_id, ind_title, sub_title)

    return {
        "id": vid,
        "name": vid,  # backward-friendly
        "title": f"{fn_title} — {ind_title} — {sub_title}",
        "description": f"{fn_title} workflows and pain points for {ind_title} ({sub_title}).",
        "version": 1,
        "enabled": True,
        "tags": tags2,
        "default_queries": default_queries,  # MUST exist for compatibility
        "persona": {
            "role": persona_role,
            "segment": seg.upper(),
            "function": fn_title,
            "industry": ind_title,
            "stage": "early" if seg == "b2c" else "growth",
        },
        "ingestion": {
            "sources": [{"name": s, "query": default_queries[0].split()[0], "limit": 80} for s in sources]
        },
        "owner": "generated",
        "notes": "Auto-generated seed vertical. Safe to edit manually.",
    }


def main(target: int = 200) -> None:
    if not INDEX_PATH.exists():
        raise RuntimeError(f"Missing index: {INDEX_PATH}")

    index = load_index()
    ids = existing_ids(index)
    prio = max_priority(index)

    chosen: List[Dict[str, Any]] = []

    # Generate in a deterministic order: segment -> function -> subdomain -> industry
    for seg_id, seg_title in SEGMENTS:
        for fn_id, fn_title, fn_tags in FUNCTIONS:
            subs = SUBDOMAINS.get(fn_id, [])
            for sub_id, sub_tags in subs:
                for ind_id, ind_title in INDUSTRIES:
                    base = f"{seg_id}_{fn_id}_{ind_id}_{sub_id}"
                    vid = unique_id(base, ids)

                    payload = build_payload(
                        vid=vid,
                        seg=seg_id,
                        fn_id=fn_id,
                        fn_title=fn_title,
                        sub_id=sub_id,
                        sub_tags=sub_tags + fn_tags,
                        ind_id=ind_id,
                        ind_title=ind_title,
                    )

                    # If you already have something very close (same base), unique_id will suffix; still ok.
                    chosen.append(payload)
                    ids.add(vid)

                    if len(chosen) >= target:
                        break
                if len(chosen) >= target:
                    break
            if len(chosen) >= target:
                break
        if len(chosen) >= target:
            break

    if len(chosen) < target:
        raise RuntimeError(f"Not enough candidates to add {target} (got {len(chosen)}).")

    # Write files + append to index
    for payload in chosen:
        write_vertical_file(payload)

    for payload in chosen:
        prio += 10
        index["verticals"].append({
            "id": payload["id"],
            "file": f"{payload['id']}.yml",
            "enabled": True,
            "priority": prio,
        })

    INDEX_PATH.write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"Added {len(chosen)} verticals.")
    print(f"Index now: {len(index['verticals'])} entries.")
    print(f"Files now: {len([p for p in CFG_DIR.glob('*.yml') if p.name != 'verticals.json'])} vertical YAMLs.")


if __name__ == "__main__":
    main(200)
