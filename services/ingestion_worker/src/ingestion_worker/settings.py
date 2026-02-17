import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


# Explicitly load .env from service root
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseModel):
    sense_ua: str = os.getenv(
        "SENSE_UA",
        "sense-os/0.1 (ingestion_worker; contact: v.bergeroux@gmail.com)",
    )

    ingestion_limit: int = int(os.getenv("INGESTION_LIMIT", "75"))
    ingestion_limit_max: int = int(os.getenv("INGESTION_LIMIT_MAX", "200"))
    ingestion_min_inserted: int = int(os.getenv("INGESTION_MIN_INSERTED", "50"))
    reddit_rps: float = float(os.getenv("REDDIT_RPS", "1.0"))


settings = Settings()
