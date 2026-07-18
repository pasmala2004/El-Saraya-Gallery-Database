"""Measurement model."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.measurement_item import MeasurementItem


class Measurement(BaseEntity):
    """
    Measurement entity.

    Represents a site visit for taking measurements.  A Job can have multiple
    measurements if re-measurement is needed (tracked via measurement_number).
    """

    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "measurement_number",
            name="uq_measurements_job_id_measurement_number",
        ),
        CheckConstraint(
            "measurement_number > 0",
            name="ck_measurements_measurement_number_positive",
        ),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    measurement_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
    )
    visit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    measured_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships — lazy="select" by default; use selectinload/joinedload in queries
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="measurements",
        lazy="select",
    )
    items: Mapped[list["MeasurementItem"]] = relationship(
        "MeasurementItem",
        back_populates="measurement",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Measurement(id={self.id}, job_id={self.job_id}, number={self.measurement_number})>"
