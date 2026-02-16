from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence


@dataclass(frozen=True)
class SignalCandidate:
    """
    Minimal normalized candidate used for ranking representative signals.
    Keep this deterministic and independent from DB access.
    """
    signal_id: str
    user_id: str | None
    distance_to_centroid: float | None  # smaller = more representative
    severity_score: int | None          # higher = better
    engagement: int | None              # higher = better


def _to_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default


def _to_float(x: Any, default: float | None = None) -> float | None:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _safe_user_id(payload: dict[str, Any]) -> str | None:
    # common shapes
    for k in ("user_id", "author_id", "author", "user"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _extract_engagement(payload: dict[str, Any]) -> int:
    # prefer already computed "engagement"
    if "engagement" in payload:
        return _to_int(payload.get("engagement"), 0)
    # else compute from common fields
    up = _to_int(payload.get("upvotes"), 0)
    cm = _to_int(payload.get("comments"), 0)
    rp = _to_int(payload.get("replies"), 0)
    # deterministic linear combination (v1)
    return up + cm + rp


def _extract_distance(payload: dict[str, Any]) -> float | None:
    # accept multiple keys
    for k in ("distance_to_centroid", "centroid_distance", "distance"):
        if k in payload:
            return _to_float(payload.get(k), None)
    return None


def _extract_severity(payload: dict[str, Any]) -> int:
    # accept multiple keys
    for k in ("severity_score", "pain_severity", "severity"):
        if k in payload:
            return _to_int(payload.get(k), 0)
    return 0


def build_candidates(signals: Iterable[dict[str, Any]]) -> list[SignalCandidate]:
    out: list[SignalCandidate] = []
    for s in signals:
        sid = s.get("signal_id") or s.get("id")
        if not isinstance(sid, str) or not sid.strip():
            continue
        out.append(
            SignalCandidate(
                signal_id=sid.strip(),
                user_id=_safe_user_id(s),
                distance_to_centroid=_extract_distance(s),
                severity_score=_extract_severity(s),
                engagement=_extract_engagement(s),
            )
        )
    return out


def rank_representative_signal_ids(
    candidates: Sequence[SignalCandidate],
    k: int = 5,
    per_user_cap: int = 1,
) -> list[str]:
    """
    Deterministic ranking:
      1) distance_to_centroid ASC (None -> worst)
      2) severity_score DESC
      3) engagement DESC
      4) signal_id ASC (stability tie-break)

    Diversity constraint:
      - avoid selecting more than `per_user_cap` per user_id
      - if not enough signals, relax the constraint deterministically
    """
    def sort_key(c: SignalCandidate) -> tuple:
        dist = c.distance_to_centroid
        # None distances are treated as very far => worst
        dist_key = dist if dist is not None else 1e18
        sev = c.severity_score if c.severity_score is not None else 0
        eng = c.engagement if c.engagement is not None else 0
        return (dist_key, -sev, -eng, c.signal_id)

    ordered = sorted(candidates, key=sort_key)

    selected: list[str] = []
    per_user_count: dict[str, int] = {}

    # pass 1: enforce diversity
    for c in ordered:
        if len(selected) >= k:
            break
        uid = c.user_id
        if uid is None:
            # no user info => always allowed (still stable)
            selected.append(c.signal_id)
            continue
        n = per_user_count.get(uid, 0)
        if n >= per_user_cap:
            continue
        per_user_count[uid] = n + 1
        selected.append(c.signal_id)

    # pass 2: if we still lack signals, relax constraint (stable)
    if len(selected) < k:
        seen = set(selected)
        for c in ordered:
            if len(selected) >= k:
                break
            if c.signal_id in seen:
                continue
            selected.append(c.signal_id)
            seen.add(c.signal_id)

    return selected


def attach_representative_signals(
    cluster_payload: dict[str, Any],
    k: int = 5,
    per_user_cap: int = 1,
) -> dict[str, Any]:
    """
    Input cluster_payload is expected to include `signals` list with enough info.
    Output cluster_payload contains:
      - top_signal_ids (list[str]) for persistence
      - representative_signals (subset of original signals) for API usage
    """
    signals = cluster_payload.get("signals") or []
    if not isinstance(signals, list) or not signals:
        out = dict(cluster_payload)
        out["top_signal_ids"] = []
        out["representative_signals"] = []
        return out

    candidates = build_candidates([s for s in signals if isinstance(s, dict)])
    top_ids = rank_representative_signal_ids(candidates, k=k, per_user_cap=per_user_cap)
    top_set = set(top_ids)

    reps: list[dict[str, Any]] = []
    for s in signals:
        if not isinstance(s, dict):
            continue
        sid = s.get("signal_id") or s.get("id")
        if isinstance(sid, str) and sid in top_set:
            reps.append(s)

    # stable order: same as top_ids
    reps_by_id = { (r.get("signal_id") or r.get("id")): r for r in reps if isinstance((r.get("signal_id") or r.get("id")), str) }
    reps_sorted = [reps_by_id[sid] for sid in top_ids if sid in reps_by_id]

    out = dict(cluster_payload)
    out["top_signal_ids"] = top_ids
    out["representative_signals"] = reps_sorted
    return out
