from __future__ import annotations

from pathlib import Path

import yaml

from domain.scoring.vertical_classifier_v1 import VerticalClassifierV1, VerticalDoc, classify_vertical_v1


def test_classification_coherent_and_stable(tmp_path: Path):
    vdir = tmp_path / "verticals"
    vdir.mkdir()

    (vdir / "saas_founders.yml").write_text(
        yaml.safe_dump(
            {
                "id": "saas_founders",
                "keywords": ["mrr", "churn", "pricing", "b2b saas", "onboarding"],
                "queries": ["how to reduce churn", "pricing experiments"],
            }
        ),
        encoding="utf-8",
    )
    (vdir / "ecommerce_ops.yml").write_text(
        yaml.safe_dump(
            {
                "id": "ecommerce_ops",
                "keywords": ["fulfillment", "warehouse", "returns", "shopify", "inventory"],
                "queries": ["warehouse picking", "returns automation"],
            }
        ),
        encoding="utf-8",
    )

    docs = []
    for p in sorted(vdir.glob("*.yml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        docs.append(VerticalDoc(key=data["id"], text=str(data)))

    clf = VerticalClassifierV1(vertical_docs=docs)

    text = "We hit $12k MRR and reduced churn via onboarding and pricing tests."
    a = classify_vertical_v1(content=text, threshold=0.10, classifier=clf)
    b = classify_vertical_v1(content=text, threshold=0.10, classifier=clf)
    assert a == b
    assert a[0] == "saas_founders"
    assert a[1] >= 10


def test_fallback_unknown_when_below_threshold(tmp_path: Path):
    docs = [
        VerticalDoc(key="remote_ops", text="remote team async timezone payroll compliance"),
        VerticalDoc(key="saas_founders", text="mrr churn pricing onboarding"),
    ]
    clf = VerticalClassifierV1(vertical_docs=docs)
    key, conf = classify_vertical_v1(content="completely unrelated text about cooking", threshold=0.50, classifier=clf)
    assert key == "unknown"
    assert 0 <= conf <= 100
