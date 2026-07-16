"""Report model."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseEntity


class Report(BaseEntity):
    """
    Report entity.

    Tracks generated reports (PDFs, Excel files, etc.) with metadata about
    when they were created and where the file is stored.
    """

    __tablename__ = "reports"

    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, report_date={self.report_date}, file_path='{self.file_path}')>"
