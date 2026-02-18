from __future__ import annotations

from typing import Any, Optional


def emit_vector_cache_stats(
    *,
    hits: int,
    misses: int,
    dim: int,
) -> None:
    """
    Best-effort metrics emission.
    If your observability layer exposes counters/gauges, we call them.
    Otherwise: no-op.
    """
    try:
        from clustering_worker.observability import metrics as m  # type: ignore
    except Exception:
        return

    total = hits + misses

    # Common patterns we try (no crash if not present)
    _incr = getattr(m, "incr", None) or getattr(m, "inc", None) or getattr(m, "counter_inc", None)
    _gauge = getattr(m, "gauge", None) or getattr(m, "set_gauge", None) or getattr(m, "set", None)

    if callable(_incr):
        try:
            _incr("vector_cache_hits_total", hits)
            _incr("vector_cache_misses_total", misses)
            _incr("vector_cache_lookups_total", total)
        except Exception:
            pass

    if callable(_gauge):
        try:
            _gauge("vector_dim", dim)
            if total > 0:
                _gauge("vector_cache_hit_rate", float(hits) / float(total))
        except Exception:
            pass
