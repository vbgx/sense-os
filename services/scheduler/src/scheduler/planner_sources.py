from typing import Any

from ingestion_worker.settings import DEFAULT_SOURCES


def build_ingestion_job(
    vertical_id: str,
    taxonomy_version: str,
    vertical_db_id: int,
    sources: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "vertical_id": vertical_id,
        "taxonomy_version": taxonomy_version,
        "vertical_db_id": vertical_db_id,
        "sources": sources or DEFAULT_SOURCES,
    }
