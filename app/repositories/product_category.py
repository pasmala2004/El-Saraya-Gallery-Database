"""ProductCategory repository."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import FilterParams, Pagination, Sorting, apply_filters
from app.models.product_category import ProductCategory
from app.repositories.base import GenericRepository

CATEGORY_FILTER_FIELD_MAP: dict[str, str] = {
    "name": "name",
}

CATEGORY_SORT_FIELDS: frozenset[str] = frozenset(
    {"id", "name", "created_at", "updated_at"}
)


class ProductCategoryRepository(GenericRepository[ProductCategory]):
    """Data access for ``ProductCategory`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductCategory)

    async def get_by_name(self, name: str) -> ProductCategory | None:
        """Return the category with an exact ``name``, or ``None``."""
        result = await self._session.execute(
            select(ProductCategory).where(ProductCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
    ) -> tuple[list[ProductCategory], int]:
        """Search categories with optional name filter, sorting, and pagination."""
        effective_filters = filters or FilterParams()
        effective_pagination = pagination or Pagination()
        effective_sorting = sorting or Sorting(sort_by="name", sort_order="asc")

        total = await self._count(filters=effective_filters)
        items = await self.get_all(
            pagination=effective_pagination,
            sorting=effective_sorting,
            filters=effective_filters,
            allowed_sort_fields=CATEGORY_SORT_FIELDS,
            filter_field_map=CATEGORY_FILTER_FIELD_MAP,
        )
        return items, total

    async def _count(self, *, filters: FilterParams) -> int:
        statement = select(func.count()).select_from(ProductCategory)
        statement = apply_filters(
            statement,
            ProductCategory,
            filters,
            field_map=CATEGORY_FILTER_FIELD_MAP,
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())
