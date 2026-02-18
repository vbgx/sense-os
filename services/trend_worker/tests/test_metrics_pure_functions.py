import inspect
from datetime import date, timedelta

from trend_worker.metrics.types import DailyPoint

from trend_worker.metrics import (
    breakout,
    daily,
    declining,
    emerging,
    half_life,
    opportunity_window,
    saturation,
    velocity,
    volatility,
)


def _history(n: int = 30):
    start = date(2026, 1, 1)
    xs = []
    for i in range(n):
        xs.append(DailyPoint(day=start + timedelta(days=i), count=float(i % 10 + 1)))
    return xs


def test_metrics_are_deterministic():
    h = _history()

    mods = [
        breakout,
        daily,
        declining,
        emerging,
        half_life,
        opportunity_window,
        saturation,
        velocity,
        volatility,
    ]

    for m in mods:
        a = m.compute(h)
        b = m.compute(h)
        assert a == b


def test_metrics_have_no_side_effect_imports():
    forbidden_tokens = [
        "datetime.now",
        "time.time",
        "random",
        "os.environ",
        "SessionLocal",
        "sqlalchemy",
        "db.",
        "requests",
        "httpx",
    ]

    mods = [
        breakout,
        daily,
        declining,
        emerging,
        half_life,
        opportunity_window,
        saturation,
        velocity,
        volatility,
    ]

    for m in mods:
        src = inspect.getsource(m)
        for tok in forbidden_tokens:
            assert tok not in src
