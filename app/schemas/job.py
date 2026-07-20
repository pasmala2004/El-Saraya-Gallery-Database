"""Job schemas for request/response validation."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enums.job import JobStatus


class JobCreate(BaseModel):
    """Create job from approved quotation."""

    quotation_id: UUID = Field(..., description="Quotation UUID (must be approved)")
    notes: str | None = Field(None, description="Initial job notes", max_length=5000)


class JobUpdate(BaseModel):
    """Update job dates and notes."""

    measurement_date: date | None = Field(None, description="Measurement date")
    production_start: date | None = Field(None, description="Production start date")
    production_end: date | None = Field(None, description="Production end date")
    installation_date: date | None = Field(None, description="Scheduled installation date")
    delivery_date: date | None = Field(None, description="Delivery date")
    notes: str | None = Field(None, description="Job notes", max_length=5000)


class JobStatusUpdate(BaseModel):
    """Update job status."""

    status: JobStatus = Field(..., description="New job status")


class JobRead(BaseModel):
    """Job response."""

    id: UUID
    quotation_id: UUID
    status: JobStatus
    measurement_date: date | None
    production_start: date | None
    production_end: date | None
    installation_date: date | None
    delivery_date: date | None
    completion_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated job list."""

    items: list[JobRead]
    total: int
    limit: int
    offset: int
