from typing import Any

from sense_queue.worker_base import Worker
from trend_worker.pipeline.compute_trends import compute_trends


class TrendWorker(Worker):
    def load(self, batch_ctx: dict[str, Any]):
        return batch_ctx

    def process(self, items):
        return compute_trends(items)

    def persist(self, outputs):
        return None
