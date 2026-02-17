from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Ensure local packages resolve without a virtualenv install.
for rel in (
    "apps/api_gateway/src",
    "packages/application/src",
    "packages/db/src",
    "packages/domain/src",
    "packages/queue/src",
    "services/scheduler/src",
):
    path = ROOT / rel
    if path.exists():
        sys.path.insert(0, str(path))


def _configure_env() -> Path:
    raw = os.getenv("E2E_DB_PATH")
    if raw:
        db_path = Path(raw).expanduser()
        if not db_path.is_absolute():
            db_path = (ROOT / db_path).resolve()
    else:
        db_path = ROOT / ".tmp" / "sense_os_e2e.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    dsn = f"sqlite+pysqlite:///{db_path}"
    os.environ["DATABASE_URL"] = dsn
    os.environ["POSTGRES_DSN"] = dsn
    return db_path


def _seed_data() -> None:
    from sqlalchemy.orm import sessionmaker

    from db.adapters.trends import reset_trends_adapter
    from db.engine import get_engine, reset_engine
    from db.models import Base, ClusterDailyHistory, PainCluster, Vertical

    reset_trends_adapter()
    reset_engine()
    engine = get_engine()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        vertical = Vertical(id=1, name="SaaS")
        session.add(vertical)

        cluster_a = PainCluster(
            vertical_id=1,
            cluster_version="v1",
            cluster_key="cluster-a",
            title="Onboarding drop-off",
            size=120,
            cluster_summary="Teams lose users during onboarding due to unclear activation steps.",
            exploitability_score=85,
            exploitability_tier="STRONG_BUILD",
            opportunity_window_status="EARLY",
            breakout_score=72,
            confidence_score=82,
            severity_score=65,
            recurrence_score=58,
            monetizability_score=61,
            saturation_score=22,
            contradiction_score=9,
            competitive_heat_score=34,
            dominant_persona="Product leader",
            key_phrases_json=json.dumps(["onboarding", "activation", "time-to-value"]),
            top_signal_ids_json=json.dumps([101, 102, 103]),
        )
        cluster_b = PainCluster(
            vertical_id=1,
            cluster_version="v1",
            cluster_key="cluster-b",
            title="Support backlog",
            size=80,
            cluster_summary="Support teams are overwhelmed and SLA breaches are rising.",
            exploitability_score=70,
            exploitability_tier="INVESTIGATE",
            opportunity_window_status="PEAK",
            breakout_score=41,
            confidence_score=63,
            severity_score=52,
            recurrence_score=47,
            monetizability_score=49,
            saturation_score=30,
            contradiction_score=14,
            competitive_heat_score=41,
            dominant_persona="Support lead",
            key_phrases_json=json.dumps(["support tickets", "triage", "sla"]),
            top_signal_ids_json=json.dumps([201, 202]),
        )

        session.add_all([cluster_a, cluster_b])
        session.flush()

        today = date.today()
        timeline = []
        for i in range(6):
            day = today - timedelta(days=6 - i)
            timeline.append(
                ClusterDailyHistory(
                    cluster_id=str(cluster_a.id),
                    day=day,
                    volume=12 + i,
                    growth_rate=0.08 * i,
                    velocity=0.12 * i,
                    breakout_flag=i >= 3,
                )
            )
        session.add_all(timeline)

        session.commit()
    finally:
        session.close()


def main() -> None:
    _configure_env()
    _seed_data()

    host = os.getenv("E2E_API_HOST", "127.0.0.1")
    port = int(os.getenv("E2E_API_PORT", "8000"))
    log_level = os.getenv("E2E_API_LOG_LEVEL", "info")

    import uvicorn

    uvicorn.run("api_gateway.main:app", host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()
