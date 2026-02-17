from __future__ import annotations

import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]  # repo root
VERT_DIR = ROOT / "config" / "verticals"
INDEX_PATH_JSON = VERT_DIR / "verticals.json"
INDEX_PATH = INDEX_PATH_JSON# --- A BIG CATALOG YOU CAN EXTEND ---
CATALOG: dict[str, dict] = {
    # B2B / Ops
    "finance_ops": {
        "title": "Finance Ops",
        "description": "Billing, invoicing, cashflow, reporting, closing.",
        "tags": ["b2b", "ops", "finance"],
        "default_queries": [
            "invoice automation",
            "accounts payable workflow",
            "month end close pain",
            "reconciliation takes too long",
        ],
        "ingestion": [
            ("reddit", "accounts payable automation", 80),
            ("reddit", "invoice approval workflow", 80),
            ("hackernews", "billing", 80),
            ("indiehackers", "invoicing", 80),
        ],
    },
    "hr_ops": {
        "title": "HR Ops",
        "description": "Hiring, onboarding, payroll ops, HRIS pain points.",
        "tags": ["b2b", "ops", "hr"],
        "default_queries": [
            "onboarding checklist automation",
            "HRIS integration pain",
            "payroll errors",
            "time off policy tracking",
        ],
        "ingestion": [
            ("reddit", "HRIS", 80),
            ("reddit", "onboarding process", 80),
            ("hackernews", "HR software", 80),
            ("indiehackers", "hiring workflow", 80),
        ],
    },
    "revops": {
        "title": "RevOps",
        "description": "CRM hygiene, pipeline, attribution, handoffs, SLAs.",
        "tags": ["b2b", "ops", "sales"],
        "default_queries": [
            "CRM data quality pain",
            "salesforce admin backlog",
            "lead routing broken",
            "attribution mismatch",
        ],
        "ingestion": [
            ("reddit", "revops", 80),
            ("reddit", "lead routing", 80),
            ("hackernews", "CRM", 80),
            ("indiehackers", "pipeline management", 80),
        ],
    },

    # Dev / Engineering
    "platform_engineering": {
        "title": "Platform Engineering",
        "description": "DevEx, internal tools, CI/CD, golden paths.",
        "tags": ["b2b", "dev", "engineering"],
        "default_queries": [
            "developer experience pain",
            "CI is flaky",
            "slow build pipeline",
            "internal tooling backlog",
        ],
        "ingestion": [
            ("reddit", "platform engineering", 80),
            ("reddit", "CI flaky", 80),
            ("hackernews", "developer productivity", 80),
            ("indiehackers", "devtools", 80),
        ],
    },
    "security_compliance": {
        "title": "Security & Compliance",
        "description": "SOC2, ISO, vendor reviews, access reviews, policies.",
        "tags": ["b2b", "dev", "security"],
        "default_queries": [
            "SOC2 vendor questionnaire pain",
            "access review process",
            "security policy automation",
            "GRC tooling",
        ],
        "ingestion": [
            ("reddit", "SOC2", 80),
            ("reddit", "vendor security review", 80),
            ("hackernews", "security compliance", 80),
            ("indiehackers", "SOC2", 80),
        ],
    },

    # Sales
    "sales_outbound": {
        "title": "Sales Outbound",
        "description": "Prospecting, personalization, deliverability, sequences.",
        "tags": ["b2b", "sales", "outbound"],
        "default_queries": [
            "cold email deliverability",
            "prospecting list building",
            "personalization at scale",
            "sequence reply rate low",
        ],
        "ingestion": [
            ("reddit", "cold email deliverability", 80),
            ("reddit", "outbound sales tools", 80),
            ("hackernews", "sales automation", 80),
            ("indiehackers", "cold email", 80),
        ],
    },
    "sales_support": {
        "title": "Sales Support",
        "description": "Proposals, pricing approvals, CPQ, handoffs.",
        "tags": ["b2b", "sales", "ops"],
        "default_queries": [
            "proposal workflow",
            "pricing approvals slow",
            "quote to cash pain",
            "CPQ implementation",
        ],
        "ingestion": [
            ("reddit", "CPQ", 80),
            ("reddit", "quote to cash", 80),
            ("hackernews", "pricing", 80),
            ("indiehackers", "proposals", 80),
        ],
    },

    # Marketing
    "marketing_seo": {
        "title": "Marketing SEO",
        "description": "Content ops, keyword research, internal linking, refresh.",
        "tags": ["b2b", "marketing", "seo"],
        "default_queries": [
            "content refresh workflow",
            "internal linking automation",
            "keyword clustering pain",
            "SEO reporting takes too long",
        ],
        "ingestion": [
            ("reddit", "SEO workflow", 80),
            ("reddit", "content refresh", 80),
            ("hackernews", "SEO tools", 80),
            ("indiehackers", "SEO", 80),
        ],
    },
    "marketing_paid_social": {
        "title": "Paid Social",
        "description": "Creative testing, attribution, ROAS volatility.",
        "tags": ["b2b", "marketing", "paid"],
        "default_queries": [
            "creative testing workflow",
            "ROAS dropped suddenly",
            "attribution iOS changes",
            "ad account banned",
        ],
        "ingestion": [
            ("reddit", "facebook ads ROAS", 80),
            ("reddit", "creative testing", 80),
            ("hackernews", "adtech", 80),
            ("indiehackers", "paid ads", 80),
        ],
    },

    # B2C
    "personal_finance_b2c": {
        "title": "Personal Finance (B2C)",
        "description": "Budgeting, subscriptions, saving, spending insights.",
        "tags": ["b2c", "finance"],
        "default_queries": [
            "track subscriptions app",
            "budgeting app frustration",
            "save money challenge",
            "expense categorization wrong",
        ],
        "ingestion": [
            ("reddit", "budgeting app", 80),
            ("reddit", "subscription tracker", 80),
            ("hackernews", "personal finance app", 80),
            ("indiehackers", "consumer finance", 80),
        ],
    },
    "fitness_habits_b2c": {
        "title": "Fitness & Habits (B2C)",
        "description": "Habit tracking, coaching, adherence, routines.",
        "tags": ["b2c", "health", "habits"],
        "default_queries": [
            "habit tracker not working",
            "gym routine planning app",
            "motivation to exercise",
            "nutrition tracking pain",
        ],
        "ingestion": [
            ("reddit", "habit tracking app", 80),
            ("reddit", "workout planning app", 80),
            ("hackernews", "fitness app", 80),
            ("indiehackers", "habit app", 80),
        ],
    },
}

