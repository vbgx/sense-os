from pydantic import BaseModel
import os


class Settings(BaseModel):
    # How many items we try to fetch per run (best-effort; source may cap)
    ingestion_limit: int = int(os.getenv("INGESTION_LIMIT", "75"))

    # Safety: hard upper bound to avoid accidental huge runs
    ingestion_limit_max: int = int(os.getenv("INGESTION_LIMIT_MAX", "200"))

    # Minimal expectations for a "healthy" ingestion run
    ingestion_min_inserted: int = int(os.getenv("INGESTION_MIN_INSERTED", "50"))

    # Rate limit (adapter-level should enforce too)
    reddit_rps: float = float(os.getenv("REDDIT_RPS", "1.0"))


settings = Settings()
