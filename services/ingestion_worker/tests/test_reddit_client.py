import json

from ingestion_worker.adapters.reddit.client import RedditClient


def test_parse_listing_posts_and_cursor():
    payload = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "abc123",
                        "title": "Hello",
                        "selftext": "Body",
                        "url": "https://example.com",
                        "created_utc": 1700000000,
                    }
                }
            ],
            "after": "t3_next",
        }
    }
    raw = json.dumps(payload)
    client = RedditClient()

    data = client.parse_listing(raw)
    posts = client.parse_posts(data)

    assert posts[0]["external_id"] == "abc123"
    assert posts[0]["title"] == "Hello"
    assert posts[0]["content"] == "Body"
    assert posts[0]["url"] == "https://example.com"
    assert posts[0]["created_at_iso"] == 1700000000
    assert client.get_next_cursor(data) == "t3_next"
