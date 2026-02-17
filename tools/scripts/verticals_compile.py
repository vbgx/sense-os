#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None


def _dump_yaml(data: Any) -> str:
    # Deterministic, safe, readable
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=120,
        default_flow_style=False,
    )


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _ensure_str_fields_quoted_in_yaml(yaml_text: str) -> str:
    # If a line like "description: Foo: bar" (unquoted colon) exists,
    # safe_dump will already quote when needed. This is extra defense if editing manually later.
    return yaml_text


@dataclass(frozen=True)
class Candidate:
    vid: str
    title: str
    description: str
    tags: List[str]
    default_queries: List[str]
    notes: Optional[str]
    ingestion: Dict[str, Any]
    defaults: Dict[str, Any]


def _build_queries(keywords: List[str], suffixes: List[str], max_n: int) -> List[str]:
    out: List[str] = []
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        # 1) raw keyword
        out.append(kw)
        # 2) keyword + suffixes
        for suf in suffixes:
            out.append(f"{kw} {suf}".strip())
    # de-dupe preserving order
    seen = set()
    uniq = []
    for q in out:
        qn = q.lower()
        if qn in seen:
            continue
        seen.add(qn)
        uniq.append(q)
        if len(uniq) >= max_n:
            break
    return uniq


def _taxonomy_dir(args_dir: Path) -> Path:
    return args_dir


def _read_taxonomy(verticals_dir: Path) -> Dict[str, Any]:
    tax_path = verticals_dir / "_taxonomy.yml"
    data = _load_yaml(tax_path)
    if not isinstance(data, dict):
        raise RuntimeError(f"Missing or invalid taxonomy: {tax_path}")
    return data


def _existing_vertical_files(verticals_dir: Path) -> List[Path]:
    return sorted(
        p
        for p in verticals_dir.glob("*.yml")
        if p.name not in ("verticals.json", "_taxonomy.yml")
    )


def _load_existing_ids(verticals_dir: Path) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    for p in _existing_vertical_files(verticals_dir):
        d = _load_yaml(p) or {}
        if isinstance(d, dict):
            vid = str(d.get("id") or d.get("name") or p.stem)
            out[vid] = p
    return out


def _make_function_candidates(tax: Dict[str, Any]) -> List[Candidate]:
    defaults = tax.get("defaults") or {}
    segments = tax.get("segments") or {}
    functions = tax.get("functions") or {}
    gen = tax.get("generation") or {}
    suffixes = ((gen.get("queries") or {}).get("suffixes")) or []
    max_q = int(((gen.get("queries") or {}).get("max_per_vertical")) or 6)

    families = (gen.get("families") or [])
    out: List[Candidate] = []

    for fam in families:
        if fam.get("kind") != "function":
            continue
        seg_ids = fam.get("segments") or []
        fn_ids = fam.get("functions") or []
        for seg_id in seg_ids:
            seg = segments.get(seg_id) or {}
            seg_label = seg.get("label", seg_id)
            seg_tags = list(seg.get("tags") or [])
            for fn_id in fn_ids:
                fn = functions.get(fn_id) or {}
                fn_label = fn.get("label", fn_id)
                fn_tags = list(fn.get("tags") or [])
                for sd in (fn.get("subdomains") or []):
                    sd_id = sd.get("id")
                    sd_label = sd.get("label", sd_id)
                    sd_kw = list(sd.get("keywords") or [])
                    if not sd_id or not sd_kw:
                        continue

                    vid = _slug(f"{seg_id}_{fn_id}_{sd_id}")
                    title = f"{seg_label} — {fn_label}: {sd_label}"
                    description = f"{seg_label} teams dealing with {sd_label.lower()} workflows, tooling, and operational friction."
                    tags = sorted(set(seg_tags + fn_tags + [f"{fn_id}:{sd_id}"]))
                    queries = _build_queries(sd_kw, suffixes, max_q)

                    ingestion = dict((defaults.get("ingestion") or {}))
                    # Keep ingestion sources but leave query empty (workers can ignore)
                    # You can later add per-vertical query overrides if you want.
                    out.append(
                        Candidate(
                            vid=vid,
                            title=title,
                            description=description,
                            tags=tags,
                            default_queries=queries,
                            notes=None,
                            ingestion=ingestion,
                            defaults={
                                "language_allowlist": defaults.get("language_allowlist", ["en"]),
                                "min_signal_quality": defaults.get("min_signal_quality", 0.2),
                            },
                        )
                    )

    return out


