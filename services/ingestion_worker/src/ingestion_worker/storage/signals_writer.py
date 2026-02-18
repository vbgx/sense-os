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
                vertical_id = signal.get("vertical_id")
                taxonomy_version = signal.get("taxonomy_version")
                vertical_db_id = signal.get("vertical_db_id")
                if not vertical_id or not taxonomy_version:
                    raise ValueError("signal missing vertical_id or taxonomy_version")
                if vertical_db_id is None:
                    raise ValueError("signal missing vertical_db_id")
                _, created = signals_repo.create_if_absent(
                    db,
                    vertical_db_id=vertical_db_id,
                    vertical_id=vertical_id,
                    taxonomy_version=taxonomy_version,
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

    def write_signals(self, items, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, int]:
        """
        Backward-compatible shim for fanout pipeline.
        Accepts a list[dict] payloads and persists them.
        Returns a summary dict (fetched/inserted/skipped) when possible.
        """
        fn = getattr(self, "write", None) or getattr(self, "write_signal_dicts", None) or getattr(self, "insert_signals", None)
        if callable(fn):
            out = fn(items, vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)
            if isinstance(out, dict):
                return out
            return {"fetched": int(len(items)), "inserted": int(len(items)), "skipped": 0}

        # last resort: if there is a per-item writer
        fn1 = getattr(self, "write_one", None) or getattr(self, "write_signal", None)
        if callable(fn1):
            ins = 0
            skip = 0
            for it in items:
                try:
                    ok = fn1(it, vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)
                    ins += 1 if ok else 0
                    skip += 0 if ok else 1
                except Exception:
                    skip += 1
            return {"fetched": int(len(items)), "inserted": int(ins), "skipped": int(skip)}

        raise AttributeError("SignalsWriter: expected write()/write_signal_dicts()/insert_signals() or write_one()")
