from __future__ import annotations

import pytest

from ingestion_worker.pipeline.ingest_vertical import ingest_vertical


def test_ingest_vertical_rejects_unknown_source(monkeypatch):
    with pytest.raises(ValueError):
        ingest_vertical({"vertical_id": 1, "source": "unknown", "limit": 1})
