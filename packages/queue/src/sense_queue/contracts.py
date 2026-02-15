from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypedDict, Union


JobType = Literal[
    "ingest_vertical",
    "process_signals",
    "cluster_pains",
    "cluster_vertical",
    "trend_job",
    "trend_day",
]


class BaseJob(TypedDict):
    type: JobType
    run_id: str
    vertical_id: int


class TrendJob(BaseJob):
    type: Literal["trend_job"]
    day: str  # YYYY-MM-DD
    algo_version: str
    cluster_version: str
    formula_version: str


JobPayload = Union[TrendJob]


@dataclass
class Job:
    """
    Runtime-validated job wrapper with attribute access.
    """

    type: str
    queue: str | None = None
    run_id: str | None = None
    vertical_id: int | None = None
    day: str | None = None
    cluster_version: str | None = None
    formula_version: str | None = None
    algo_version: str | None = None


def validate_job(payload: dict[str, Any]) -> Job:
    """
    Validate minimum required job fields and return a Job wrapper.
    """
    if not isinstance(payload, dict):
        raise ValueError("job payload must be a dict")
    job_type = payload.get("type")
    if not job_type:
        raise ValueError("job payload missing 'type'")

    return Job(
        type=str(job_type),
        queue=payload.get("queue"),
        run_id=payload.get("run_id"),
        vertical_id=payload.get("vertical_id"),
        day=payload.get("day"),
        cluster_version=payload.get("cluster_version"),
        formula_version=payload.get("formula_version"),
        algo_version=payload.get("algo_version"),
    )
