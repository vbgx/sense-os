from db.adapters.trends import get_trends_adapter  # noqa: F401
from db.init_db import init_db  # noqa: F401
from db.uow import SqlAlchemyUnitOfWork


def create_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork()
