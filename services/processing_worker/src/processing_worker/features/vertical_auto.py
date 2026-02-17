from __future__ import annotations

from domain.scoring.vertical_classifier_v1 import (
    VerticalClassifierV1,
    classify_vertical_v1,
    load_vertical_docs_default,
)


_classifier: VerticalClassifierV1 | None = None


def _get_classifier() -> VerticalClassifierV1:
    global _classifier
    if _classifier is None:
        docs = load_vertical_docs_default()
        _classifier = VerticalClassifierV1(vertical_docs=docs)
    return _classifier


def compute_vertical_auto(*, content: str, threshold: float) -> tuple[str, int]:
    clf = _get_classifier()
    return classify_vertical_v1(content=content or "", threshold=threshold, classifier=clf)
