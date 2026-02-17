from __future__ import annotations

import time
from typing import Any

import pytest
import redis  # type: ignore


_store: dict[str, list[str]] = {}


class _InMemoryRedis:
    def __init__(self, url: str, decode_responses: bool = True):
        self._url = url
        self._decode_responses = decode_responses

    def delete(self, name: str) -> int:
        return 1 if _store.pop(name, None) is not None else 0

    def lpush(self, name: str, value: str) -> int:
        _store.setdefault(name, []).insert(0, value)
        return len(_store[name])

    def blpop(self, name: str, timeout: int | float | None = 0):
        deadline = None
        if timeout:
            deadline = time.time() + float(timeout)

        while True:
            bucket = _store.get(name, [])
            if bucket:
                value = bucket.pop()
                return (name, value)

            if deadline is None:
                return None

            if time.time() >= deadline:
                return None

            time.sleep(0.01)


@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch: pytest.MonkeyPatch):
    def _from_url(url: str, *args: Any, **kwargs: Any) -> _InMemoryRedis:
        decode_responses = kwargs.get("decode_responses", True)
        return _InMemoryRedis(url, decode_responses=decode_responses)

    monkeypatch.setattr(redis.Redis, "from_url", staticmethod(_from_url))
