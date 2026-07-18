"""Product application service."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError, EntityNotFoundError, ValidationError
from app.core.query import Pagination, Sorting
from app.models.product import Product
from app.repositories.product import ProductFilters, ProductRepository
from app.repositories.product_category import ProductCategoryRepository
from app.services.base import BaseService


class ProductService(BaseService[Product]):
    """
    Product catalog use-cases.

    Pricing is intentionally out of scope — unit prices live on quotation items.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: ProductRepository,
        category_repository: ProductCategoryRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Product")
        self._products = repository
        self._categories = category_repository or ProductCategoryRepository(session)

    async def get_product(self, product_id: uuid.UUID) -> Product:
        return await self.get_by_id(product_id)

    async def list_products(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: ProductFilters | None = None,
    ) -> tuple[list[Product], int]:
        return await self._products.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def create_product(self, data: dict[str, Any]) -> Product:
        payload = self._normalize_payload(data, require_name=True, require_category=True)
        await self._ensure_category_exists(payload["category_id"])
        await self._ensure_name_unique(payload["category_id"], payload["name"])

        product = Product(
            category_id=payload["category_id"],
            name=payload["name"],
            active=payload.get("active", True),
        )
        return await self.create(product, commit=True)

    async def update_product(
        self,
        product_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Product:
        product = await self.get_product(product_id)
        payload = self._normalize_payload(
            data,
            require_name=False,
            require_category=False,
        )

        new_category_id = payload.get("category_id", product.category_id)
        new_name = payload.get("name", product.name)

        if "category_id" in payload:
            await self._ensure_category_exists(new_category_id)

        if "name" in payload or "category_id" in payload:
            await self._ensure_name_unique(
                new_category_id,
                new_name,
                exclude_id=product.id,
            )

        for field, value in payload.items():
            setattr(product, field, value)

        return await self.update(product, commit=True)

    def _normalize_payload(
        self,
        data: dict[str, Any],
        *,
        require_name: bool,
        require_category: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        if "name" in data or require_name:
            if data.get("name") is None and require_name:
                raise ValidationError("name is required", field="name")
            if "name" in data and data["name"] is not None:
                name = str(data["name"]).strip()
                if not name:
                    raise ValidationError("name must not be empty", field="name")
                payload["name"] = name

        if "category_id" in data or require_category:
            if data.get("category_id") is None and require_category:
                raise ValidationError("category_id is required", field="category_id")
            if "category_id" in data and data["category_id"] is not None:
                payload["category_id"] = uuid.UUID(str(data["category_id"]))

        if "active" in data and data["active"] is not None:
            payload["active"] = bool(data["active"])

        return payload

    async def _ensure_category_exists(self, category_id: uuid.UUID) -> None:
        category = await self._categories.get_by_id(category_id)
        if category is None:
            raise EntityNotFoundError("ProductCategory", category_id)

    async def _ensure_name_unique(
        self,
        category_id: uuid.UUID,
        name: str,
        *,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        existing = await self._products.get_by_category_and_name(category_id, name)
        if existing is None:
            return
        if exclude_id is not None and existing.id == exclude_id:
            return
        raise DuplicateEntityError(
            "Product",
            "name",
            name,
            message=(
                f"Product with name={name!r} already exists in category "
                f"{category_id}"
            ),
        )
