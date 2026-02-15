from processing_worker.features.sentiment import sentiment_score


def test_sentiment_basic():
    text = "I hate this tool."
    score = sentiment_score(text)
    assert isinstance(score, float)
