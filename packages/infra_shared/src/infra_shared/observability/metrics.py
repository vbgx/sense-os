from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict


class MetricsRegistry:
    def __init__(self) -> None:
        self.counters: Dict[str, int] = defaultdict(int)
        self.timings: Dict[str, list[float]] = defaultdict(list)

    def incr(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def timing(self, name: str, duration_seconds: float) -> None:
        self.timings[name].append(duration_seconds)

    def timer(self, name: str):
        start = time.perf_counter()

        class _Timer:
            def __enter__(self_inner):
                return None

            def __exit__(self_inner, exc_type, exc_val, exc_tb):
                duration = time.perf_counter() - start
                self.timing(name, duration)

        return _Timer()


metrics = MetricsRegistry()
