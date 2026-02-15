import os


ENV = os.getenv("ENV", "dev")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://sense:sense@localhost:5432/sense",
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
