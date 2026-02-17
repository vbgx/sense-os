from __future__ import annotations

from typing import Any, Protocol, Sequence


class NotFoundError(Exception):
    """Raised when an entity is not found in a use case."""


class SchedulerRepo(Protocol):
    def get_last_run(self) -> Any:
        ...


class PainClustersRepo(Protocol):
    def list(self) -> list[Any]:
        ...

    def get(self, cluster_id: str) -> Any:
        ...

    def count(self) -> int:
        ...

    def list_top_pains(
        self,
        *,
        vertical_id: str | None,
        tier: str | None,
        limit: int,
        offset: int,
        opportunity_window_status: str | None,
    ) -> list[Any]:
        ...


class PainInstancesRepo(Protocol):
    def list_ranked(
        self,
        *,
        vertical_id: int,
        limit: int,
        offset: int,
    ) -> tuple[list[Any], int]:
        ...

    def get_with_signal(self, *, pain_id: int) -> Any:
        ...


class SignalsRepo(Protocol):
    def list_by_vertical(
        self,
        *,
        vertical_id: int,
        limit: int,
        offset: int,
    ) -> list[Any]:
        ...

    def count_by_vertical(self, *, vertical_id: int) -> int:
        ...

    def count_last_days(self, *, days: int) -> int:
        ...

    def get_by_ids(self, ids: Sequence[int]) -> list[Any]:
        ...


class VerticalsRepo(Protocol):
    def get_all(self) -> list[Any]:
        ...

    def get_by_name(self, name: str) -> Any | None:
        ...

    def create(self, name: str) -> Any:
        ...


class ClusterDailyHistoryRepo(Protocol):
    def list_cluster_history(self, *, cluster_id: str, days: int) -> list[Any]:
        ...


class TrendsRepo(Protocol):
    def list_kind(self, kind: str, q: Any) -> dict[str, Any]:
        ...

    def list_top_pains(self, q: Any) -> dict[str, Any]:
        ...

    def get_cluster_detail(
        self,
        *,
        vertical_id: int,
        cluster_id: str,
        day: str,
        sparkline_days: int,
    ) -> dict[str, Any]:
        ...


class UnitOfWork(Protocol):
    pain_clusters: PainClustersRepo
    pain_instances: PainInstancesRepo
    signals: SignalsRepo
    verticals: VerticalsRepo
    cluster_daily_history: ClusterDailyHistoryRepo
    trends: TrendsRepo
    scheduler: SchedulerRepo

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
