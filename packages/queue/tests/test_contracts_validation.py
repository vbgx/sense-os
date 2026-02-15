from __future__ import annotations

import pytest

from sense_queue.contracts import validate_job


def test_validate_job_ok():
    job = validate_job({"type": "hello", "queue": "test", "run_id": "r1"})
    assert job.type == "hello"
    assert job.queue == "test"
    assert job.run_id == "r1"


def test_validate_job_missing_required_fails():
    with pytest.raises(ValueError):
        validate_job({"queue": "test"})  # missing type
