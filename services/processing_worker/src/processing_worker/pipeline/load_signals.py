from __future__ import annotations

from db.session import SessionLocal
from db.repos import signals as signals_repo


def load_batch(
    vertical_db_id: int,
    limit: int,
    offset: int,
    language_codes: list[str] | None = None,
):
    db = SessionLocal()
    try:
        rows = signals_repo.list_by_vertical_db_id(
            db,
            vertical_db_id=vertical_db_id,
            limit=limit,
            offset=offset,
            language_codes=language_codes,
        )
        out: list[dict] = []
        for s in rows:
            if isinstance(s, dict):
                out.append(s)
                continue
            out.append(
                {
                    "id": int(getattr(s, "id")),
                    "text": str(getattr(s, "content", "")),
                    "title": "",
                    "source": str(getattr(s, "source", "")),
                }
            )
        return out
    finally:
        db.close()


def _parse_language_codes(raw: object) -> list[str] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        codes = [c.strip() for c in raw.split(",") if c.strip()]
        return codes or None
    if isinstance(raw, (list, tuple)):
        codes = [str(c).strip() for c in raw if str(c).strip()]
        return codes or None
    return None


def load_signals(job: dict) -> list:
    vertical_db_id = int(job.get("vertical_db_id") or 1)
    limit = int(job.get("limit") or job.get("batch_size") or 200)
    offset = int(job.get("offset") or 0)
    language_codes = _parse_language_codes(job.get("language_codes") or job.get("languages"))
    return load_batch(vertical_db_id, limit, offset, language_codes=language_codes)
