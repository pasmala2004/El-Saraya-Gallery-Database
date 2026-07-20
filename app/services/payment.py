"""
Payment application service — payment management for jobs.

Status lifecycle (``PaymentStatus``)
------------------------------------
``pending`` → ``paid``
Can be ``cancelled`` or ``overdue`` from pending.
Terminal: ``paid``, ``cancelled``
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolation,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.core.query import Pagination, Sorting
from app.enums.payment import PaymentStatus
from app.models.activity_log import ActivityLog
from app.models.payment import Payment
from app.repositories.job import JobRepository
from app.repositories.payment import PaymentFilters, PaymentRepository
from app.services.base import BaseService

# Terminal outcomes — no further status changes.
_TERMINAL_STATUSES: frozenset[PaymentStatus] = frozenset(
    {
        PaymentStatus.PAID,
        PaymentStatus.CANCELLED,
    }
)


class PaymentService(BaseService[Payment]):
    """Payment management and calculations."""

    def __init__(
        self,
        session: AsyncSession,
        repository: PaymentRepository,
        job_repository: JobRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Payment")
        self._payments = repository
        self._jobs = job_repository or JobRepository(session)

    # ------------------------------------------------------------------
    # Reads

    async def get_payment(self, payment_id: uuid.UUID) -> Payment:
        """Get a single payment by ID."""
        payment = await self._payments.get_by_id(payment_id)
        if payment is None:
            raise EntityNotFoundError("Payment", payment_id)
        return payment

    async def list_payments(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: PaymentFilters | None = None,
    ) -> tuple[list[Payment], int]:
        """List payments with optional filtering, sorting, and pagination."""
        return await self._payments.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def list_job_payments(
        self,
        job_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Payment], int]:
        """List all payments for a job."""
        # Verify job exists
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise EntityNotFoundError("Job", job_id)

        return await self._payments.list_by_job(
            job_id,
            pagination=pagination,
            sorting=sorting,
        )

    # ------------------------------------------------------------------
    # Writes

    async def create_payment(self, data: dict[str, Any]) -> Payment:
        """
        Create a new payment for a job.

        Business rules:
        - Job must exist
        - payment_order auto-increments per job
        - 0 < percentage <= 100
        - amount >= 0
        - paid_date cannot be before due_date
        - payment_method required
        - payment_type required
        """
        job_id = data.get("job_id")
        if not job_id:
            raise ValidationError("job_id is required")

        # Validate job exists
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise EntityNotFoundError("Job", job_id)

        # Auto-assign payment_order
        payment_order = await self._payments.get_next_payment_order(job_id)

        # Validate payment_type and payment_method
        payment_type = data.get("payment_type")
        if not payment_type:
            raise ValidationError("payment_type is required")

        payment_method = data.get("payment_method")
        if not payment_method:
            raise ValidationError("payment_method is required")

        # Validate percentage
        percentage = self._as_decimal(data.get("percentage", Decimal("0.00")), field="percentage")
        if percentage <= 0 or percentage > 100:
            raise ValidationError(
                "percentage must be greater than 0 and less than or equal to 100",
                field="percentage"
            )

        # Validate amount
        amount = self._as_decimal(data.get("amount", Decimal("0.00")), field="amount")
        if amount < 0:
            raise ValidationError("amount cannot be negative", field="amount")

        # Validate dates
        due_date = data.get("due_date")
        paid_date = data.get("paid_date")
        if due_date and isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        if paid_date and isinstance(paid_date, str):
            paid_date = date.fromisoformat(paid_date)

        if paid_date and due_date and paid_date < due_date:
            raise ValidationError(
                "paid_date cannot be before due_date",
                field="paid_date"
            )

        # Determine status
        status = PaymentStatus.PENDING
        if paid_date:
            status = PaymentStatus.PAID

        # Create payment
        payment_data = {
            "job_id": job_id,
            "payment_order": payment_order,
            "payment_type": payment_type,
            "payment_method": payment_method,
            "percentage": percentage,
            "amount": amount,
            "due_date": due_date,
            "paid_date": paid_date,
            "status": status,
            "notes": data.get("notes"),
        }

        payment = Payment(**payment_data)
        self._session.add(payment)
        await self._session.flush()
        await self._session.refresh(payment)

        # Log activity
        await self._log_activity(
            job_id=job.id,
            action="payment_created",
            description=f"Payment #{payment_order} created: {payment_type.value} - {amount}",
        )

        return payment

    async def update_payment(
        self,
        payment_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Payment:
        """
        Update payment details.

        Cannot update job_id or payment_order.
        Terminal payments (paid, cancelled) have limited editability.
        """
        payment = await self.get_payment(payment_id)

        # Update allowed fields
        if "payment_type" in data and data["payment_type"] is not None:
            payment.payment_type = data["payment_type"]

        if "payment_method" in data and data["payment_method"] is not None:
            payment.payment_method = data["payment_method"]

        if "percentage" in data and data["percentage"] is not None:
            percentage = self._as_decimal(data["percentage"], field="percentage")
            if percentage <= 0 or percentage > 100:
                raise ValidationError(
                    "percentage must be greater than 0 and less than or equal to 100",
                    field="percentage"
                )
            payment.percentage = percentage

        if "amount" in data and data["amount"] is not None:
            amount = self._as_decimal(data["amount"], field="amount")
            if amount < 0:
                raise ValidationError("amount cannot be negative", field="amount")
            payment.amount = amount

        if "due_date" in data:
            due_date = data["due_date"]
            if due_date and isinstance(due_date, str):
                due_date = date.fromisoformat(due_date)
            payment.due_date = due_date

        if "paid_date" in data:
            paid_date = data["paid_date"]
            if paid_date and isinstance(paid_date, str):
                paid_date = date.fromisoformat(paid_date)
            payment.paid_date = paid_date

        if "notes" in data:
            payment.notes = data.get("notes")

        # Re-validate dates after update
        if payment.paid_date and payment.due_date and payment.paid_date < payment.due_date:
            raise ValidationError(
                "paid_date cannot be before due_date",
                field="paid_date"
            )

        await self._session.flush()
        await self._session.refresh(payment)

        # Log activity
        await self._log_activity(
            job_id=payment.job_id,
            action="payment_updated",
            description=f"Payment #{payment.payment_order} updated",
        )

        return payment

    async def update_status(
        self,
        payment_id: uuid.UUID,
        new_status: PaymentStatus,
    ) -> Payment:
        """
        Update payment status.

        Validates:
        - Payment exists
        - Terminal states cannot be changed
        """
        payment = await self.get_payment(payment_id)

        # Terminal states cannot be changed
        if payment.status in _TERMINAL_STATUSES:
            raise BusinessRuleViolation(
                f"Cannot change status from terminal state: {payment.status.value}"
            )

        old_status = payment.status
        payment.status = new_status

        # Auto-set paid_date when marking as paid
        if new_status == PaymentStatus.PAID and not payment.paid_date:
            payment.paid_date = date.today()

        await self._session.flush()
        await self._session.refresh(payment)

        # Log status change
        action = "payment_marked_paid" if new_status == PaymentStatus.PAID else "payment_cancelled" if new_status == PaymentStatus.CANCELLED else "payment_status_changed"
        await self._log_activity(
            job_id=payment.job_id,
            action=action,
            description=f"Payment #{payment.payment_order} status changed from {old_status.value} to {new_status.value}",
        )

        return payment

    # ------------------------------------------------------------------
    # Helper Calculations

    async def get_total_paid(self, job_id: uuid.UUID) -> Decimal:
        """Calculate total paid amount for a job."""
        stmt = (
            select(func.sum(Payment.amount))
            .where(Payment.job_id == job_id)
            .where(Payment.status == PaymentStatus.PAID)
        )
        result = await self._session.execute(stmt)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_total_scheduled(self, job_id: uuid.UUID) -> Decimal:
        """Calculate total scheduled amount (all payments) for a job."""
        stmt = (
            select(func.sum(Payment.amount))
            .where(Payment.job_id == job_id)
        )
        result = await self._session.execute(stmt)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_outstanding_balance(self, job_id: uuid.UUID) -> Decimal:
        """Calculate outstanding balance (scheduled - paid) for a job."""
        total_scheduled = await self.get_total_scheduled(job_id)
        total_paid = await self.get_total_paid(job_id)
        return total_scheduled - total_paid

    async def get_paid_percentage(self, job_id: uuid.UUID) -> Decimal:
        """Calculate paid percentage for a job."""
        total_scheduled = await self.get_total_scheduled(job_id)
        if total_scheduled == 0:
            return Decimal("0.00")
        total_paid = await self.get_total_paid(job_id)
        percentage = (total_paid / total_scheduled) * Decimal("100")
        return percentage.quantize(Decimal("0.01"))

    # ------------------------------------------------------------------
    # Activity Logging

    async def _log_activity(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        description: str,
    ) -> None:
        """Create an activity log entry for the payment."""
        activity = ActivityLog(
            job_id=job_id,
            action=action,
            description=description,
        )
        self._session.add(activity)
        await self._session.flush()

    # ------------------------------------------------------------------
    # Utilities

    @staticmethod
    def _as_decimal(value: Any, *, field: str) -> Decimal:
        """Convert value to Decimal with validation."""
        try:
            amount = Decimal(str(value))
        except Exception as exc:
            raise ValidationError(
                f"Invalid decimal value for {field}",
                field=field
            ) from exc
        return amount.quantize(Decimal("0.01"))
