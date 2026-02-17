from __future__ import annotations

from typing import Callable, Optional, Type

from sqlalchemy.orm import Session

from db.adapters.cluster_daily_history import ClusterDailyHistoryAdapter
from db.adapters.pain_clusters import PainClustersAdapter
from db.adapters.pain_instances import PainInstancesAdapter
from db.adapters.signals import SignalsAdapter
from db.adapters.trends import get_trends_adapter
from db.adapters.verticals import VerticalsAdapter
from db.session import SessionLocal


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory
        self.session: Optional[Session] = None

        self.pain_clusters = None
        self.pain_instances = None
        self.signals = None
        self.verticals = None
        self.cluster_daily_history = None
        self.trends = get_trends_adapter()

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.pain_clusters = PainClustersAdapter(self.session)
        self.pain_instances = PainInstancesAdapter(self.session)
        self.signals = SignalsAdapter(self.session)
        self.verticals = VerticalsAdapter(self.session)
        self.cluster_daily_history = ClusterDailyHistoryAdapter(self.session)
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb) -> None:
        if self.session is None:
            return
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
            self.session = None

    def commit(self) -> None:
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()
