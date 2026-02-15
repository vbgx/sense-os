from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ingestion_worker.normalize.clean_text import clean_text


@dataclass(frozen=True)
class NormalizedSignal:
    source: str
    external_id: str
    content: str
    url: Optional[str]
    created_at: Optional[datetime]


def normalize_reddit_item(*, guid: str, title: str, summary: str, link: str, created_at) -> NormalizedSignal:
    text = clean_text(f"{title}\n\n{summary}")
    return NormalizedSignal(
        source="reddit",
        external_id=guid,
        content=text,
        url=link,
        created_at=created_at,
    )
