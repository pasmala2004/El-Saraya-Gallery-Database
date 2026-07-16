"""ActivityLog model."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.job import Job


class ActivityLog(BaseEntity):
    """
    Activity log entity.

    Tracks actions and events related to a Job throughout its lifecycle.
    Used for audit trail and activity history.
    """

    __tablename__ = "activity_logs"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="activity_logs",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, job_id={self.job_id}, action='{self.action}')>"
