from typing import Any

from sense_queue.worker_base import Worker
from processing_worker.pipeline.handle_job import handle_job


class ProcessingWorker(Worker):
    def load(self, batch_ctx: dict[str, Any]):
        return batch_ctx

    def process(self, items):
        return handle_job(items)

    def persist(self, outputs):
        return None
