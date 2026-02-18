from __future__ import annotations

from domain.scoring.vertical_classifier_v1 import (
    VerticalClassifierV1,
    classify_vertical_v1,
    load_vertical_docs_default,
)

_CLASSIFIER: VerticalClassifierV1 | None = None


def _get_classifier() -> VerticalClassifierV1:
    global _CLASSIFIER
    if _CLASSIFIER is None:
        docs = load_vertical_docs_default()
        _CLASSIFIER = VerticalClassifierV1(docs)
    return _CLASSIFIER


def infer_vertical_auto(*, content: str, vertical_db_id: int, taxonomy_version: str) -> dict[str, int | str]:
    _ = vertical_db_id, taxonomy_version
    classifier = _get_classifier()
    if not classifier.vertical_docs:
        return {"id": "unknown", "confidence": 0}
    vid, confidence = classify_vertical_v1(content=content, threshold=0.2, classifier=classifier)
    return {"id": str(vid), "confidence": int(confidence)}
