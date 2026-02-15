from __future__ import annotations

from db.seed import seed_verticals
from db.repos import verticals as vertical_repo


def test_seed_verticals_creates_once(db_session):
    created = seed_verticals(names=["alpha", "beta"])
    assert created == 2

    created_again = seed_verticals(names=["alpha", "beta"])
    assert created_again == 0

    names = {v.name for v in vertical_repo.get_all(db_session)}
    assert {"alpha", "beta"}.issubset(names)
