from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    url = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    signal_quality_score = Column(Integer, nullable=True, index=True)
    language_code = Column(String(8), nullable=True, index=True)

    spam_score = Column(Integer, nullable=True, index=True)
