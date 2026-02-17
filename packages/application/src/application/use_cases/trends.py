from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from application.ports import UnitOfWork


def _default_day_iso() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _cid_int(cluster_id: str) -> int:
    try:
        return int(cluster_id)
    except Exception as exc:
        raise ValueError(f"invalid cluster_id: {cluster_id!r}") from exc


@dataclass(frozen=True)
class TrendsQuery:
    vertical_id: int
    day: str
    limit: int
    offset: int
    sparkline_days: int
    min_exploitability: int | None = None
    max_exploitability: int | None = None


@dataclass(frozen=True)
class TopPainsQuery:
    vertical_id: int
    limit: int
    offset: int
    min_exploitability: int | None = None
    max_exploitability: int | None = None


@dataclass
class TrendsUseCase:
    uow: UnitOfWork

    def list_trending(self, q: TrendsQuery):
        return self.uow.trends.list_kind("trending", q)

    def list_emerging(self, q: TrendsQuery):
        return self.uow.trends.list_kind("emerging", q)

    def list_declining(self, q: TrendsQuery):
        return self.uow.trends.list_kind("declining", q)

    def list_top_pains(self, q: TopPainsQuery):
        return self.uow.trends.list_top_pains(q)

    def get_cluster_detail(
        self,
        *,
        vertical_id: int,
        cluster_id: str,
        day: str,
        sparkline_days: int,
    ):
        _cid_int(cluster_id)
        return self.uow.trends.get_cluster_detail(
            vertical_id=int(vertical_id),
            cluster_id=str(cluster_id),
            day=day or _default_day_iso(),
            sparkline_days=int(sparkline_days),
        )


def build_query(
    *,
    vertical_id: int,
    day: str | None,
    limit: int,
    offset: int,
    sparkline_days: int,
    min_exploitability: int | None = None,
    max_exploitability: int | None = None,
) -> TrendsQuery:
    return TrendsQuery(
        vertical_id=int(vertical_id),
        day=(day or _default_day_iso()),
        limit=int(limit),
        offset=int(offset),
        sparkline_days=int(sparkline_days),
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )


def build_top_pains_query(
    *,
    vertical_id: int,
    limit: int,
    offset: int,
    min_exploitability: int | None = None,
    max_exploitability: int | None = None,
) -> TopPainsQuery:
    return TopPainsQuery(
        vertical_id=int(vertical_id),
        limit=int(limit),
        offset=int(offset),
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )
