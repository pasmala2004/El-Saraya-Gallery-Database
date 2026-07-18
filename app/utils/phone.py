"""
Egyptian phone number normalization.

Assumptions
-----------
1. Primary market is Egypt (country code ``+20``).
2. Mobile numbers are commonly written as:
   - ``01xxxxxxxxx`` (11 digits, local)
   - ``+201xxxxxxxxx`` / ``00201xxxxxxxxx`` (international)
   - with spaces, dashes, or parentheses for readability
3. Stored form is E.164-like for Egypt: ``+20`` followed by the national
   number **without** a leading ``0`` (e.g. ``+201012345678``).
4. Non-Egyptian numbers that already start with ``+`` (other country codes)
   are cleaned of formatting characters but otherwise left intact.
5. Empty / whitespace-only input raises ``ValidationError``.
6. This helper does **not** verify carrier prefixes or check digit length
   beyond a minimum sanity check (at least 8 digits after cleaning).
"""
from __future__ import annotations

import re

from app.core.exceptions import ValidationError

_DIGITS_ONLY = re.compile(r"\D")

def normalize_phone_number(raw: str) -> str:
    """
    Normalize a phone number for storage and uniqueness checks.

    Steps
    -----
    1. Trim surrounding whitespace.
    2. Remove spaces, dashes, and parentheses (and any other non-digit
       characters except a leading ``+``).
    3. Map common Egyptian local / international prefixes to ``+20…``.
    4. Reject values that are empty or too short after cleaning.

    Examples
    --------
    >>> normalize_phone_number("010 1234 5678")
    '+201012345678'
    >>> normalize_phone_number("+20 10-1234-5678")
    '+201012345678'
    >>> normalize_phone_number("00201012345678")
    '+201012345678'
    """
    if raw is None:
        raise ValidationError("phone number is required", field="phone_number")

    trimmed = raw.strip()
    if not trimmed:
        raise ValidationError("phone number must not be empty", field="phone_number")

    # Keep a single leading + if present; strip other punctuation.
    has_plus = trimmed.startswith("+")
    digits = _DIGITS_ONLY.sub("", trimmed)

    if not digits:
        raise ValidationError("phone number must contain digits", field="phone_number")

    if digits.startswith("00"):
        # International prefix 00 → treat as +
        digits = digits[2:]
        has_plus = True

    # Egyptian local mobile/landline: leading 0 + national number
    if not has_plus and digits.startswith("0"):
        digits = "20" + digits[1:]
        has_plus = True

    # Already includes country code 20 without +
    if not has_plus and digits.startswith("20") and len(digits) >= 10:
        has_plus = True

    if len(digits) < 8:
        raise ValidationError(
            "phone number is too short after normalization",
            field="phone_number",
        )

    return f"+{digits}" if has_plus or digits.startswith("20") else digits
