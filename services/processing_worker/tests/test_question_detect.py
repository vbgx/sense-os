from processing_worker.features.question_detect import question_score


def test_question_detect_basic():
    text = "How do I reduce churn?"
    score = question_score(text)
    assert score >= 0
