"""Quotation repository."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

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
from app.enums.quotation import QuotationStatus
from app.models.quotation import Quotation
from app.repositories.base import GenericRepository

QUOTATION_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "quotation_number",
        "quotation_date",
        "status",
        "total_price",
        "final_price",
        "created_at",
        "updated_at",
    }
)

# API sort aliases → model columns
QUOTATION_SORT_ALIASES: dict[str, str] = {
    "date": "quotation_date",
}


@dataclass(frozen=True, slots=True)
class QuotationFilters:
    """
    Quotation list filters.

    ``status`` / partial ``quotation_number`` reuse ``FilterParams`` where
    practical; customer and date-range predicates are applied explicitly.
    """

    status: QuotationStatus | None = None
    customer_id: uuid.UUID | None = None
    quotation_number: str | None = None
    date_from: date | None = None
    date_to: date | None = None


class QuotationRepository(GenericRepository[Quotation]):
    """Data access for ``Quotation`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Quotation)

    async def get_by_number(self, quotation_number: str) -> Quotation | None:
        result = await self._session.execute(
            select(Quotation).where(Quotation.quotation_number == quotation_number)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: QuotationFilters | None = None,
    ) -> tuple[list[Quotation], int]:
        """Search quotations with status / customer / number / date filters."""
        effective_filters = filters or QuotationFilters()
        effective_pagination = pagination or Pagination()
        effective_sorting = sorting or Sorting(
            sort_by="quotation_date",
            sort_order="desc",
        )

        sort_by = QUOTATION_SORT_ALIASES.get(
            effective_sorting.sort_by,
            effective_sorting.sort_by,
        )
        resolved_sorting = Sorting(
            sort_by=sort_by,
            sort_order=effective_sorting.sort_order,
        )

        total = await self._count(filters=effective_filters)
        statement = self._filtered_select(effective_filters)
        statement = apply_sorting(
            statement,
            Quotation,
            resolved_sorting,
            allowed_sort_fields=QUOTATION_SORT_FIELDS,
        )
        statement = apply_pagination(statement, effective_pagination)
        result = await self._session.execute(statement)
        return list(result.scalars().all()), total

    async def list_by_customer(
        self,
        customer_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Quotation], int]:
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=QuotationFilters(customer_id=customer_id),
        )

    async def list_by_status(
        self,
        status: QuotationStatus,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Quotation], int]:
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=QuotationFilters(status=status),
        )

    async def _count(self, *, filters: QuotationFilters) -> int:
        statement = select(func.count()).select_from(Quotation)
        statement = self._apply_filters(statement, filters)
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    def _filtered_select(self, filters: QuotationFilters) -> Select:
        return self._apply_filters(self.base_select(), filters)

    def _apply_filters(
        self,
        statement: Select,
        filters: QuotationFilters,
    ) -> Select:
        # quotation_number → ILIKE via FilterParams.name remapped
        statement = apply_filters(
            statement,
            Quotation,
            FilterParams(name=filters.quotation_number),
            field_map={"name": "quotation_number"},
        )
        if filters.status is not None:
            statement = statement.where(Quotation.status == filters.status)
        if filters.customer_id is not None:
            statement = statement.where(Quotation.customer_id == filters.customer_id)
        if filters.date_from is not None:
            statement = statement.where(Quotation.quotation_date >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(Quotation.quotation_date <= filters.date_to)
        return statement
