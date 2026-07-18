"""Pydantic v2 schemas for Product (no pricing fields)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Payload for creating a catalog product."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "category_id": "22222222-2222-2222-2222-222222222222",
                    "name": "Sliding Window",
                    "active": True,
                }
            ]
        }
    )

    category_id: uuid.UUID = Field(
        ...,
        description="Existing product category UUID.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name (unique within its category).",
        examples=["Sliding Window"],
    )
    active: bool = Field(
        default=True,
        description="Whether the product is available for new quotations.",
    )


class ProductUpdate(BaseModel):
    """Partial update payload for a product."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Sliding Window Pro",
                    "active": False,
                }
            ]
        }
    )

    category_id: uuid.UUID | None = Field(
        default=None,
        description="Move the product to another category.",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Product name (unique within its category).",
    )
    active: bool | None = Field(
        default=None,
        description="Active flag for catalog visibility.",
    )


class ProductRead(BaseModel):
    """Product resource returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Paginated product list envelope."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "id": "33333333-3333-3333-3333-333333333333",
                            "category_id": "22222222-2222-2222-2222-222222222222",
                            "name": "Sliding Window",
                            "active": True,
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

    items: list[ProductRead]
    total: int
    limit: int
    offset: int
