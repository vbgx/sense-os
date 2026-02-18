import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    user_agent: str
    redis_dsn: str | None


settings = Settings(
    user_agent=os.getenv(
        "INGESTION_USER_AGENT",
        "sense-os/0.1 (contact: unknown)",
    ),
    redis_dsn=os.getenv("REDIS_DSN"),
)

DEFAULT_SOURCES = os.getenv(
    "INGESTION_DEFAULT_SOURCES",
    "github,hackernews,stackexchange",
).split(",")
