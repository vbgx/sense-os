from typing import Sequence

from adapters._base import FetchContext
from domain import RawSignal

from .client import StackExchangeClient
from .map import map_question_to_signal


def fetch_signals(*, client: StackExchangeClient, ctx: FetchContext) -> Sequence[RawSignal]:
    questions = client.search_questions(
        query=ctx.vertical_id,
        limit=ctx.limit,
        cursor=ctx.cursor,
    )
    return [map_question_to_signal(q) for q in questions]
