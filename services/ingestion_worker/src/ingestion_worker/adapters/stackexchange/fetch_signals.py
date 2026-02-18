from __future__ import annotations

from typing import Any

from ingestion_worker.adapters._base import FetchContext


def fetch_signals(*, ctx: FetchContext, **kwargs: Any) -> list[dict[str, Any]]:
    """
    Backward-compatible entrypoint expected by StackExchangeAdapter.

    Delegates to the actual implementation module.
    """
    # Most common patterns: client.py / api.py / fetch.py / impl.py
    for mod_name in ("client", "api", "fetch", "impl", "service"):
        try:
            mod = __import__(f"ingestion_worker.adapters.stackexchange.{mod_name}", fromlist=["fetch_signals"])
            fn = getattr(mod, "fetch_signals", None)
            if callable(fn):
                return fn(ctx=ctx, **kwargs)
        except Exception:
            continue

    raise ImportError(
        "stackexchange.fetch_signals: no implementation found. "
        "Expected a fetch_signals(ctx=..., ...) in one of: client.py/api.py/fetch.py/impl.py/service.py"
    )
