from __future__ import annotations

from typing import Dict
from ingestion_worker.normalize.clean_text import clean_text
from ingestion_worker.adapters.producthunt.extract import extract_comment_like_sections


def map_producthunt_entry(entry: dict, *, vertical_id: int) -> Dict:
    guid = entry["guid"]
    title = entry["title"]
    summary = entry["summary"]
    url = entry["link"]

    description_text = extract_comment_like_sections(summary)
    content = clean_text(f"{title}\n\n{description_text}".strip())

    return {
        "vertical_id": int(vertical_id),
        "source": "producthunt",
        "external_id": f"ph:{guid}",
        "content": content,
        "url": url,
    }
