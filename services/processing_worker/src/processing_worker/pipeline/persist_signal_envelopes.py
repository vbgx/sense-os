from __future__ import annotations

from typing import Any, Iterable

from db.repos import signals as signals_repo


def _maybe_call(repo: Any, fn_names: list[str], *args: Any, **kwargs: Any) -> bool:
    for name in fn_names:
        fn = getattr(repo, name, None)
        if callable(fn):
            fn(*args, **kwargs)
            return True
    return False


def persist_signal_envelopes_in_session(db: Any, envelopes: Iterable[Any]) -> None:
    """
    Persist signal attributes back to the Signal table using a single DB session.
    Best-effort: if a repo method doesn't exist, we skip it (no crash).
    """
    for e in envelopes:
        sid = getattr(e, "signal_id", None)
        if sid is None:
            continue

        # language
        if getattr(e, "language_code", None):
            _maybe_call(
                signals_repo,
                ["set_language_code", "set_signal_language_code"],
                db,
                signal_id=int(sid),
                language_code=str(e.language_code),
            )

        # spam
        if getattr(e, "spam_score", None) is not None:
            _maybe_call(
                signals_repo,
                ["set_spam_score", "set_signal_spam_score"],
                db,
                signal_id=int(sid),
                spam_score=int(e.spam_score),
            )

        # quality
        if getattr(e, "signal_quality", None) is not None:
            _maybe_call(
                signals_repo,
                ["set_signal_quality", "set_quality_score", "set_signal_quality_score"],
                db,
                signal_id=int(sid),
                signal_quality=int(e.signal_quality),
            )

        # vertical auto
        if getattr(e, "vertical_auto", None):
            _maybe_call(
                signals_repo,
                ["set_vertical_auto", "set_vertical_auto_classification", "set_signal_vertical_auto"],
                db,
                signal_id=int(sid),
                vertical_auto=str(e.vertical_auto),
            )
