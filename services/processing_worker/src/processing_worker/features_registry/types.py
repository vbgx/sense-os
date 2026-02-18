from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class FeatureContext:
    vertical_db_id: int
    taxonomy_version: str


class FeatureFn(Protocol):
    def __call__(self, *, content: str, ctx: FeatureContext) -> Any: ...


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    fn: FeatureFn
