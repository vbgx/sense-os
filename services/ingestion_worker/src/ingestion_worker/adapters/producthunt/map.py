from __future__ import annotations

from typing import Dict
from ingestion_worker.normalize.clean_text import clean_text
from ingestion_worker.normalize.dates import to_utc_datetime
from ingestion_worker.adapters.producthunt.extract import extract_comment_like_sections


def map_producthunt_entry(
    entry: dict,
    *,
    vertical_id: str,
    vertical_db_id: int | None,
    taxonomy_version: str | None,
) -> Dict:
    guid = entry["guid"]
    title = entry["title"]
    summary = entry["summary"]
    url = entry["link"]
    published = entry.get("published")
    description_text = extract_comment_like_sections(summary)
    content = clean_text(f"{title}\n\n{description_text}".strip())

    data = {
        "vertical_id": str(vertical_id),
        "source": "producthunt",
        "external_id": f"ph:{guid}",
        "content": content,
        "url": url,
    }
    if vertical_db_id is not None:
        data["vertical_db_id"] = int(vertical_db_id)
    if taxonomy_version is not None:
        data["taxonomy_version"] = str(taxonomy_version)
    if published:
        data["created_at"] = to_utc_datetime(published)
    return data
