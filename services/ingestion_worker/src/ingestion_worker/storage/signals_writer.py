from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from db.session import SessionLocal
from db.repos import signals as signals_repo


class SignalsWriter:
    def insert_many(self, signals: List[Dict]) -> tuple[int, int]:
        inserted = 0
        deduped = 0
        db = SessionLocal()
        try:
            for signal in signals:
                created_at: Optional[datetime] = signal.get("created_at")
                _, created = signals_repo.create_if_absent(
                    db,
                    vertical_id=signal["vertical_id"],
                    source=signal["source"],
                    external_id=signal["external_id"],
                    content=signal["content"],
                    url=signal.get("url"),
                    created_at=created_at,
                )
                if created:
                    inserted += 1
                else:
                    deduped += 1

            db.commit()
            return inserted, deduped
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
