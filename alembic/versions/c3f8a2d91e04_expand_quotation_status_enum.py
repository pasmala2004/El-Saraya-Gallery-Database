"""Expand quotation_status enum for full quotation lifecycle.

Revision ID: c3f8a2d91e04
Revises: b2c4e8f91a03
Create Date: 2026-07-18 20:55:00.000000

Adds waiting_for_measurement, measured, under_negotiation, and expired
to the existing quotation_status PostgreSQL enum.

Existing rows are preserved — all prior values (draft, sent, approved,
rejected, cancelled) remain valid and are not rewritten.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c3f8a2d91e04"
down_revision: Union[str, None] = "b2c4e8f91a03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_VALUES: tuple[str, ...] = (
    "waiting_for_measurement",
    "measured",
    "under_negotiation",
    "expired",
)


def upgrade() -> None:
    # PostgreSQL requires autocommit for ADD VALUE on enums in some versions.
    with op.get_context().autocommit_block():
        for value in _NEW_VALUES:
            op.execute(
                f"ALTER TYPE quotation_status ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # PostgreSQL cannot drop individual enum values safely without recreating
    # the type and rewriting every dependent column. Existing quotation rows
    # may already use the new values, so this migration is intentionally
    # irreversible.
    pass
