from __future__ import annotations


def emit_vector_cache_stats(
    *,
    hits: int,
    misses: int,
    dim: int,
    unique_texts: int | None = None,
    total_items: int | None = None,
) -> None:
    """
    Best-effort metrics emission.

    Tries common counter/gauge APIs exposed by clustering_worker.observability.metrics.
    If not available: no-op.
    """
    try:
        from clustering_worker.observability import metrics as m  # type: ignore
    except Exception:
        return

    total = hits + misses

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
            if unique_texts is not None:
                _gauge("vector_unique_texts", int(unique_texts))
            if total_items is not None:
                _gauge("vector_total_items", int(total_items))
            if unique_texts is not None and total_items is not None and total_items > 0:
                _gauge("vector_dedup_ratio", float(unique_texts) / float(total_items))
        except Exception:
            pass
