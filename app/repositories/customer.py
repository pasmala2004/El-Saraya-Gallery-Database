"""Customer repository — reference data-access implementation for ERP modules."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import FilterParams, Pagination, Sorting, apply_filters
from app.models.customer import Customer
from app.repositories.base import GenericRepository

CUSTOMER_FILTER_FIELD_MAP: dict[str, str] = {
    "name": "full_name",
    "phone": "phone_number",
    "city": "city",
}

CUSTOMER_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "full_name",
        "phone_number",
        "city",
        "created_at",
        "updated_at",
    }
)


class CustomerRepository(GenericRepository[Customer]):
    """Data access for ``Customer`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_phone(self, phone_number: str) -> Customer | None:
        """Return the customer with an exact ``phone_number``, or ``None``."""
        result = await self._session.execute(
            select(Customer).where(Customer.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
    ) -> tuple[list[Customer], int]:
        """
        Search customers with optional filters, sorting, and pagination.

        Reuses ``FilterParams`` / ``apply_query_options`` (ILIKE via the
        shared ``apply_filters`` helper). Returns ``(items, total)``.
        """
        effective_filters = filters or FilterParams()
        effective_pagination = pagination or Pagination()
        effective_sorting = sorting or Sorting()

        total = await self._count(filters=effective_filters)
        items = await self.get_all(
            pagination=effective_pagination,
            sorting=effective_sorting,
            filters=effective_filters,
            allowed_sort_fields=CUSTOMER_SORT_FIELDS,
            filter_field_map=CUSTOMER_FILTER_FIELD_MAP,
        )
        return items, total

    async def _count(self, *, filters: FilterParams) -> int:
        statement = select(func.count()).select_from(Customer)
        statement = apply_filters(
            statement,
            Customer,
            filters,
            field_map=CUSTOMER_FILTER_FIELD_MAP,
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())
