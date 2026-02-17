from __future__ import annotations

import os
from pathlib import Path

import yaml


VERTICALS_DIR = Path(os.getenv("VERTICALS_DIR", "config/verticals"))
INDEX_FILE = VERTICALS_DIR / "verticals.json"
TAX_FILE = VERTICALS_DIR / "_taxonomy.yml"


def _load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def test_taxonomy_exists_and_loads():
    assert TAX_FILE.exists(), f"Missing taxonomy: {TAX_FILE}"
    data = _load_yaml(TAX_FILE)
    assert isinstance(data, dict)
    assert "generation" in data
    assert "functions" in data
    assert "segments" in data


def test_index_exists_and_is_consistent_with_files():
    assert INDEX_FILE.exists(), f"Missing index: {INDEX_FILE}"
    idx = _load_yaml(INDEX_FILE)
    assert isinstance(idx, dict)
    items = idx.get("verticals")
    assert isinstance(items, list)
    assert items, "Index has no entries"

    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "Duplicate ids in index"

    for x in items:
        assert "file" in x, f"Index entry missing file: {x}"
        path = VERTICALS_DIR / x["file"]
        assert path.exists(), f"Index references missing file: {path}"


def test_all_vertical_yamls_load_and_have_required_fields():
    # All yml excluding index + taxonomy
    for p in sorted(VERTICALS_DIR.glob("*.yml")):
        if p.name in ("verticals.yml","verticals.json","_taxonomy.yml"):
            continue
        d = _load_yaml(p)
        assert isinstance(d, dict), f"Invalid YAML mapping: {p}"
        assert "id" in d or "name" in d, f"Missing id/name: {p}"
        assert "default_queries" in d, f"Missing default_queries (compat): {p}"
        assert isinstance(d["default_queries"], list), f"default_queries must be a list: {p}"
        # safety: descriptions with ':' must parse (this test would fail if not)
        if "description" in d and d["description"] is not None:
            assert isinstance(d["description"], str), f"description must be string: {p}"
