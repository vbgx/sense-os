from __future__ import annotations

from typing import Any

from db.models import PainInstance, Signal
from db.session import SessionLocal


def load_instances(job: dict[str, Any]) -> list[dict[str, Any]]:
    vertical_db_id = int(job.get("vertical_db_id") or 1)

    db = SessionLocal()
    try:
        rows = (
            db.query(PainInstance, Signal)
            .join(Signal, Signal.id == PainInstance.signal_id)
            .filter(PainInstance.vertical_id == vertical_db_id)
            .order_by(PainInstance.id.asc())
            .all()
        )
        instances: list[dict[str, Any]] = []
        for pain, signal in rows:
            instances.append(
                {
                    "id": int(pain.id),
                    "pain_instance_id": int(pain.id),
                    "signal_id": int(pain.signal_id),
                    "vertical_db_id": int(vertical_db_id),
                    "content": signal.content,
                    "text": signal.content,
                }
            )
        return instances
    finally:
        db.close()
