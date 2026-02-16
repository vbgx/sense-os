from __future__ import annotations

import hashlib
import json
import os
from datetime import date, timedelta
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from db.settings import DATABASE_URL, REDIS_URL

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def _default_day_iso() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


class TrendsAdapter:
    def __init__(self) -> None:
        dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL") or DATABASE_URL
        if not dsn:
            raise RuntimeError("POSTGRES_DSN (or DATABASE_URL) is required")

        self._engine = create_engine(dsn, pool_pre_ping=True, future=True)
        self._Session = sessionmaker(bind=self._engine, autoflush=False, autocommit=False, future=True)

        self._cache_enabled = _env_bool("TRENDS_CACHE_ENABLED", default=False)
        self._cache_ttl_s = int(os.getenv("TRENDS_CACHE_TTL_S", "60"))
        self._redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS_DSN") or REDIS_URL

        self._redis = None
        if self._cache_enabled and redis is not None:
            self._redis = redis.Redis.from_url(self._redis_url, decode_responses=True)

    def _cache_key(self, prefix: str, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        h = hashlib.sha1(raw).hexdigest()
        return f"trends:{prefix}:{h}"

    def _cache_get(self, key: str) -> Any | None:
        if not self._redis:
            return None
        try:
            v = self._redis.get(key)
            return None if v is None else json.loads(v)
        except Exception:
            return None

    def _cache_set(self, key: str, value: Any) -> None:
        if not self._redis:
            return
        try:
            self._redis.setex(key, self._cache_ttl_s, json.dumps(value, separators=(",", ":")))
        except Exception:
            pass

    def list_kind(self, kind: str, q) -> dict[str, Any]:
        return self._list_kind(kind, q)

    def list_top_pains(self, q) -> dict[str, Any]:
        cache_payload = {
            "kind": "top_pains",
            "vertical_id": q.vertical_id,
            "limit": q.limit,
            "offset": q.offset,
            "min_exploitability": q.min_exploitability,
            "max_exploitability": q.max_exploitability,
        }
        ck = self._cache_key("insights", cache_payload)
        cached = self._cache_get(ck)
        if cached is not None:
            return cached

        where_extra, params = self._exploitability_filter_sql(q.min_exploitability, q.max_exploitability)

        with self._Session() as s:
            total = s.execute(
                text(
                    f"""
                    SELECT COUNT(*) AS n
                    FROM pain_clusters c
                    WHERE c.vertical_id = :vertical_id
                    {where_extra}
                    """
                ),
                {"vertical_id": q.vertical_id, **params},
            ).scalar_one()

            rows = (
                s.execute(
                    text(
                        f"""
                        SELECT
                            c.id AS cluster_id,
                            c.vertical_id,
                            c.title,
                            c.exploitability_score,
                            c.exploitability_tier,
                            c.exploitability_pain_strength,
                            c.exploitability_timing_strength,
                            c.exploitability_risk_penalty,
                            c.exploitability_version
                        FROM pain_clusters c
                        WHERE c.vertical_id = :vertical_id
                        {where_extra}
                        ORDER BY c.exploitability_score DESC, c.id ASC
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    {"vertical_id": q.vertical_id, "limit": q.limit, "offset": q.offset, **params},
                )
                .mappings()
                .all()
            )

            items: list[dict[str, Any]] = []
            for r in rows:
                items.append(
                    {
                        "cluster_id": str(r["cluster_id"]),
                        "vertical_id": int(r["vertical_id"]),
                        "title": r.get("title"),
                        "exploitability": {
                            "exploitability_score": int(r.get("exploitability_score") or 0),
                            "tier": str(r.get("exploitability_tier") or "IGNORE"),
                            "pain_strength": float(r.get("exploitability_pain_strength") or 0.0),
                            "timing_strength": float(r.get("exploitability_timing_strength") or 0.0),
                            "risk_penalty": float(r.get("exploitability_risk_penalty") or 0.0),
                            "version": str(r.get("exploitability_version") or ""),
                        },
                    }
                )

            out = {"page": {"limit": q.limit, "offset": q.offset, "total": int(total)}, "items": items}

        self._cache_set(ck, out)
        return out

    def get_cluster_detail(
        self,
        *,
        vertical_id: int,
        cluster_id: str,
        day: str,
        sparkline_days: int,
    ) -> dict[str, Any]:
        day = day or _default_day_iso()
        cache_payload = {"vertical_id": vertical_id, "cluster_id": cluster_id, "day": day, "sparkline_days": sparkline_days}
        ck = self._cache_key("cluster_detail", cache_payload)
        cached = self._cache_get(ck)
        if cached is not None:
            return cached

        cid = int(cluster_id)

        with self._Session() as s:
            row = (
                s.execute(
                    text(
                        """
                        SELECT
                            m.day,
                            c.vertical_id,
                            m.cluster_id,
                            c.title,
                            m.emerging AS score,
                            m.velocity,
                            COALESCE(m.source_count, 1) AS source_count,

                            c.exploitability_score,
                            c.exploitability_tier,
                            c.exploitability_pain_strength,
                            c.exploitability_timing_strength,
                            c.exploitability_risk_penalty,
                            c.exploitability_version
                        FROM cluster_daily_metrics m
                        JOIN pain_clusters c ON c.id = m.cluster_id
                        WHERE m.day = :day
                          AND c.vertical_id = :vertical_id
                          AND m.cluster_id = :cluster_id
                        LIMIT 1
                        """
                    ),
                    {"day": day, "vertical_id": vertical_id, "cluster_id": cid},
                )
                .mappings()
                .first()
            )

            if not row:
                out_nf = {
                    "cluster_id": str(cluster_id),
                    "vertical_id": int(vertical_id),
                    "day": day,
                    "title": None,
                    "score": 0.0,
                    "velocity": 0.0,
                    "source_count": 1,
                    "breakdown": {},
                    "sparkline": [],
                    "meta": {"not_found": True},
                    "exploitability": {
                        "exploitability_score": 0,
                        "tier": "IGNORE",
                        "pain_strength": 0.0,
                        "timing_strength": 0.0,
                        "risk_penalty": 0.0,
                        "version": "",
                    },
                }
                self._cache_set(ck, out_nf)
                return out_nf

            spark = self._sparkline(s, cluster_id=cid, vertical_id=vertical_id, day=day, days=sparkline_days)

            out = {
                "cluster_id": str(row["cluster_id"]),
                "vertical_id": int(row["vertical_id"]),
                "day": str(row["day"]),
                "title": row.get("title"),
                "score": float(row.get("score") or 0.0),
                "velocity": float(row.get("velocity") or 0.0),
                "source_count": int(row.get("source_count") or 1),
                "breakdown": {},
                "sparkline": spark,
                "meta": {},
                "exploitability": {
                    "exploitability_score": int(row.get("exploitability_score") or 0),
                    "tier": str(row.get("exploitability_tier") or "IGNORE"),
                    "pain_strength": float(row.get("exploitability_pain_strength") or 0.0),
                    "timing_strength": float(row.get("exploitability_timing_strength") or 0.0),
                    "risk_penalty": float(row.get("exploitability_risk_penalty") or 0.0),
                    "version": str(row.get("exploitability_version") or ""),
                },
            }

        self._cache_set(ck, out)
        return out

    def _list_kind(self, kind: str, q) -> dict[str, Any]:
        cache_payload = {
            "kind": kind,
            "vertical_id": q.vertical_id,
            "day": q.day,
            "limit": q.limit,
            "offset": q.offset,
            "sparkline_days": q.sparkline_days,
            "min_exploitability": q.min_exploitability,
            "max_exploitability": q.max_exploitability,
        }
        ck = self._cache_key("list", cache_payload)
        cached = self._cache_get(ck)
        if cached is not None:
            return cached

        order_sql = self._order_by(kind)
        where_extra, params = self._exploitability_filter_sql(q.min_exploitability, q.max_exploitability)

        with self._Session() as s:
            total = s.execute(
                text(
                    f"""
                    SELECT COUNT(*) AS n
                    FROM cluster_daily_metrics m
                    JOIN pain_clusters c ON c.id = m.cluster_id
                    WHERE m.day = :day AND c.vertical_id = :vertical_id
                    {where_extra}
                    """
                ),
                {"day": q.day, "vertical_id": q.vertical_id, **params},
            ).scalar_one()

            rows = (
                s.execute(
                    text(
                        f"""
                        SELECT
                            m.cluster_id,
                            c.vertical_id,
                            c.title,
                            m.emerging AS score,
                            m.velocity,
                            COALESCE(m.source_count, 1) AS source_count,

                            c.exploitability_score,
                            c.exploitability_tier,
                            c.exploitability_pain_strength,
                            c.exploitability_timing_strength,
                            c.exploitability_risk_penalty,
                            c.exploitability_version
                        FROM cluster_daily_metrics m
                        JOIN pain_clusters c ON c.id = m.cluster_id
                        WHERE m.day = :day AND c.vertical_id = :vertical_id
                        {where_extra}
                        {order_sql}
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    {"day": q.day, "vertical_id": q.vertical_id, "limit": q.limit, "offset": q.offset, **params},
                )
                .mappings()
                .all()
            )

            items: list[dict[str, Any]] = []
            for r in rows:
                cid = int(r["cluster_id"])
                spark = self._sparkline(s, cluster_id=cid, vertical_id=q.vertical_id, day=q.day, days=q.sparkline_days)
                items.append(
                    {
                        "cluster_id": str(cid),
                        "vertical_id": int(r["vertical_id"]),
                        "title": r.get("title"),
                        "score": float(r.get("score") or 0.0),
                        "velocity": float(r.get("velocity") or 0.0),
                        "source_count": int(r.get("source_count") or 1),
                        "sparkline": spark,
                        "exploitability": {
                            "exploitability_score": int(r.get("exploitability_score") or 0),
                            "tier": str(r.get("exploitability_tier") or "IGNORE"),
                            "pain_strength": float(r.get("exploitability_pain_strength") or 0.0),
                            "timing_strength": float(r.get("exploitability_timing_strength") or 0.0),
                            "risk_penalty": float(r.get("exploitability_risk_penalty") or 0.0),
                            "version": str(r.get("exploitability_version") or ""),
                        },
                    }
                )

            out = {"page": {"limit": q.limit, "offset": q.offset, "total": int(total)}, "items": items}

        self._cache_set(ck, out)
        return out

    def _exploitability_filter_sql(self, min_e: int | None, max_e: int | None) -> tuple[str, dict[str, Any]]:
        clauses: list[str] = []
        params: dict[str, Any] = {}
        if min_e is not None:
            clauses.append("AND c.exploitability_score >= :min_exploitability")
            params["min_exploitability"] = int(min_e)
        if max_e is not None:
            clauses.append("AND c.exploitability_score <= :max_exploitability")
            params["max_exploitability"] = int(max_e)
        return ("\n" + "\n".join(clauses) if clauses else ""), params

    def _order_by(self, kind: str) -> str:
        if kind == "emerging":
            return "ORDER BY m.velocity DESC, m.emerging DESC, m.cluster_id ASC"
        if kind == "declining":
            return "ORDER BY m.declining DESC, m.velocity ASC, m.cluster_id ASC"
        return "ORDER BY m.emerging DESC, m.velocity DESC, m.cluster_id ASC"

    def _sparkline(self, session, *, cluster_id: int, vertical_id: int, day: str, days: int) -> list[dict[str, Any]]:
        try:
            end = date.fromisoformat(day)
        except Exception:
            end = date.today() - timedelta(days=1)
        start = end - timedelta(days=max(0, days - 1))

        rows = (
            session.execute(
                text(
                    """
                    SELECT m.day, m.velocity AS v
                    FROM cluster_daily_metrics m
                    JOIN pain_clusters c ON c.id = m.cluster_id
                    WHERE c.vertical_id = :vertical_id
                      AND m.cluster_id = :cluster_id
                      AND m.day BETWEEN :start_day AND :end_day
                    ORDER BY m.day ASC
                    """
                ),
                {
                    "vertical_id": vertical_id,
                    "cluster_id": cluster_id,
                    "start_day": start.isoformat(),
                    "end_day": end.isoformat(),
                },
            )
            .mappings()
            .all()
        )

        return [{"day": str(r["day"]), "v": float(r.get("v") or 0.0)} for r in rows]


_default_adapter: TrendsAdapter | None = None
_default_dsn: str | None = None


def get_trends_adapter() -> TrendsAdapter:
    global _default_adapter, _default_dsn
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL") or DATABASE_URL
    if _default_adapter is None or _default_dsn != dsn:
        _default_adapter = TrendsAdapter()
        _default_dsn = dsn
    return _default_adapter
