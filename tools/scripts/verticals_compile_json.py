#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re
from pathlib import Path
from typing import Any, Dict, List


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def dump_json(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def write_if_changed(p: Path, content: str, check: bool) -> bool:
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    if old == content:
        return False
    if check:
        return True
    p.write_text(content, encoding="utf-8")
    return True


def build_queries(keywords: List[str], suffixes: List[str], max_n: int) -> List[str]:
    out: List[str] = []
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        out.append(kw)
        for suf in suffixes:
            out.append(f"{kw} {suf}".strip())
    seen = set()
    uniq: List[str] = []
    for q in out:
        qn = q.lower()
        if qn in seen:
            continue
        seen.add(qn)
        uniq.append(q)
        if len(uniq) >= max_n:
            break
    return uniq


def candidate_vertical(
    vid: str,
    title: str,
    description: str,
    tags: List[str],
    default_queries: List[str],
    enabled: bool,
    defaults: Dict[str, Any],
    ingestion: Dict[str, Any],
    taxonomy: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "id": vid,
        "name": vid,
        "title": title,
        "description": description,
        "version": 1,
        "enabled": enabled,
        "tags": tags,
        "default_queries": default_queries,  # backward-compat
        "defaults": defaults,
        "ingestion": ingestion,
    }
    if taxonomy:
        d["taxonomy"] = taxonomy
    return d


def existing_vertical_json_files(dirp: Path) -> List[Path]:
    return sorted(
        p for p in dirp.glob("*.json")
        if p.name not in ("verticals.json", "_taxonomy.json")
    )


def rebuild_index(dirp: Path, enabled_default: bool, check: bool) -> bool:
    entries = []
    prio = 10
    for p in existing_vertical_json_files(dirp):
        d = load_json(p)
        vid = str(d.get("id") or p.stem)
        enabled = bool(d.get("enabled", enabled_default))
        entries.append({"id": vid, "file": p.name, "enabled": enabled, "priority": prio})
        prio += 10
    idx = {"verticals": entries}
    return write_if_changed(dirp / "verticals.json", dump_json(idx), check=check)


def compile(dirp: Path, target: int, check: bool) -> int:
    tax = load_json(dirp / "_taxonomy.json")
    defaults_all = tax.get("defaults", {})
    enabled_default = bool(defaults_all.get("enabled", True))
    ingestion_default = defaults_all.get("ingestion", {})
    default_defaults = {
        "language_allowlist": defaults_all.get("language_allowlist", ["en"]),
        "min_signal_quality": defaults_all.get("min_signal_quality", 0.2),
    }

    gen = tax.get("generation", {})
    suffixes = (gen.get("queries", {}) or {}).get("suffixes", [])
    max_q = int((gen.get("queries", {}) or {}).get("max_per_vertical", 6))

    # current count
    existing = existing_vertical_json_files(dirp)
    have = {p.stem for p in existing}
    to_add = max(0, target - len(existing))

    segments = tax.get("segments", {})
    functions = tax.get("functions", {})
    industries = {x["id"]: x for x in tax.get("industries", []) if isinstance(x, dict) and x.get("id")}

    families = gen.get("families", [])
    candidates: List[Dict[str, Any]] = []

    for fam in families:
        kind = fam.get("kind")
        if kind == "function":
            for seg_id in fam.get("segments", []):
                seg = segments.get(seg_id, {})
                seg_label = seg.get("label", seg_id)
                seg_tags = list(seg.get("tags", []))
                for fn_id in fam.get("functions", []):
                    fn = functions.get(fn_id, {})
                    fn_label = fn.get("label", fn_id)
                    fn_tags = list(fn.get("tags", []))
                    for sd in fn.get("subdomains", []):
                        sd_id = sd.get("id")
                        sd_label = sd.get("label", sd_id)
                        kws = list(sd.get("keywords", []))
                        if not sd_id or not kws:
                            continue
                        vid = slug(f"{seg_id}_{fn_id}_{sd_id}")
                        title = f"{seg_label} — {fn_label}: {sd_label}"
                        desc = f"{seg_label} teams dealing with {sd_label.lower()} workflows, tooling, and operational friction."
                        tags = sorted(set(seg_tags + fn_tags + [f"{fn_id}:{sd_id}"]))
                        queries = build_queries(kws, suffixes, max_q)
                        candidates.append(candidate_vertical(
                            vid, title, desc, tags, queries,
                            enabled_default, default_defaults, ingestion_default,
                            taxonomy={"segment": seg_id, "function": fn_id, "subdomain": sd_id}
                        ))
        elif kind == "industry":
            fn_hint = fam.get("function_hint")
            fn_tags = list((functions.get(fn_hint, {}) or {}).get("tags", [])) if fn_hint else []
            for seg_id in fam.get("segments", []):
                seg = segments.get(seg_id, {})
                seg_label = seg.get("label", seg_id)
                seg_tags = list(seg.get("tags", []))
                for ind_id in fam.get("industries", []):
                    ind = industries.get(ind_id, {})
                    if not ind:
                        continue
                    ind_label = ind.get("label", ind_id)
                    ind_tags = list(ind.get("tags", []))
                    kws = list(ind.get("keywords", []))
                    if not kws:
                        continue
                    vid = slug(f"industry_{ind_id}")
                    title = f"{seg_label} — {ind_label}"
                    desc = f"{ind_label} operators and teams: recurring ops pain across tools, workflows, compliance, and reporting."
                    tags = sorted(set(seg_tags + ind_tags + fn_tags))
                    queries = build_queries(kws, suffixes, max_q)
                    candidates.append(candidate_vertical(
                        vid, title, desc, tags, queries,
                        enabled_default, default_defaults, ingestion_default,
                        taxonomy={"segment": seg_id, "industry": ind_id, "function_hint": fn_hint} if fn_hint else {"segment": seg_id, "industry": ind_id}
                    ))

    candidates.sort(key=lambda d: d["id"])

    changed = 0
    for v in candidates:
        if to_add <= 0:
            break
        if v["id"] in have:
            continue
        p = dirp / f'{v["id"]}.json'
        if write_if_changed(p, dump_json(v), check=check):
            changed += 1
        have.add(v["id"])
        to_add -= 1

    if rebuild_index(dirp, enabled_default, check=check):
        changed += 1

    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="config/verticals")
    ap.add_argument("--target", type=int, default=1000)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    dirp = Path(args.dir)
    dirp.mkdir(parents=True, exist_ok=True)

    if not (dirp / "_taxonomy.json").exists():
        raise SystemExit(f"Missing {dirp/'_taxonomy.json'}")

    changed = compile(dirp, args.target, args.check)
    if args.check and changed:
        raise SystemExit(2)
    print(f"ok: compiled json verticals (changed={changed}, target={args.target})")


if __name__ == "__main__":
    main()
