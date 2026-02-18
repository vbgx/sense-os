# api_gateway/src/api_gateway/routers/overview.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from api_gateway.dependencies import get_insights_use_case, get_meta_use_case
from api_gateway.schemas.overview import (
    OverviewOut,
    OverviewKpiOut,
    OverviewBreakoutOut,
    OverviewHeatmapCellOut,
    OverviewStatus,
)
from application.use_cases.insights import InsightsUseCase
from application.use_cases.meta import MetaUseCase

# Reuse the exact same vertical config loader logic as /verticals
# (duplicated minimally here to avoid importing private helpers)
import json
import os
from pathlib import Path

router = APIRouter(prefix="/overview", tags=["overview"])


# ---- vertical config loading (minimal, JSON-only) ----
_DEFAULT_VERTICALS_DIR = Path(os.getenv("VERTICALS_DIR", "/app/config/verticals"))
if _DEFAULT_VERTICALS_DIR.exists():
    VERTICALS_DIR = _DEFAULT_VERTICALS_DIR
else:
    repo_root = Path(__file__).resolve().parents[5]
    fallback = repo_root / "config" / "verticals"
    VERTICALS_DIR = fallback if fallback.exists() else _DEFAULT_VERTICALS_DIR

INDEX_FILE_JSON = VERTICALS_DIR / "verticals.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _load_enabled_vertical_ids() -> List[str]:
    """
    Returns enabled vertical string ids from config/verticals/verticals.json
    """
    data = _read_json(INDEX_FILE_JSON)
    items = data.get("verticals")
    out: List[str] = []
    if isinstance(items, list):
        for entry in items:
            if not isinstance(entry, dict):
                continue
            if entry.get("enabled", True) is False:
                continue
            vid = entry.get("id")
            if vid:
                out.append(str(vid))
    return out


# ---- duck-typing helpers ----
def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def _to_str(v: Any, default: str = "") -> str:
    try:
        if v is None:
            return default
        return str(v)
    except Exception:
        return default


def _status_from_item(item: Any) -> OverviewStatus:
    # best effort mapping
    raw = _to_str(_get(item, "status", ""), "").lower()
    if raw in {"hot", "emerging", "stable", "saturated", "declining"}:
        return OverviewStatus(raw)  # type: ignore[arg-type]
    # fallback heuristic
    momentum = _to_float(_get(item, "momentum_7d", None), 0.0)
    if momentum >= 10:
        return OverviewStatus.hot
    if momentum > 0:
        return OverviewStatus.emerging
    return OverviewStatus.stable


@router.get("", response_model=OverviewOut)
def get_overview(
    *,
    meta: MetaUseCase = Depends(get_meta_use_case),
    insights: InsightsUseCase = Depends(get_insights_use_case),
    # allows you to scope if needed; otherwise uses config verticals count only
    limit_breakouts: int = Query(default=10, ge=1, le=50),
):
    now = datetime.now(timezone.utc).isoformat()

    # KPI 1: total active verticals (config-based)
    active_vertical_ids = _load_enabled_vertical_ids()
    total_active_verticals = float(len(active_vertical_ids))

    # KPI 2/3: emerging + declining (insights-based)
    # NOTE: these endpoints already exist and don’t require a vertical_id
    emerging = insights.get_emerging_opportunities(vertical_id=None, limit=200, offset=0)
    declining = insights.get_declining_risks(vertical_id=None, limit=200, offset=0)

    emerging_count = float(len(emerging or []))
    declining_count = float(len(declining or []))

    # KPI 4/5: placeholders for now (you can wire real math later)
    # - volatility index could be computed from score dispersion across verticals
    # - signal growth could come from signals ingestion stats
    volatility_index = 0.0
    signal_growth_7d = 0.0

    # Breakouts: best-effort from "emerging opportunities" items
    # We map “whatever fields exist” -> stable breakout schema.
    breakouts: List[OverviewBreakoutOut] = []
    for i, it in enumerate((emerging or [])[: int(limit_breakouts)]):
        breakouts.append(
            OverviewBreakoutOut(
                rank=i + 1,
                vertical_id=_to_str(_get(it, "vertical_id", None), "unknown"),
                vertical_label=_to_str(_get(it, "vertical_label", None), "Unknown"),
                score=_to_float(_get(it, "score", _get(it, "pain_score", 0.0)), 0.0),
                momentum_7d=_to_float(_get(it, "momentum_7d", 0.0), 0.0),
                confidence=_to_float(_get(it, "confidence", 0.5), 0.5),
                tier=_get(it, "tier", None),
                status=_status_from_item(it),
            )
        )

    # Heatmap: stable contract, empty for now (wire later from vertical meta + breakouts)
    heatmap: List[OverviewHeatmapCellOut] = []

    # Meta status exists; we keep it future-proof without depending on its internal fields.
    _ = meta.get_status()

    kpis = [
        OverviewKpiOut(key="total_active_verticals", label="Active Verticals", value=total_active_verticals, delta_7d=None),
        OverviewKpiOut(key="emerging_clusters_7d", label="Emerging (7d)", value=emerging_count, delta_7d=None),
        OverviewKpiOut(key="declining_clusters", label="Declining", value=declining_count, delta_7d=None),
        OverviewKpiOut(key="opportunity_volatility_index", label="Volatility Index", value=volatility_index, delta_7d=None),
        OverviewKpiOut(key="signal_growth_7d", label="Signal Growth (7d)", value=signal_growth_7d, delta_7d=None),
    ]

    return OverviewOut(
        updated_at=now,
        kpis=kpis,
        breakouts=breakouts,
        heatmap=heatmap,
    )
