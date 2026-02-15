from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    mode: Literal["single", "yaml"] = "single"
    vertical_id: int | None = Field(default=None, ge=1)
    source: str = "reddit"
    query: str | None = None
    limit: int | None = Field(default=None, ge=1, le=200)
    fixture: str | None = None


class RunResponse(BaseModel):
    run_id: str
    status: str


class QueueStats(BaseModel):
    pending: int
    retry: int
    dlq: int


class QueuesResponse(BaseModel):
    queues: dict[str, QueueStats]


class LogsResponse(BaseModel):
    service: str
    container_id: str | None = None
    lines: list[str]
