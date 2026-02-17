from __future__ import annotations

import json
from pathlib import Path

from domain.scoring.vertical_classifier_v1 import load_vertical_docs


def test_vertical_docs_load_from_json(tmp_path: Path):
    vert_dir = tmp_path / "verticals"
    vert_dir.mkdir(parents=True)

    (vert_dir / "verticals.json").write_text(
        json.dumps(
            {
                "verticals": [
                    {"id": "saas_founders", "file": "saas_founders.json", "enabled": True, "priority": 10}
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    (vert_dir / "saas_founders.json").write_text(
        json.dumps(
            {
                "id": "saas_founders",
                "name": "saas_founders",
                "title": "SaaS Founders",
                "description": "SaaS founders building early-stage B2B products",
                "default_queries": ["billing software", "stripe alternative"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    docs = load_vertical_docs(vert_dir)
    assert isinstance(docs, list)
    assert docs[0]["id"] == "saas_founders"
    assert "default_queries" in docs[0]
