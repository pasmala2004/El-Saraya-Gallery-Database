"""Unit tests for Egyptian phone normalization."""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.utils.phone import normalize_phone_number


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("01012345678", "+201012345678"),
        ("010 1234 5678", "+201012345678"),
        ("+20 10-1234-5678", "+201012345678"),
        ("(010) 1234-5678", "+201012345678"),
        ("00201012345678", "+201012345678"),
    ],
)
def test_normalize_egyptian_phones(raw: str, expected: str) -> None:
    assert normalize_phone_number(raw) == expected


def test_normalize_rejects_empty() -> None:
    with pytest.raises(ValidationError):
        normalize_phone_number("   ")
