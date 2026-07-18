"""ProductCategory application service."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError, ValidationError
from app.core.query import FilterParams, Pagination, Sorting
from app.models.product_category import ProductCategory
from app.repositories.product_category import ProductCategoryRepository
from app.services.base import BaseService


class ProductCategoryService(BaseService[ProductCategory]):
    """Product category use-cases."""

    def __init__(
        self,
        session: AsyncSession,
        repository: ProductCategoryRepository,
    ) -> None:
        super().__init__(session, repository, entity_name="ProductCategory")
        self._categories = repository

    async def get_category(self, category_id: uuid.UUID) -> ProductCategory:
        return await self.get_by_id(category_id)

    async def list_categories(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
    ) -> tuple[list[ProductCategory], int]:
        return await self._categories.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def create_category(self, data: dict[str, Any]) -> ProductCategory:
        name = (data.get("name") or "").strip()
        if not name:
            raise ValidationError("name must not be empty", field="name")

        existing = await self._categories.get_by_name(name)
        if existing is not None:
            raise DuplicateEntityError("ProductCategory", "name", name)

        category = ProductCategory(name=name)
        return await self.create(category, commit=True)
