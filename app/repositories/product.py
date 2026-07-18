"""Product repository."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import (
    FilterParams,
    Pagination,
    Sorting,
    apply_filters,
    apply_pagination,
    apply_sorting,
)
from app.models.product import Product
from app.repositories.base import GenericRepository

PRODUCT_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "category_id",
        "active",
        "created_at",
        "updated_at",
    }
)


@dataclass(frozen=True, slots=True)
class ProductFilters:
    """
    Product list filters.

    ``name`` is applied through the shared ``FilterParams`` / ``apply_filters``
    helpers (ILIKE). ``category_id`` and ``active`` use equality predicates
    composed in this repository (``FilterParams.active()`` is a method name,
    so an ``active`` field cannot live on a FilterParams subclass).
    """

    name: str | None = None
    category_id: uuid.UUID | None = None
    active: bool | None = None


class ProductRepository(GenericRepository[Product]):
    """Data access for ``Product`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Product)

    async def get_by_category_and_name(
        self,
        category_id: uuid.UUID,
        name: str,
    ) -> Product | None:
        """Return the product with ``name`` in ``category_id``, or ``None``."""
        result = await self._session.execute(
            select(Product).where(
                Product.category_id == category_id,
                Product.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: ProductFilters | None = None,
    ) -> tuple[list[Product], int]:
        """
        Search products by name / category / active flag.

        Reuses generic pagination, sorting, and name-filter helpers.
        """
        effective_filters = filters or ProductFilters()
        effective_pagination = pagination or Pagination()
        effective_sorting = sorting or Sorting()

        total = await self._count(filters=effective_filters)

        statement = self._filtered_select(effective_filters)
        statement = apply_sorting(
            statement,
            Product,
            effective_sorting,
            allowed_sort_fields=PRODUCT_SORT_FIELDS,
        )
        statement = apply_pagination(statement, effective_pagination)

        result = await self._session.execute(statement)
        return list(result.scalars().all()), total

    async def _count(self, *, filters: ProductFilters) -> int:
        statement = select(func.count()).select_from(Product)
        statement = self._apply_product_filters(statement, filters)
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    def _filtered_select(self, filters: ProductFilters) -> Select:
        statement = self.base_select()
        return self._apply_product_filters(statement, filters)

    def _apply_product_filters(
        self,
        statement: Select,
        filters: ProductFilters,
    ) -> Select:
        # Name → shared ILIKE helper via FilterParams
        statement = apply_filters(
            statement,
            Product,
            FilterParams(name=filters.name),
            field_map={"name": "name"},
        )
        if filters.category_id is not None:
            statement = statement.where(Product.category_id == filters.category_id)
        if filters.active is not None:
            statement = statement.where(Product.active.is_(filters.active))
        return statement
