from typing import List, Dict
from db.session import SessionLocal
from db.repos import signals as signals_repo

class SignalsWriter:
    def __init__(self):
        self.db = SessionLocal()

    def insert_many(self, signals: List[Dict]) -> tuple[int, int]:
        inserted = 0
        deduped = 0
        for signal in signals:
            obj, created = signals_repo.create_if_absent(
                self.db,
                vertical_id=signal["vertical_id"],
                source=signal["source"],
                external_id=signal["external_id"],
                content=signal["content"],
                url=signal["url"],
            )
            if created:
                inserted += 1
            else:
                deduped += 1

        self.db.commit()
        return inserted, deduped
