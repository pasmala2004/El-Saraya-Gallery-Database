"""Quotation model."""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.enums.quotation import QuotationStatus

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.job import Job
    from app.models.quotation_item import QuotationItem


class Quotation(BaseEntity):
    """
    Quotation entity.

    A formal price estimate sent to a customer.  Can contain multiple line
    items (QuotationItem) and may eventually become a Job if approved.
    """

    __tablename__ = "quotations"

    quotation_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quotation_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[QuotationStatus] = mapped_column(
        ENUM(QuotationStatus, name="quotation_status", create_type=True),
        nullable=False,
        default=QuotationStatus.DRAFT,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    final_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="quotations",
        lazy="joined",
    )
    items: Mapped[list["QuotationItem"]] = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    job: Mapped["Job | None"] = relationship(
        "Job",
        back_populates="quotation",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Quotation(id={self.id}, number='{self.quotation_number}', status={self.status.value})>"
