from __future__ import annotations

from dataclasses import dataclass

from application.ports import NotFoundError, UnitOfWork
from domain.versions import TAXONOMY_VERSION


@dataclass
class VerticalsUseCase:
    uow: UnitOfWork

    def list_verticals(self):
        with self.uow:
            return self.uow.verticals.get_all()

    def create_vertical(self, *, name: str):
        with self.uow:
            return self.uow.verticals.create(name=name)

    def ensure_vertical(self, *, name: str) -> int:
        with self.uow:
            v = self.uow.verticals.get_by_name(name)
            if v is None:
                v = self.uow.verticals.create(name=name)
        return int(getattr(v, "id"))

    def build_ventureos_export(
        self,
        *,
        vertical_id: str,
        taxonomy_version: str | None = None,
    ) -> dict[str, object]:
        vertical_key = str(vertical_id or "").strip()
        if not vertical_key:
            raise NotFoundError("Vertical not found")

        with self.uow:
            vertical = self.uow.verticals.get_by_name(vertical_key)
            if vertical is None:
                raise NotFoundError("Vertical not found")

            vertical_db_id = int(getattr(vertical, "id"))
            clusters = self.uow.pain_clusters.list_top_pains(
                vertical_id=str(vertical_db_id),
                tier=None,
                limit=1,
                offset=0,
                opportunity_window_status=None,
            )
            if not clusters:
                raise NotFoundError("No clusters found for vertical")
            cluster_id = str(getattr(clusters[0], "id"))

        from application.use_cases.insights import InsightsUseCase

        insights = InsightsUseCase(uow=self.uow)
        return insights.export_ventureos_payload(
            cluster_id,
            vertical_id=vertical_key,
            taxonomy_version=taxonomy_version or TAXONOMY_VERSION,
        )
