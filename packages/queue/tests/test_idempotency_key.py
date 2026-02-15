from __future__ import annotations

from sense_queue.idempotency import idempotency_key


def test_idempotency_key_is_stable():
    a = {"type": "hello", "queue": "q", "x": 1, "y": 2}
    b = {"y": 2, "x": 1, "queue": "q", "type": "hello"}  # different order
    assert idempotency_key(a) == idempotency_key(b)


def test_idempotency_key_changes_on_payload_change():
    a = {"type": "hello", "queue": "q", "x": 1}
    b = {"type": "hello", "queue": "q", "x": 2}
    assert idempotency_key(a) != idempotency_key(b)
