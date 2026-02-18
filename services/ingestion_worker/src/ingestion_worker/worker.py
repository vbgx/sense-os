from typing import Any

from sense_queue.worker_base import Worker
from ingestion_worker.pipeline.ingest_vertical import ingest_vertical


class IngestionWorker(Worker):
    def load(self, batch_ctx: dict[str, Any]):
        # ici le job contient déjà tout
        return batch_ctx

    def process(self, items):
        return ingest_vertical(items)

    def persist(self, outputs):
        # ingestion_vertical persiste déjà
        return None
