"""Measurement schemas for request/response validation."""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    """Create measurement for a job."""

    visit_date: date | None = Field(None, description="Measurement visit date")
    measured_by: str | None = Field(None, description="Person who took measurements", max_length=255)
    notes: str | None = Field(None, description="Measurement notes", max_length=5000)


class MeasurementUpdate(BaseModel):
    """Update measurement details."""

    visit_date: date | None = Field(None, description="Measurement visit date")
    measured_by: str | None = Field(None, description="Person who took measurements", max_length=255)
    notes: str | None = Field(None, description="Measurement notes", max_length=5000)


class MeasurementItemRead(BaseModel):
    """Measurement item response (nested in measurement)."""

    id: UUID
    measurement_id: UUID
    quotation_item_id: UUID
    room_name: str | None
    piece_number: str | None
    width: Decimal | None
    height: Decimal | None
    quantity: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeasurementRead(BaseModel):
    """Measurement response."""

    id: UUID
    job_id: UUID
    measurement_number: int
    visit_date: date | None
    measured_by: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeasurementReadWithItems(MeasurementRead):
    """Measurement response with items included."""

    items: list[MeasurementItemRead] = []


class MeasurementListResponse(BaseModel):
    """Paginated measurement list."""

    items: list[MeasurementRead]
    total: int
    limit: int
    offset: int


class MeasurementItemCreate(BaseModel):
    """Create measurement item."""

    quotation_item_id: UUID = Field(..., description="Quotation item UUID")
    room_name: str | None = Field(None, description="Room name", max_length=100)
    piece_number: str | None = Field(None, description="Piece number", max_length=100)
    width: Decimal | None = Field(None, description="Width measurement", ge=0)
    height: Decimal | None = Field(None, description="Height measurement", ge=0)
    quantity: int = Field(1, description="Quantity measured", gt=0)
    notes: str | None = Field(None, description="Item notes", max_length=5000)


class MeasurementItemUpdate(BaseModel):
    """Update measurement item."""

    quotation_item_id: UUID | None = Field(None, description="Quotation item UUID")
    room_name: str | None = Field(None, description="Room name", max_length=100)
    piece_number: str | None = Field(None, description="Piece number", max_length=100)
    width: Decimal | None = Field(None, description="Width measurement", ge=0)
    height: Decimal | None = Field(None, description="Height measurement", ge=0)
    quantity: int | None = Field(None, description="Quantity measured", gt=0)
    notes: str | None = Field(None, description="Item notes", max_length=5000)

