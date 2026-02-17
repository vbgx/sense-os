import pytest

from domain.models.vertical import VerticalMeta, VerticalTier
from domain.verticals.contract_v1 import validate_vertical_meta, validate_vertical_tier


def test_validate_vertical_meta_accepts_empty():
    meta = validate_vertical_meta(None)
    assert isinstance(meta, VerticalMeta)


def test_validate_vertical_meta_rejects_unknown_keys():
    with pytest.raises(ValueError):
        validate_vertical_meta({"industry": "retail", "unexpected": "value"})


def test_validate_vertical_meta_rejects_non_string_values():
    with pytest.raises(ValueError):
        validate_vertical_meta({"industry": 123})


def test_validate_vertical_tier_accepts_enum_and_string():
    assert validate_vertical_tier(VerticalTier.CORE) == VerticalTier.CORE
    assert validate_vertical_tier("core") == VerticalTier.CORE
    assert validate_vertical_tier("Long_Tail") == VerticalTier.LONG_TAIL


def test_validate_vertical_tier_rejects_invalid_value():
    with pytest.raises(ValueError):
        validate_vertical_tier("invalid-tier")
