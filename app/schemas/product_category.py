"""Pydantic v2 schemas for ProductCategory."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCategoryCreate(BaseModel):
    """Payload for creating a product category."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"name": "Windows"}]
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique category name.",
        examples=["Windows"],
    )


class ProductCategoryRead(BaseModel):
    """Product category resource."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class ProductCategoryListResponse(BaseModel):
    """Paginated category list envelope."""

    items: list[ProductCategoryRead]
    total: int
    limit: int
    offset: int
