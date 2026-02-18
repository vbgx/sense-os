from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Protocol


@dataclass(frozen=True)
class FetchContext:
    vertical_id: str
    vertical_db_id: int
    taxonomy_version: str
    query: str | None = None
    limit: int = 50


class Adapter(Protocol):
    source: str

    def fetch_signals(self, ctx: FetchContext, **kwargs: Any) -> Iterable[dict[str, Any]]: ...


class BaseAdapter(ABC):
    source: str

    @abstractmethod
    def fetch_signals(self, ctx: FetchContext, **kwargs: Any) -> Iterable[dict[str, Any]]:
        raise NotImplementedError
