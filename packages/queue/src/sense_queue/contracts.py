from __future__ import annotations

from typing import Literal, TypedDict, Union


JobType = Literal[
    "ingest_vertical",
    "process_signals",
    "cluster_pains",
    "trend_job",
]


class BaseJob(TypedDict):
    type: JobType
    run_id: str
    vertical_id: int


class TrendJob(BaseJob):
    type: Literal["trend_job"]
    day: str  # YYYY-MM-DD
    algo_version: str


JobPayload = Union[TrendJob]
