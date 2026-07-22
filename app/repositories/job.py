"""Job repository."""
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
from app.enums.job import JobStatus
from app.models.job import Job
from app.repositories.base import GenericRepository

JOB_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "status",
        "measurement_date",
        "production_start",
        "production_end",
        "installation_date",
        "delivery_date",
        "completion_date",
        "created_at",
        "updated_at",
    }
)


@dataclass(frozen=True, slots=True)
class JobFilters:
    """
    Job list filters.

    Support filtering by status, customer (via quotation), quotation, and date ranges.
    """

    status: JobStatus | None = None
    customer_id: uuid.UUID | None = None
    quotation_id: uuid.UUID | None = None
    date_from: date | None = None
    date_to: date | None = None


class JobRepository(GenericRepository[Job]):
    """Data access for ``Job`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Job)

    async def get_by_quotation(self, quotation_id: uuid.UUID) -> Job | None:
        """Get job by quotation ID (1-to-1 relationship)."""
        result = await self._session.execute(
            select(Job).where(Job.quotation_id == quotation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_quotation_id(self, quotation_id: uuid.UUID) -> Job | None:
        """
        Check if job already exists for quotation.
        
        Alias for get_by_quotation() to match service layer naming.
        Used to prevent duplicate job creation when approving quotations.
        """
        return await self.get_by_quotation(quotation_id)

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: JobFilters | None = None,
    ) -> tuple[list[Job], int]:
        """Search jobs with status / customer / quotation / date filters."""
        effective_filters = filters or JobFilters()
        effective_pagination = pagination or Pagination()
        effective_sorting = sorting or Sorting(
            sort_by="created_at",
            sort_order="desc",
        )

        total = await self._count(filters=effective_filters)
        statement = self._filtered_select(effective_filters)
        statement = apply_sorting(
            statement,
            Job,
            effective_sorting,
            allowed_sort_fields=JOB_SORT_FIELDS,
        )
        statement = apply_pagination(statement, effective_pagination)
        result = await self._session.execute(statement)
        return list(result.scalars().all()), total

    async def list_by_status(
        self,
        status: JobStatus,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Job], int]:
        """List jobs by status."""
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=JobFilters(status=status),
        )

    async def list_by_customer(
        self,
        customer_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Job], int]:
        """List jobs for a specific customer."""
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=JobFilters(customer_id=customer_id),
        )

    async def _count(self, *, filters: JobFilters) -> int:
        """Count jobs matching filters."""
        statement = select(func.count()).select_from(Job)
        statement = self._apply_filters(statement, filters)
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    def _filtered_select(self, filters: JobFilters) -> Select:
        """Build filtered select statement."""
        return self._apply_filters(self.base_select(), filters)

    def _apply_filters(
        self,
        statement: Select,
        filters: JobFilters,
    ) -> Select:
        """Apply filters to statement."""
        # Join with quotation if we need customer filter
        needs_join = filters.customer_id is not None
        
        if needs_join:
            from app.models.quotation import Quotation
            statement = statement.join(Quotation, Job.quotation_id == Quotation.id)

        if filters.status is not None:
            statement = statement.where(Job.status == filters.status)
        if filters.quotation_id is not None:
            statement = statement.where(Job.quotation_id == filters.quotation_id)
        if filters.customer_id is not None:
            from app.models.quotation import Quotation
            statement = statement.where(Quotation.customer_id == filters.customer_id)
        if filters.date_from is not None:
            statement = statement.where(Job.created_at >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(Job.created_at <= filters.date_to)
        return statement
