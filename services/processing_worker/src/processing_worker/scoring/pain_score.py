from processing_worker.features.extract_features import FeatureVector
from domain.scoring.pain_score import score as domain_score


def score_features(features: FeatureVector):
    from domain.models.pain_features import FeatureVector as DomainFV

    dfv = DomainFV(
        is_question=features.is_question,
        sentiment=features.sentiment,
        pain_hits=features.pain_hits,
        workaround_hits=features.workaround_hits,
        money_hits=features.money_hits,
        length=features.length,
    )
    return domain_score(dfv)
