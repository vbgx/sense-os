from processing_worker.features.markers import extract_markers


def test_markers_basic():
    text = "This is frustrating and costs us time."
    markers = extract_markers(text)
    assert isinstance(markers, dict)
