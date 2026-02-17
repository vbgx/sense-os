#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ID_RE = re.compile(r"^[a-z0-9_]+$")
DEFAULT_TAXONOMY_FILE = "taxonomy.json"
FALLBACK_TAXONOMY_FILE = "_taxonomy.json"
INDEX_JSON = "verticals.json"
BULK_TSV_SUFFIX = "_bulk_seed.tsv"
DEFAULT_TIER = "core"
ALLOWED_TIERS = {"core", "experimental", "long_tail"}
META_KEYS = ("audience", "function", "industry", "cluster", "member", "persona", "variant")


def _die(msg: str) -> None:
    raise RuntimeError(msg)


def _read_json(path: Path) -> Any:
    if not path.exists():
        _die(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any, check: bool) -> bool:
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False
    if check:
        return True
    path.write_text(content, encoding="utf-8")
    return True


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _stable_pick(items: List[str], key: str) -> str:
    if not items:
        return ""
    h = int(_sha(key)[:16], 16)
    return items[h % len(items)]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_taxonomy(verticals_dir: Path) -> Dict[str, Any]:
    candidates = [
        verticals_dir / DEFAULT_TAXONOMY_FILE,
        verticals_dir / FALLBACK_TAXONOMY_FILE,
    ]
    tax_path = next((p for p in candidates if p.exists()), None)
    if tax_path is None:
        _die(f"Missing taxonomy file (expected taxonomy.json or _taxonomy.json) in: {verticals_dir}")

    data = _read_json(tax_path)
    if not isinstance(data, dict):
        _die("taxonomy must be a JSON object")

    if int(data.get("schema_version", 0)) < 1:
        _die("taxonomy missing/invalid schema_version")

    if "axes" not in data or "clusters" not in data:
        _die("taxonomy must include axes and clusters")

    rules = data.get("rules", {}) or {}
    gen = (rules.get("generation") or {})
    if "max_generate" not in gen:
        gen["max_generate"] = 20000
    rules["generation"] = gen
    data["rules"] = rules

    engine = data.get("engine", {}) or {}
    engine.setdefault("default_enabled", True)
    engine.setdefault("default_priority_step", 10)
    engine.setdefault("id_prefix", "")
    data["engine"] = engine

    return data


def _iter_axis_ids(tax: Dict[str, Any], axis: str) -> List[str]:
    axes = tax.get("axes", {}) or {}
    items = axes.get(axis) or []
    out: List[str] = []
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            out.append(str(it["id"]))
    return out


def _axis_label_map(tax: Dict[str, Any], axis: str) -> Dict[str, str]:
    axes = tax.get("axes", {}) or {}
    items = axes.get(axis) or []
    out: Dict[str, str] = {}
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            out[str(it["id"])] = str(it.get("label") or it["id"])
    return out


