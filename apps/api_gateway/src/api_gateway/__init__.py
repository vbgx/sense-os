"""
api_gateway package.

Keep this file lightweight: no heavy imports, no FastAPI app creation,
no router imports (avoid side effects at import time).
"""

from __future__ import annotations

try:
    from importlib.metadata import version as _pkg_version  # py3.8+
except Exception:  # pragma: no cover
    _pkg_version = None  # type: ignore[assignment]

__all__ = ["__version__"]

if _pkg_version is not None:
    try:
        __version__ = _pkg_version("api-gateway")
    except Exception:  # pragma: no cover
        __version__ = "0.0.0"
else:  # pragma: no cover
    __version__ = "0.0.0"
