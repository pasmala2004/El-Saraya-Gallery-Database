"""MeasurementItem model."""
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.measurement import Measurement
    from app.models.quotation_item import QuotationItem


class MeasurementItem(BaseEntity):
    """
    Measurement item entity.

    Represents the actual on-site measurements for one product within a
    Measurement visit.  Each item links back to a QuotationItem and records
    physical dimensions (width, height), room location, piece number, and quantity.
    """

    __tablename__ = "measurement_items"

    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quotation_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotation_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    room_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    piece_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    measurement: Mapped["Measurement"] = relationship(
        "Measurement",
        back_populates="items",
        lazy="joined",
    )
    quotation_item: Mapped["QuotationItem"] = relationship(
        "QuotationItem",
        back_populates="measurement_items",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<MeasurementItem(id={self.id}, measurement_id={self.measurement_id}, piece='{self.piece_number}')>"
