from __future__ import annotations

from typing import Dict
from ingestion_worker.normalize.clean_text import clean_text
from ingestion_worker.normalize.dates import to_utc_datetime
from ingestion_worker.adapters.indiehackers.language import detect_language


def map_indiehackers_entry(entry: dict, *, vertical_id: int) -> Dict:
    guid = entry["guid"]
    title = entry["title"]
    summary = entry["summary"]
    url = entry["link"]
    published = entry.get("published")
    content = clean_text(f"{title}\n\n{summary}".strip())
    language = detect_language(content)

    data = {
        "vertical_id": int(vertical_id),
        "source": "indiehackers",
        "external_id": f"ih:{guid}",
        "content": content,
        "url": url,
        "language": language,
    }
    if published:
        data["created_at"] = to_utc_datetime(published)
    return data
