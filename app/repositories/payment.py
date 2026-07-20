"""Payment repository."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import Pagination, Sorting, apply_pagination, apply_sorting
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType
from app.models.payment import Payment
from app.repositories.base import GenericRepository

PAYMENT_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "payment_order",
        "payment_type",
        "payment_method",
        "percentage",
        "amount",
        "due_date",
        "paid_date",
        "status",
        "created_at",
        "updated_at",
    }
)


@dataclass(frozen=True, slots=True)
class PaymentFilters:
    """Filters for payment search."""

    job_id: uuid.UUID | None = None
    status: PaymentStatus | None = None
    payment_type: PaymentType | None = None
    payment_method: PaymentMethod | None = None
    due_date_from: date | None = None
    due_date_to: date | None = None
    paid_date_from: date | None = None
    paid_date_to: date | None = None
    created_after: date | None = None
    created_before: date | None = None


class PaymentRepository(GenericRepository[Payment]):
    """Repository for payment operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Payment)

    async def list_by_job(
        self,
        job_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Payment], int]:
        """List all payments for a job."""
        filters = PaymentFilters(job_id=job_id)
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def get_next_payment_order(self, job_id: uuid.UUID) -> int:
        """Get the next payment_order for a job."""
        stmt = (
            select(func.max(Payment.payment_order))
            .where(Payment.job_id == job_id)
        )
        result = await self._session.execute(stmt)
        max_order = result.scalar_one_or_none()
        return 1 if max_order is None else max_order + 1

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: PaymentFilters | None = None,
    ) -> tuple[list[Payment], int]:
        """Search payments with filters, sorting, and pagination."""
        stmt = select(Payment)
        count_stmt = select(func.count()).select_from(Payment)

        # Apply filters
        if filters:
            conditions = self._build_filter_conditions(filters)
            if conditions:
                from sqlalchemy import and_
                stmt = stmt.where(and_(*conditions))
                count_stmt = count_stmt.where(and_(*conditions))

        # Get total count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply sorting
        if sorting:
            stmt = apply_sorting(
                stmt,
                Payment,
                sorting,
                allowed_sort_fields=PAYMENT_SORT_FIELDS,
            )
        else:
            # Default sort by payment_order ascending
            stmt = stmt.order_by(Payment.payment_order.asc())

        # Apply pagination
        if pagination:
            stmt = apply_pagination(stmt, pagination)

        # Execute query
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    def _build_filter_conditions(self, filters: PaymentFilters) -> list:
        """Build SQLAlchemy filter conditions."""
        conditions = []

        if filters.job_id:
            conditions.append(Payment.job_id == filters.job_id)

        if filters.status is not None:
            conditions.append(Payment.status == filters.status)

        if filters.payment_type is not None:
            conditions.append(Payment.payment_type == filters.payment_type)

        if filters.payment_method is not None:
            conditions.append(Payment.payment_method == filters.payment_method)

        if filters.due_date_from:
            conditions.append(Payment.due_date >= filters.due_date_from)

        if filters.due_date_to:
            conditions.append(Payment.due_date <= filters.due_date_to)

        if filters.paid_date_from:
            conditions.append(Payment.paid_date >= filters.paid_date_from)

        if filters.paid_date_to:
            conditions.append(Payment.paid_date <= filters.paid_date_to)

        if filters.created_after:
            conditions.append(
                func.date(Payment.created_at) >= filters.created_after
            )

        if filters.created_before:
            conditions.append(
                func.date(Payment.created_at) <= filters.created_before
            )

        return conditions