def load_index() -> dict:
    if INDEX_PATH.exists():
        return yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {"verticals": []}
    return {"verticals": []}

def save_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def next_priority(index: dict) -> int:
    items = index.get("verticals") or []
    if not items:
        return 10
    return max(int(v.get("priority", 0) or 0) for v in items) + 10

def ensure_vertical_file(vid: str, spec: dict) -> None:
    path = VERT_DIR / f"{vid}.yml"
    if path.exists():
        return
    ingestion = [{"name": n, "query": q, "limit": int(l)} for (n, q, l) in (spec.get("ingestion") or [])]
    data = {
        "id": vid,
        "name": vid,
        "title": spec.get("title", vid.replace("_", " ").title()),
        "description": spec.get("description", ""),
        "version": 1,
        "enabled": True,
        "tags": spec.get("tags", []),
        "default_queries": spec.get("default_queries", []),
    }
    if ingestion:
        data["ingestion"] = {"sources": ingestion}
    save_yaml(path, data)

def ensure_index_entry(index: dict, vid: str, prio: int) -> None:
    items = index.setdefault("verticals", [])
    if any(v.get("id") == vid for v in items):
        return
    items.append({"id": vid, "file": f"{vid}.yml", "enabled": True, "priority": prio})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="Generate all verticals from catalog")
    ap.add_argument("--ids", nargs="*", default=[], help="Generate only these ids")
    args = ap.parse_args()

    VERT_DIR.mkdir(parents=True, exist_ok=True)

    index = load_index()
    prio = next_priority(index)

    if args.all:
        ids = list(CATALOG.keys())
    else:
        ids = args.ids

    if not ids:
        print("No ids provided. Use --all or --ids ...")
        raise SystemExit(2)

    created = 0
    for vid in ids:
        if vid not in CATALOG:
            print(f"Unknown id: {vid} (add it to CATALOG in tools/scripts/gen_verticals.py)")
            continue
        ensure_vertical_file(vid, CATALOG[vid])
        ensure_index_entry(index, vid, prio)
        prio += 10
        created += 1

    save_yaml(INDEX_PATH, index)
    print(f"done. generated/ensured: {created} verticals")
    print(f"index: {INDEX_PATH}")

if __name__ == "__main__":
    main()
