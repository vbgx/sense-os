from __future__ import annotations

from processing_worker.features.language import detect_language
from processing_worker.features.signal_quality import compute_signal_quality
from processing_worker.features.spam import compute_spam_score
from processing_worker.features.vertical_auto import infer_vertical_auto
from processing_worker.features.pain_score import compute_pain_score

from processing_worker.features_registry.types import FeatureContext, FeatureSpec


def _language(*, content: str, ctx: FeatureContext):
    return detect_language(content)


def _spam(*, content: str, ctx: FeatureContext):
    return compute_spam_score(content)


def _quality(*, content: str, ctx: FeatureContext):
    return compute_signal_quality(content)


def _vertical_auto(*, content: str, ctx: FeatureContext):
    return infer_vertical_auto(
        content=content,
        vertical_db_id=ctx.vertical_db_id,
        taxonomy_version=ctx.taxonomy_version,
    )


def _pain_score(*, content: str, ctx: FeatureContext):
    language_code = detect_language(content)
    return compute_pain_score(content=content, language_code=language_code)


FEATURES: list[FeatureSpec] = [
    FeatureSpec(name="language", fn=_language),
    FeatureSpec(name="spam", fn=_spam),
    FeatureSpec(name="quality", fn=_quality),
    FeatureSpec(name="vertical_auto", fn=_vertical_auto),
    FeatureSpec(name="pain_score", fn=_pain_score),
]
