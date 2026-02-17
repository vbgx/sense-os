from __future__ import annotations

import json
from pathlib import Path

VERTICALS_DIR = Path("config/verticals")

TAXONOMY = VERTICALS_DIR / "_taxonomy.json"
INDEX = VERTICALS_DIR / "verticals.json"


def _load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def test_json_only_in_verticals_dir():
    assert VERTICALS_DIR.exists()
    assert TAXONOMY.exists()
    assert INDEX.exists()

    for p in VERTICALS_DIR.iterdir():
        if p.name in ("_taxonomy.json", "verticals.json"):
            continue
        if p.suffix in (".json", ".tsv"):
            continue
        raise AssertionError(f"Non-JSON/TSV file found in config/verticals: {p.name}")


def test_all_vertical_json_have_required_fields():
    for p in sorted(VERTICALS_DIR.glob("*.json")):
        if p.name in ("_taxonomy.json", "verticals.json"):
            continue
        d = _load_json(p)
        assert isinstance(d, dict), f"Invalid JSON object: {p}"
        assert d.get("id") or d.get("name"), f"Missing id/name: {p}"
        assert "default_queries" in d, f"Missing default_queries: {p}"
        assert isinstance(d["default_queries"], list) and len(d["default_queries"]) >= 1, f"default_queries empty: {p}"


def test_index_points_to_existing_files():
    idx = _load_json(INDEX)
    items = idx.get("verticals")
    assert isinstance(items, list) and items, "Index 'verticals' list missing/empty"

    for it in items[:200]:  # sample to keep test fast
        assert "id" in it and "file" in it
        p = VERTICALS_DIR / it["file"]
        assert p.exists(), f"Index references missing file: {it['file']}"