def _make_industry_candidates(tax: Dict[str, Any]) -> List[Candidate]:
    defaults = tax.get("defaults") or {}
    segments = tax.get("segments") or {}
    industries = tax.get("industries") or []
    functions = tax.get("functions") or {}
    gen = tax.get("generation") or {}
    suffixes = ((gen.get("queries") or {}).get("suffixes")) or []
    max_q = int(((gen.get("queries") or {}).get("max_per_vertical")) or 6)

    families = (gen.get("families") or [])
    out: List[Candidate] = []

    # build lookup
    ind_by_id = {x.get("id"): x for x in industries if isinstance(x, dict) and x.get("id")}

    for fam in families:
        if fam.get("kind") != "industry":
            continue
        seg_ids = fam.get("segments") or []
        ind_ids = fam.get("industries") or []
        fn_hint = fam.get("function_hint")
        fn_tags: List[str] = []
        if fn_hint and fn_hint in functions:
            fn_tags = list((functions.get(fn_hint) or {}).get("tags") or [])

        for seg_id in seg_ids:
            seg = segments.get(seg_id) or {}
            seg_label = seg.get("label", seg_id)
            seg_tags = list(seg.get("tags") or [])
            for ind_id in ind_ids:
                ind = ind_by_id.get(ind_id) or {}
                ind_label = ind.get("label", ind_id)
                ind_tags = list(ind.get("tags") or [])
                ind_kw = list(ind.get("keywords") or [])
                if not ind_kw:
                    continue

                vid = _slug(f"industry_{ind_id}")
                title = f"{seg_label} — {ind_label}"
                description = f"{ind_label} operators and teams: recurring ops pain across tools, workflows, compliance, and reporting."
                tags = sorted(set(seg_tags + ind_tags + fn_tags))
                queries = _build_queries(ind_kw, suffixes, max_q)

                ingestion = dict((defaults.get("ingestion") or {}))
                out.append(
                    Candidate(
                        vid=vid,
                        title=title,
                        description=description,
                        tags=tags,
                        default_queries=queries,
                        notes=None,
                        ingestion=ingestion,
                        defaults={
                            "language_allowlist": defaults.get("language_allowlist", ["en"]),
                            "min_signal_quality": defaults.get("min_signal_quality", 0.2),
                        },
                    )
                )

    return out


def _candidate_to_yaml(c: Candidate, enabled_default: bool) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "id": c.vid,
        "name": c.vid,
        "title": c.title,
        "description": c.description,
        "version": 1,
        "enabled": enabled_default,
        "tags": c.tags,
        "default_queries": c.default_queries,
    }
    if c.notes:
        d["notes"] = c.notes

    if c.ingestion:
        d["ingestion"] = c.ingestion

    if c.defaults:
        d["defaults"] = c.defaults

    return d


def _autofix_vertical_doc(doc: Dict[str, Any], vid_fallback: str) -> Dict[str, Any]:
    # minimal normalization + backward compat
    vid = str(doc.get("id") or doc.get("name") or vid_fallback)
    doc.setdefault("id", vid)
    doc.setdefault("name", vid)
    doc.setdefault("version", 1)
    doc.setdefault("enabled", True)
    doc.setdefault("tags", [])
    if "default_queries" not in doc or not isinstance(doc.get("default_queries"), list):
        doc["default_queries"] = []
    # avoid None for text fields
    for k in ("title", "description", "notes"):
        if k in doc and doc[k] is None:
            doc[k] = ""
    return doc


