from __future__ import annotations

from ingestion_worker.adapters.hackernews.types import parse_hn_item
from ingestion_worker.adapters.hackernews.map import map_hn_story_to_signal_dict, map_hn_comment_to_signal_dict


def test_map_hn_story_to_signal_dict_contract():
    raw = {
        "id": 123,
        "type": "story",
        "by": "alice",
        "time": 1700000000,
        "title": "Ask HN: Something",
        "text": "Body",
        "url": None,
        "kids": [456],
    }
    item = parse_hn_item(raw)
    d = map_hn_story_to_signal_dict(item, raw, vertical_id=7, kind="ask")
    assert set(d.keys()) == {"vertical_id", "source", "external_id", "content", "url"}
    assert d["vertical_id"] == 7
    assert d["source"] == "hackernews"
    assert d["external_id"] == "hn:123"
    assert isinstance(d["content"], str)
    assert d["content"]


def test_map_hn_comment_to_signal_dict_contract():
    raw = {
        "id": 456,
        "type": "comment",
        "by": "bob",
        "time": 1700000100,
        "text": "Comment text",
        "kids": [],
    }
    item = parse_hn_item(raw)
    d = map_hn_comment_to_signal_dict(item, raw, vertical_id=7, parent_story_id=123)
    assert set(d.keys()) == {"vertical_id", "source", "external_id", "content", "url"}
    assert d["source"] == "hackernews"
    assert d["external_id"] == "hn:456"
    assert d["content"]
