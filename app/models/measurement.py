"""Measurement model."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, SmallInteger, String, Text
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
    )
    visit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    measured_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="measurements",
        lazy="joined",
    )
    items: Mapped[list["MeasurementItem"]] = relationship(
        "MeasurementItem",
        back_populates="measurement",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Measurement(id={self.id}, job_id={self.job_id}, number={self.measurement_number})>"
