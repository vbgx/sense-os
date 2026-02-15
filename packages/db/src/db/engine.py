from __future__ import annotations

from sqlalchemy import create_engine

from db.settings import DATABASE_URL

# pool_pre_ping avoids stale connections in docker restarts
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
