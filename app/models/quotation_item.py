"""QuotationItem model."""
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.measurement_item import MeasurementItem
    from app.models.product import Product
    from app.models.quotation import Quotation


class QuotationItem(BaseEntity):
    """
    Quotation line item.

    Represents one product entry within a Quotation (e.g., "5x Sliding Window").

    IMPORTANT: Width and height are NOT stored here — measurements belong
    to MeasurementItem (linked via quotation_item_id).
    """

    __tablename__ = "quotation_items"

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    quotation: Mapped["Quotation"] = relationship(
        "Quotation",
        back_populates="items",
        lazy="joined",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="quotation_items",
        lazy="joined",
    )
    measurement_items: Mapped[list["MeasurementItem"]] = relationship(
        "MeasurementItem",
        back_populates="quotation_item",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<QuotationItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
