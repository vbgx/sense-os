from typing import TYPE_CHECKING

from db.adapters.trends import get_trends_adapter  # noqa: F401
from db.init_db import init_db  # noqa: F401

if TYPE_CHECKING:
    from db.uow import SqlAlchemyUnitOfWork


def create_uow() -> "SqlAlchemyUnitOfWork":
    from db.uow import SqlAlchemyUnitOfWork

    return SqlAlchemyUnitOfWork()
