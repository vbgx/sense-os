from __future__ import annotations

from collections.abc import Callable
from typing import Any, Dict

Job = dict[str, Any]
HandlerFn = Callable[[Job], Any]

_JOB_REGISTRY: Dict[str, HandlerFn] = {}


def _job_name_from_payload(job: Job) -> str | None:
    for k in ("job_type", "type", "name", "job", "kind"):
        v = job.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def handle_job(job: Job, handler: HandlerFn | None = None) -> Any:
    if handler is not None:
        return handler(job)

    name = _job_name_from_payload(job)
    if not name:
        raise TypeError("handle_job() missing handler and job has no job_type/type/name")

    fn = _JOB_REGISTRY.get(name)
    if fn is None:
        raise KeyError(f"unknown job handler: {name}")
    return fn(job)


def job_handler(name_or_fn: str | HandlerFn):
    if callable(name_or_fn):
        fn = name_or_fn
        name = getattr(fn, "__job_name__", fn.__name__)
        _JOB_REGISTRY[str(name)] = fn

        def _wrapped(job: Job) -> Any:
            return fn(job)

        return _wrapped

    name = str(name_or_fn)

    def _decorator(fn: HandlerFn) -> HandlerFn:
        setattr(fn, "__job_name__", name)
        _JOB_REGISTRY[name] = fn

        def _wrapped(job: Job) -> Any:
            return fn(job)

        setattr(_wrapped, "__job_name__", name)
        return _wrapped

    return _decorator
