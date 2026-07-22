"""Payment model."""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
)
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
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "payment_order",
            name="uq_payments_job_id_payment_order",
        ),
        CheckConstraint("payment_order > 0", name="ck_payments_payment_order_positive"),
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonneg"),
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_payments_percentage_range",
        ),
        Index("ix_payments_status", "status"),
        Index("ix_payments_due_date", "due_date"),
    )

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
        # Types are created by Alembic migrations — do not auto-create from ORM
        ENUM(
            PaymentType,
            name="payment_type",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        ENUM(
            PaymentMethod,
            name="payment_method",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        ENUM(
            PaymentStatus,
            name="payment_status",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default="pending",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships — lazy="select" by default; use selectinload/joinedload in queries
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="payments",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, job_id={self.job_id}, type={self.payment_type.value}, status={self.status.value})>"