def _write_if_changed(path: Path, data: Dict[str, Any], check: bool) -> bool:
    new_text = _ensure_str_fields_quoted_in_yaml(_dump_yaml(data))
    old_text = path.read_text(encoding="utf-8") if path.exists() else ""
    if old_text == new_text:
        return False
    if check:
        return True
    path.write_text(new_text, encoding="utf-8")
    return True


def _rebuild_index(verticals_dir: Path, enabled_default: bool, check: bool) -> bool:
    index_path = verticals_dir / "verticals.json"
    files = _existing_vertical_files(verticals_dir)

    entries: List[Dict[str, Any]] = []
    prio = 10
    for p in files:
        d = _load_yaml(p) or {}
        if not isinstance(d, dict):
            continue
        vid = str(d.get("id") or d.get("name") or p.stem)
        enabled = bool(d.get("enabled", enabled_default))
        entries.append({"id": vid, "file": p.name, "enabled": enabled, "priority": prio})
        prio += 10

    doc = {
        "verticals": entries
    }
    return _write_if_changed(index_path, doc, check=check)


def compile_verticals(verticals_dir: Path, target_count: int, check: bool) -> int:
    tax = _read_taxonomy(verticals_dir)

    enabled_default = bool((tax.get("defaults") or {}).get("enabled", True))

    existing = _load_existing_ids(verticals_dir)
    existing_ids = set(existing.keys())

    # 1) generate candidates
    candidates: List[Candidate] = []
    candidates.extend(_make_function_candidates(tax))
    candidates.extend(_make_industry_candidates(tax))

    # deterministic order
    candidates.sort(key=lambda c: c.vid)

    # 2) write missing until target reached
    changed = 0
    current_count = len(_existing_vertical_files(verticals_dir))
    to_add = max(0, target_count - current_count)

    for c in candidates:
        if to_add <= 0:
            break
        if c.vid in existing_ids:
            continue
        path = verticals_dir / f"{c.vid}.yml"
        doc = _candidate_to_yaml(c, enabled_default=enabled_default)
        doc = _autofix_vertical_doc(doc, vid_fallback=c.vid)
        changed += 1 if _write_if_changed(path, doc, check=check) else 0
        existing_ids.add(c.vid)
        to_add -= 1

    # 3) autofix all existing docs (normalize + rewrite to enforce valid YAML)
    for p in _existing_vertical_files(verticals_dir):
        d = _load_yaml(p)
        if not isinstance(d, dict):
            raise RuntimeError(f"Invalid YAML mapping in {p}")
        d2 = _autofix_vertical_doc(d, vid_fallback=p.stem)
        changed += 1 if _write_if_changed(p, d2, check=check) else 0

    # 4) rebuild index
    if _rebuild_index(verticals_dir, enabled_default=enabled_default, check=check):
        changed += 1

    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description="Compile verticals from taxonomy (source-of-truth).")
    ap.add_argument("--dir", default="config/verticals", help="Verticals directory (default: config/verticals)")
    ap.add_argument("--target", type=int, default=None, help="Target total vertical count (default: taxonomy.generation.target_count)")
    ap.add_argument("--check", action="store_true", help="Check-only: exit non-zero if changes would be made")
    args = ap.parse_args()

    verticals_dir = Path(args.dir)
    verticals_dir.mkdir(parents=True, exist_ok=True)

    tax = _read_taxonomy(verticals_dir)
    target = int(args.target or ((tax.get("generation") or {}).get("target_count") or 1000))

    changed = compile_verticals(verticals_dir, target_count=target, check=args.check)
    if args.check and changed:
        raise SystemExit(2)
    print(f"ok: compiled verticals (changed={changed}, target={target})")


if __name__ == "__main__":
    main()
