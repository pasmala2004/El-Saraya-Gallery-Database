"""Pydantic v2 schemas for the Customer module."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    """Payload for creating a customer."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "full_name": "Ahmed Hassan",
                    "phone_number": "01012345678",
                    "alternative_phone": "+20 100 987 6543",
                    "address": "15 Tahrir Street, Apt 4",
                    "city": "Cairo",
                    "location_url": "https://maps.google.com/?q=30.0444,31.2357",
                    "notes": "Prefers morning appointments",
                }
            ]
        }
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Customer's full legal or display name.",
        examples=["Ahmed Hassan"],
    )
    phone_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Primary phone number (Egyptian formats accepted; stored normalized).",
        examples=["01012345678"],
    )
    alternative_phone: str | None = Field(
        default=None,
        max_length=50,
        description="Optional secondary phone number.",
        examples=["+20 100 987 6543"],
    )
    address: str | None = Field(
        default=None,
        description="Street address or delivery location text.",
        examples=["15 Tahrir Street, Apt 4"],
    )
    city: str | None = Field(
        default=None,
        max_length=100,
        description="City or area name.",
        examples=["Cairo"],
    )
    location_url: str | None = Field(
        default=None,
        max_length=500,
        description="Optional Google Maps (or similar) location URL.",
        examples=["https://maps.google.com/?q=30.0444,31.2357"],
    )
    notes: str | None = Field(
        default=None,
        description="Internal free-text notes about the customer.",
        examples=["Prefers morning appointments"],
    )


class CustomerUpdate(BaseModel):
    """Payload for updating a customer (partial — omit fields to leave unchanged)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "full_name": "Ahmed Hassan",
                    "phone_number": "+201012345678",
                    "city": "Giza",
                    "notes": "Updated contact preferences",
                }
            ]
        }
    )

    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Customer's full name.",
    )
    phone_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Primary phone number.",
    )
    alternative_phone: str | None = Field(
        default=None,
        max_length=50,
        description="Secondary phone number. Send null to clear.",
    )
    address: str | None = Field(default=None, description="Street address.")
    city: str | None = Field(default=None, max_length=100, description="City name.")
    location_url: str | None = Field(
        default=None,
        max_length=500,
        description="Maps URL. Send null to clear.",
    )
    notes: str | None = Field(default=None, description="Internal notes.")


class CustomerRead(BaseModel):
    """Customer resource returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(description="Customer primary key.")
    full_name: str
    phone_number: str = Field(description="Normalized primary phone number.")
    alternative_phone: str | None = None
    address: str | None = None
    city: str | None = None
    location_url: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    """Paginated customer list envelope."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "id": "11111111-1111-1111-1111-111111111111",
                            "full_name": "Ahmed Hassan",
                            "phone_number": "+201012345678",
                            "alternative_phone": None,
                            "address": "15 Tahrir Street",
                            "city": "Cairo",
                            "location_url": None,
                            "notes": None,
                            "created_at": "2026-07-18T12:00:00Z",
                            "updated_at": "2026-07-18T12:00:00Z",
                        }
                    ],
                    "total": 1,
                    "limit": 50,
                    "offset": 0,
                }
            ]
        }
    )

    items: list[CustomerRead] = Field(description="Customers for the current page.")
    total: int = Field(description="Total rows matching filters (before pagination).")
    limit: int = Field(description="Page size applied to this response.")
    offset: int = Field(description="Number of rows skipped.")