def _persona_map(tax: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p in (tax.get("personas") or []):
        if isinstance(p, dict) and p.get("id"):
            out[str(p["id"])] = p
    return out


def _validate_id(vid: str, max_len: int = 80) -> None:
    if len(vid) > max_len:
        _die(f"id too long ({len(vid)}>{max_len}): {vid}")
    if not ID_RE.match(vid):
        _die(f"invalid id format: {vid}")


@dataclass(frozen=True)
class Member:
    id: str
    label: str
    default_queries: List[str]


def _collect_members(tax: Dict[str, Any]) -> List[Member]:
    members: List[Member] = []
    for c in (tax.get("clusters") or []):
        if not isinstance(c, dict):
            continue
        for m in (c.get("members") or []):
            if not isinstance(m, dict):
                continue
            mid = str(m.get("id") or "").strip()
            if not mid:
                continue
            label = str(m.get("label") or mid)
            dq = m.get("default_queries") or []
            if not isinstance(dq, list):
                dq = []
            dq = [str(x) for x in dq if str(x).strip()]
            members.append(Member(id=mid, label=label, default_queries=dq))
    # stable ordering
    members.sort(key=lambda x: (_sha(x.id), x.id))
    return members


def _build_queries(member: Member, persona_keywords: List[str], suffixes: List[str], max_n: int = 12) -> List[str]:
    # deterministic query builder; avoid YAML colon issues by staying in JSON anyway.
    base: List[str] = []
    base.extend(member.default_queries[:max_n])
    # add deterministic expansions
    kw = [k.strip() for k in persona_keywords if k.strip()]
    seeds = [member.label] + kw[:6]
    out: List[str] = []
    for s in seeds:
        s = s.strip()
        if not s:
            continue
        out.append(s)
        for suf in suffixes:
            out.append(f"{s} {suf}".strip())

    # normalize & unique (case-insensitive)
    seen = set()
    uniq: List[str] = []
    for q in base + out:
        qn = q.strip()
        if not qn:
            continue
        key = qn.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(qn)
        if len(uniq) >= max_n:
            break
    return uniq


def _normalize_tier(value: Any) -> str:
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ALLOWED_TIERS:
            return v
    return DEFAULT_TIER


def _normalize_meta(
    meta: Any,
    axes: Dict[str, Any] | None,
    persona: Any,
) -> Dict[str, Optional[str]]:
    meta_in: Dict[str, Any] = meta if isinstance(meta, dict) else {}
    axes_in: Dict[str, Any] = axes if isinstance(axes, dict) else {}

    merged: Dict[str, Any] = dict(meta_in)
    for key in ("audience", "function", "industry", "cluster", "member", "variant"):
        if merged.get(key) in (None, ""):
            v = axes_in.get(key)
            if v not in (None, ""):
                merged[key] = v
    if merged.get("persona") in (None, "") and persona not in (None, ""):
        merged["persona"] = persona

    out: Dict[str, Optional[str]] = {}
    for key in META_KEYS:
        v = merged.get(key)
        if v is None:
            out[key] = None
            continue
        s = str(v).strip()
        out[key] = s if s else None
    return out


def _make_vertical_doc(
    *,
    vid: str,
    title: str,
    description: str,
    tags: List[str],
    default_queries: List[str],
    persona_id: str,
    axes: Dict[str, str],
    notes: str,
    enabled: bool,
    version: int = 1,
    meta: Optional[Dict[str, Any]] = None,
    tier: str = DEFAULT_TIER,
) -> Dict[str, Any]:
    return {
        "id": vid,
        "name": vid,
        "title": title,
        "description": description,
        "version": version,
        "enabled": enabled,
        "tags": tags,
        "default_queries": default_queries,
        "persona": persona_id,
        "axes": axes,
        "meta": _normalize_meta(meta, axes, persona_id),
        "tier": _normalize_tier(tier),
        "notes": notes,
    }


def _existing_ids(verticals_dir: Path) -> Tuple[List[str], Dict[str, Path]]:
    mapping: Dict[str, Path] = {}
    ids: List[str] = []
    for p in sorted(verticals_dir.glob("*.json")):
        if p.name in (INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE):
            continue
        if p.name.endswith(BULK_TSV_SUFFIX):
            continue
        try:
            d = _read_json(p)
        except Exception:
            # if a file is corrupt, we still want to surface deterministically
            continue
        if isinstance(d, dict):
            vid = str(d.get("id") or d.get("name") or p.stem)
            mapping[vid] = p
            ids.append(vid)
    ids = sorted(set(ids), key=lambda x: (_sha(x), x))
    return ids, mapping


def _candidate_ids(tax: Dict[str, Any], members: List[Member], target: int) -> List[Tuple[str, Dict[str, str], Member]]:
    """
    Deterministic combinator:
    - keep member ids as base
    - generate combinations with axes (audience/function/industry) if present
    - add suffix variants _vN for collisions / scaling
    """
    rules = (tax.get("rules") or {}).get("id_format") or {}
    max_len = int(rules.get("max_len", 80))

    gen = (tax.get("rules") or {}).get("generation") or {}
    max_generate = int(gen.get("max_generate", 20000))
    include_industry = bool(gen.get("include_industry_variants", True))
    suffix_base = str(gen.get("variant_suffix", "_v"))  # like "_v"
    persona_rotation = bool(gen.get("persona_rotation", True))

    audience = _iter_axis_ids(tax, "audience")
    function = _iter_axis_ids(tax, "function")
    industry = _iter_axis_ids(tax, "industry") if include_industry else []

    # base combos (axes order matters for id stability)
    combos: List[Tuple[Dict[str, str], str]] = []
    combos.append(({}, "base"))
    for a in audience:
        combos.append(({"audience": a}, "audience"))
    for f in function:
        combos.append(({"function": f}, "function"))
    if industry:
        for i in industry:
            combos.append(({"industry": i}, "industry"))
    for a in audience:
        for f in function:
            combos.append(({"audience": a, "function": f}, "audience_function"))
    if industry:
        for a in audience:
            for i in industry:
                combos.append(({"audience": a, "industry": i}, "audience_industry"))
        for f in function:
            for i in industry:
                combos.append(({"function": f, "industry": i}, "function_industry"))
        for a in audience:
            for f in function:
                for i in industry:
                    combos.append(({"audience": a, "function": f, "industry": i}, "audience_function_industry"))

    # stable order by hash of combo signature then name
    def _combo_key(x: Tuple[Dict[str, str], str]) -> Tuple[str, str]:
        axes, kind = x
        sig = kind + "|" + "|".join(f"{k}={axes[k]}" for k in sorted(axes.keys()))
        return (_sha(sig), sig)

    combos.sort(key=_combo_key)

    candidates: List[Tuple[str, Dict[str, str], Member]] = []
    prefix = str((tax.get("engine") or {}).get("id_prefix") or "")
    # deterministically generate until max_generate cap
    for m in members:
        for axes, _kind in combos:
            parts: List[str] = []
            if prefix:
                parts.append(prefix)
            # prefer explicit axis ordering for id
            if "audience" in axes:
                parts.append(axes["audience"])
            if "function" in axes:
                parts.append(axes["function"])
            if "industry" in axes:
                parts.append(axes["industry"])
            parts.append(m.id)
            base_id = "_".join(parts)
            base_id = _slug(base_id)
            # validate base id format; if too long we will hash-shorten deterministically
            if len(base_id) > max_len:
                short = base_id[: max(10, max_len - 13)]
                base_id = f"{short}_{_sha(base_id)[:12]}"
            _validate_id(base_id, max_len=max_len)
            candidates.append((base_id, axes, m))

    # de-duplicate base candidates by id (keep first occurrence stable)
    seen = set()
    uniq: List[Tuple[str, Dict[str, str], Member]] = []
    for cid, axes, m in sorted(candidates, key=lambda x: (_sha(x[0] + "|" + json.dumps(x[1], sort_keys=True)), x[0])):
        if cid in seen:
            continue
        seen.add(cid)
        uniq.append((cid, axes, m))

    # If we need more than base ids, expand with suffix variants deterministically.
    if len(uniq) < min(target, max_generate):
        expanded: List[Tuple[str, Dict[str, str], Member]] = uniq[:]
        # cycle variants over uniq base list
        v = 2
        while len(expanded) < min(target, max_generate):
            for cid, axes, m in uniq:
                vid = f"{cid}{suffix_base}{v}"
                if len(vid) > max_len:
                    short = cid[: max(10, max_len - (len(suffix_base) + len(str(v)) + 1 + 12))]
                    vid = f"{short}{suffix_base}{v}_{_sha(cid + str(v))[:12]}"
                vid = _slug(vid)
                if vid in seen:
                    continue
                _validate_id(vid, max_len=max_len)
                seen.add(vid)
                expanded.append((vid, axes, m))
                if len(expanded) >= min(target, max_generate):
                    break
            v += 1
            if v > 99999:
                break
        uniq = expanded

    # hard cap
    uniq = uniq[: min(target, max_generate)]
    return uniq


def compile_verticals(verticals_dir: Path, target: int, prune: bool, check: bool) -> bool:
    _ensure_dir(verticals_dir)
    tax = _load_taxonomy(verticals_dir)
    members = _collect_members(tax)

    if not members:
        _die("taxonomy has no cluster members")

    personas = _persona_map(tax)
    persona_ids = sorted(list(personas.keys()))
    # fall back persona list if taxonomy has none
    if not persona_ids:
        persona_ids = ["general"]

    audience_labels = _axis_label_map(tax, "audience")
    function_labels = _axis_label_map(tax, "function")
    industry_labels = _axis_label_map(tax, "industry")

    engine = tax.get("engine") or {}
    default_enabled = bool(engine.get("default_enabled", True))
    prio_step = int(engine.get("default_priority_step", 10))
    taxonomy_version = str(tax.get("taxonomy_version") or "").strip()
    if not taxonomy_version:
        taxonomy_version = "unknown"

    existing_ids, existing_map = _existing_ids(verticals_dir)
    existing_set = set(existing_ids)

    # choose candidates deterministically
    candidates = _candidate_ids(tax, members, target=target)

    # ensure we can hit target count (existing + new), unless prune is true (then we can shrink)
    if not prune and len(existing_set) > target:
        _die(f"existing verticals ({len(existing_set)}) > target ({target}); use --prune to shrink")
    if not prune:
        needed = target - len(existing_set)
        if needed < 0:
            needed = 0
    else:
        needed = max(0, target)  # will rebuild exactly target

    # Build final id list
    if prune:
        chosen = [c for c in candidates][:target]
        final_ids = [cid for cid, _axes, _m in chosen]
    else:
        # keep existing; fill with new from candidates
        final_ids = list(existing_ids)
        for cid, _axes, _m in candidates:
            if cid in existing_set:
                continue
            final_ids.append(cid)
            if len(final_ids) >= target:
                break

    if len(final_ids) != target:
        _die(f"Not enough unique candidates for target={target}. Got {len(final_ids)}. Expand taxonomy axes/clusters/members.")

    # Write vertical docs for ids that don't exist yet (or if prune, rewrite all deterministically)
    changed = False
    suffixes = ["pain", "bottleneck", "automation", "workflow", "tooling", "process", "best practices"]

    # map candidate -> metadata
    cand_map: Dict[str, Tuple[Dict[str, str], Member]] = {cid: (axes, m) for cid, axes, m in candidates}

    for cid in final_ids:
        axes, m = cand_map.get(cid, ({}, Member(id=cid, label=cid, default_queries=[])))

        # persona rotation: deterministic pick by id hash
        persona_id = _stable_pick(persona_ids, cid) if persona_ids else "general"
        persona_kw = (personas.get(persona_id, {}) or {}).get("keywords") or []
        if not isinstance(persona_kw, list):
            persona_kw = []
        persona_kw = [str(x) for x in persona_kw]

        # labels
        a = axes.get("audience")
        f = axes.get("function")
        i = axes.get("industry")
        parts_title: List[str] = []
        if a:
            parts_title.append(audience_labels.get(a, a).strip())
        if f:
            parts_title.append(function_labels.get(f, f).strip())
        if i:
            parts_title.append(industry_labels.get(i, i).strip())
        parts_title.append(m.label.strip())

        title = " — ".join([p for p in parts_title if p])
        desc_bits: List[str] = []
        if a:
            desc_bits.append(f"{audience_labels.get(a, a)}")
        if f:
            desc_bits.append(f"{function_labels.get(f, f)}")
        if i:
            desc_bits.append(f"{industry_labels.get(i, i)}")
        if not desc_bits:
            desc_bits = ["General"]
        description = f"{', '.join(desc_bits)} pains and workflows around {m.label}."

        tags: List[str] = []
        if a:
            tags.append(a)
        if f:
            tags.append(f)
        if i:
            tags.append(i)
        tags.append(_slug(m.id))

        default_queries = _build_queries(m, persona_kw, suffixes, max_n=12)
        notes = f"Generated deterministically from taxonomy (member={m.id}, persona={persona_id})."

        doc = _make_vertical_doc(
            vid=cid,
            title=title,
            description=description,
            tags=tags,
            default_queries=default_queries,
            persona_id=persona_id,
            axes=axes,
            notes=notes,
            enabled=default_enabled,
            version=1,
        )

        path = verticals_dir / f"{cid}.json"
        if prune or cid not in existing_map:
            changed |= _write_json(path, doc, check=check)

    # Prune extra json files if requested
    if prune:
        keep = set(final_ids) | {INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE}
        for p in sorted(verticals_dir.glob("*.json")):
            if p.name in (INDEX_JSON, DEFAULT_TAXONOMY_FILE, FALLBACK_TAXONOMY_FILE):
                continue
            if p.stem not in keep:
                changed = True
                if not check:
                    p.unlink()

    # Write index verticals.json (source-of-truth for API router)
    index_items: List[Dict[str, Any]] = []
    prio = prio_step
    for cid in final_ids:
        meta = None
        tier = None
        doc_path = verticals_dir / f"{cid}.json"
        if doc_path.exists():
            doc = _read_json(doc_path)
            if isinstance(doc, dict):
                meta = _normalize_meta(doc.get("meta"), doc.get("axes"), doc.get("persona"))
                tier = _normalize_tier(doc.get("tier"))
        if meta is None:
            axes, _m = cand_map.get(cid, ({}, Member(id=cid, label=cid, default_queries=[])))
            persona_id = _stable_pick(persona_ids, cid) if persona_ids else "general"
            meta = _normalize_meta(None, axes, persona_id)
        if tier is None:
            tier = DEFAULT_TIER
        index_items.append(
            {
                "id": cid,
                "file": f"{cid}.json",
                "enabled": default_enabled,
                "priority": prio,
                "tier": tier,
                "meta": meta,
                "taxonomy_version": taxonomy_version,
            }
        )
        prio += prio_step

    index_doc = {"taxonomy_version": taxonomy_version, "verticals": index_items}
    changed |= _write_json(verticals_dir / INDEX_JSON, index_doc, check=check)

    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="config/verticals", help="verticals directory")
    ap.add_argument("--target", type=int, default=1000, help="target number of verticals")
    ap.add_argument("--prune", action="store_true", help="delete extra vertical json files to match target exactly")
    ap.add_argument("--check", action="store_true", help="dry-run (no writes), exit non-zero if changes needed")
    args = ap.parse_args()

    verticals_dir = Path(args.dir).resolve()
    changed = compile_verticals(verticals_dir, target=int(args.target), prune=bool(args.prune), check=bool(args.check))

    if args.check and changed:
        _die("verticals_compile: changes required (run without --check)")


if __name__ == "__main__":
    main()
