from __future__ import annotations

import json
import logging
from pathlib import Path

from clustering_worker.pipeline.build_vectors import build_vectors
from clustering_worker.vectorize.tfidf import HashingVectorizerConfig


def test_vectorize_emits_json_event(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO)
    cfg = HashingVectorizerConfig(n_features=2**10)
    _ = build_vectors([{"text": "hello"}], cache_dir=str(tmp_path / "vectors"), cfg=cfg)

    events = []
    for rec in caplog.records:
        msg = rec.getMessage()
        if '"event"' in msg and '"vectorize_stats"' in msg:
            events.append(msg)

    assert events, "Expected a vectorize_stats JSON log line"
    payload = json.loads(events[-1])
    assert payload["event"] == "vectorize_stats"
    assert payload["items_total"] == 1
    assert payload["texts_unique"] == 1
