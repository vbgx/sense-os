from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseSettings:
    service_name: str
    environment: str
    log_level: str
    redis_url: str | None
    postgres_dsn: str | None


def load_base_settings(service_name: str) -> BaseSettings:
    return BaseSettings(
        service_name=service_name,
        environment=os.getenv("ENVIRONMENT", "local"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        redis_url=os.getenv("REDIS_URL"),
        postgres_dsn=os.getenv("POSTGRES_DSN"),
    )
