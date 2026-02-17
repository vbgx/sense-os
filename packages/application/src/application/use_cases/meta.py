from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.ports import UnitOfWork
from domain.versions import DEFAULT_ALGO_VERSION


@dataclass
class MetaUseCase:
    uow: UnitOfWork

    def get_status(self) -> dict[str, Any]:
        with self.uow:
            # last_run_at (optional / best-effort)
            last_run_at = None
            scheduler = getattr(self.uow, "scheduler", None)
            if scheduler is not None and hasattr(scheduler, "get_last_run"):
                last_run_at = scheduler.get_last_run()

            # total_clusters (best-effort: count() else len(list()))
            pain_clusters_repo = self.uow.pain_clusters
            if hasattr(pain_clusters_repo, "count"):
                total_clusters = pain_clusters_repo.count()
            else:
                total_clusters = len(pain_clusters_repo.list())

            # total_signals_7d (best-effort; fallback 0 if not available)
            signals_repo = self.uow.signals
            if hasattr(signals_repo, "count_last_days"):
                total_signals_7d = signals_repo.count_last_days(days=7)
            else:
                total_signals_7d = 0

        return {
            "last_run_at": last_run_at,
            "scoring_version": DEFAULT_ALGO_VERSION,
            "total_signals_7d": total_signals_7d,
            "total_clusters": total_clusters,
        }
