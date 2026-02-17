from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.ports import UnitOfWork
from domain.versions import SCORING_VERSION


@dataclass
class MetaUseCase:
  uow: UnitOfWork

  def get_status(self) -> dict[str, Any]:
    last_run = None
    total_clusters = 0
    total_signals_7d = 0

    # Be resilient: meta must never crash the UI
    try:
      with self.uow:
        # optional scheduler
        scheduler = getattr(self.uow, "scheduler", None)
        if scheduler is not None:
          try:
            last_run = scheduler.get_last_run()
          except Exception:
            last_run = None

        # optional repo methods (depending on adapter maturity)
        pain_clusters = getattr(self.uow, "pain_clusters", None)
        if pain_clusters is not None and hasattr(pain_clusters, "count"):
          total_clusters = int(pain_clusters.count())

        signals = getattr(self.uow, "signals", None)
        if signals is not None and hasattr(signals, "count_last_days"):
          total_signals_7d = int(signals.count_last_days(days=7))

    except Exception:
      # don't leak infra errors to the UI layer
      pass

    return {
      "status": "ok",
      "last_run_at": last_run,
      "scoring_version": SCORING_VERSION,
      "total_signals_7d": total_signals_7d,
      "total_clusters": total_clusters,
    }
