"""Job model."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.enums.job import JobStatus

if TYPE_CHECKING:
    from app.models.activity_log import ActivityLog
    from app.models.measurement import Measurement
    from app.models.payment import Payment
    from app.models.quotation import Quotation


class Job(BaseEntity):
    """
    Job entity.

    Created when a Quotation is approved.  Tracks the entire lifecycle from
    measurement through production, installation, and completion.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status", "status"),
    )

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        # Types are created by Alembic migrations — do not auto-create from ORM
        ENUM(
            JobStatus,
            name="job_status",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=JobStatus.PENDING,
        server_default="pending",
    )
    measurement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    production_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    production_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    installation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships — lazy="select" by default; use selectinload/joinedload in queries
    quotation: Mapped["Quotation"] = relationship(
        "Quotation",
        back_populates="job",
        lazy="select",
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select",
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, quotation_id={self.quotation_id}, status={self.status.value})>"
