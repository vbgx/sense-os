import os

ENV = os.getenv("ENV", "dev")

DEFAULT_VERTICAL_NAME = os.getenv("DEFAULT_VERTICAL_NAME", "default")

# Default ingest query (V0). Later: per-vertical config.
DEFAULT_REDDIT_QUERY = os.getenv("DEFAULT_REDDIT_QUERY", "billing software")

DEFAULT_INGEST_LIMIT = int(os.getenv("DEFAULT_INGEST_LIMIT", "25"))

DEFAULT_PROCESS_LIMIT = int(os.getenv("DEFAULT_PROCESS_LIMIT", "200"))
DEFAULT_PROCESS_OFFSET = int(os.getenv("DEFAULT_PROCESS_OFFSET", "0"))
