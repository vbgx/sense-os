from typing import Any

from sense_queue.worker_base import Worker
from clustering_worker.pipeline.run_clustering import run_clustering


class ClusteringWorker(Worker):
    def load(self, batch_ctx: dict[str, Any]):
        return batch_ctx

    def process(self, items):
        return run_clustering(items)

    def persist(self, outputs):
        return None
