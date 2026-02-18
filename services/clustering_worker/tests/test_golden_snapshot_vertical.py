from __future__ import annotations

import json
from pathlib import Path

from clustering_worker.pipeline.run_clustering import run_clustering  # adjust if signature differs


FIX_DIR = Path("tests/fixtures/clustering/golden")
INP = FIX_DIR / "vertical_postgres_inputs.json"
OUT = FIX_DIR / "vertical_postgres_expected.json"


def _normalize(payload: dict) -> dict:
    """
    Remove unstable fields (timestamps, random ids if any).
    Keep only what must NOT drift.
    """
    clusters = payload.get("clusters") or payload.get("items") or []
    norm = []
    for c in clusters:
        norm.append(
            {
                "title": c.get("title"),
                "size": c.get("size"),
                "representative_ids": c.get("representative_ids") or [x.get("id") for x in (c.get("representative_signals") or [])],
                "confidence_score": c.get("confidence_score"),
                "key_phrases": c.get("key_phrases") or c.get("key_phrases_json"),
            }
        )
    norm.sort(key=lambda x: (-(x.get("size") or 0), str(x.get("title") or "")))
    return {"clusters": norm}


def test_golden_snapshot_vertical_postgres():
    inputs = json.loads(INP.read_text(encoding="utf-8"))

    # run pipeline (make sure deterministic ordering inside run_clustering)
    payload = run_clustering(inputs)  # <-- you may need: run_clustering(instances=inputs)
    got = _normalize(payload)

    expected = json.loads(OUT.read_text(encoding="utf-8"))
    expected_norm = _normalize(expected)

    assert got == expected_norm
