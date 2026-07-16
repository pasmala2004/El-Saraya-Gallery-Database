"""Payment model."""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, SmallInteger, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType

if TYPE_CHECKING:
    from app.models.job import Job


class Payment(BaseEntity):
    """
    Payment entity.

    Represents a payment installment for a Job.  Multiple payments can exist
    per Job, sequenced by `payment_order`.

    payment_type: Business milestone (Deposit, Production, Final)
    payment_method: How the customer pays (Cash, Bank Transfer, etc.)
    """

    __tablename__ = "payments"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_order: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        ENUM(PaymentType, name="payment_type", create_type=True),
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        ENUM(PaymentMethod, name="payment_method", create_type=True),
        nullable=False,
    )
    percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        ENUM(PaymentStatus, name="payment_status", create_type=True),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="payments",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, job_id={self.job_id}, type={self.payment_type.value}, status={self.status.value})>"
