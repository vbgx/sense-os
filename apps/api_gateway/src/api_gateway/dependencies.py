from __future__ import annotations

from fastapi import Depends

from application.ports import UnitOfWork
from application.use_cases.clusters import ClustersUseCase
from application.use_cases.insights import InsightsUseCase
from application.use_cases.pains import PainsUseCase
from application.use_cases.signals import SignalsUseCase
from application.use_cases.trends import TrendsUseCase
from application.use_cases.verticals import VerticalsUseCase
from db.adapters import create_uow


def get_uow() -> UnitOfWork:
    return create_uow()


def get_clusters_use_case(uow: UnitOfWork = Depends(get_uow)) -> ClustersUseCase:
    return ClustersUseCase(uow=uow)


def get_pains_use_case(uow: UnitOfWork = Depends(get_uow)) -> PainsUseCase:
    return PainsUseCase(uow=uow)


def get_signals_use_case(uow: UnitOfWork = Depends(get_uow)) -> SignalsUseCase:
    return SignalsUseCase(uow=uow)


def get_trends_use_case(uow: UnitOfWork = Depends(get_uow)) -> TrendsUseCase:
    return TrendsUseCase(uow=uow)


def get_insights_use_case(uow: UnitOfWork = Depends(get_uow)) -> InsightsUseCase:
    return InsightsUseCase(uow=uow)


def get_verticals_use_case(uow: UnitOfWork = Depends(get_uow)) -> VerticalsUseCase:
    return VerticalsUseCase(uow=uow)
