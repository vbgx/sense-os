from dataclasses import dataclass
from processing_worker.features.question_detect import is_question
from processing_worker.features.sentiment import simple_sentiment_score
from processing_worker.features.markers import features as marker_features


@dataclass(frozen=True)
class FeatureVector:
    is_question: bool
    sentiment: float
    pain_hits: int
    workaround_hits: int
    money_hits: int
    length: int


def extract_features(text: str) -> FeatureVector:
    mf = marker_features(text)
    return FeatureVector(
        is_question=is_question(text),
        sentiment=simple_sentiment_score(text),
        pain_hits=mf["pain_hits"],
        workaround_hits=mf["workaround_hits"],
        money_hits=mf["money_hits"],
        length=mf["len"],
    )
