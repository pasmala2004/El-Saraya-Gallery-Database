"""
Job application service — production workflow after quotation approval.

Status lifecycle (``JobStatus``)
---------------------------------
``pending`` → ``measuring`` → ``in_production`` → ``ready_for_installation`` →
``installed`` → ``completed``

Can be ``cancelled`` from any non-terminal state.
Terminal: ``completed``, ``cancelled``
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolation,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.core.query import Pagination, Sorting
from app.enums.job import JobStatus
from app.enums.quotation import QuotationStatus
from app.models.activity_log import ActivityLog
from app.models.job import Job
from app.repositories.job import JobFilters, JobRepository
from app.repositories.quotation import QuotationRepository
from app.services.base import BaseService

# Terminal outcomes — no further status changes.
_TERMINAL_STATUSES: frozenset[JobStatus] = frozenset(
    {
        JobStatus.COMPLETED,
        JobStatus.CANCELLED,
    }
)

# Allowed status transitions for job lifecycle.
_ALLOWED_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.PENDING: frozenset({JobStatus.MEASURING, JobStatus.CANCELLED}),
    JobStatus.MEASURING: frozenset({JobStatus.IN_PRODUCTION, JobStatus.CANCELLED}),
    JobStatus.IN_PRODUCTION: frozenset({JobStatus.READY_FOR_INSTALLATION, JobStatus.CANCELLED}),
    JobStatus.READY_FOR_INSTALLATION: frozenset({JobStatus.INSTALLED, JobStatus.CANCELLED}),
    JobStatus.INSTALLED: frozenset({JobStatus.COMPLETED, JobStatus.CANCELLED}),
    JobStatus.COMPLETED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


class JobService(BaseService[Job]):
    """Job workflow and lifecycle management."""

    def __init__(
        self,
        session: AsyncSession,
        repository: JobRepository,
        quotation_repository: QuotationRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Job")
        self._jobs = repository
        self._quotations = quotation_repository or QuotationRepository(session)

    # ------------------------------------------------------------------
    # Reads

    async def get_job(self, job_id: uuid.UUID) -> Job:
        """Get a single job by ID."""
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise EntityNotFoundError("Job", job_id)
        return job

    async def get_job_by_quotation(self, quotation_id: uuid.UUID) -> Job | None:
        """Get job associated with a quotation."""
        return await self._jobs.get_by_quotation(quotation_id)

    async def list_jobs(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: JobFilters | None = None,
    ) -> tuple[list[Job], int]:
        """List jobs with optional filtering, sorting, and pagination."""
        return await self._jobs.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def list_customer_jobs(
        self,
        customer_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Job], int]:
        """List all jobs for a customer."""
        # Verify customer exists
        from app.repositories.customer import CustomerRepository
        customer_repo = CustomerRepository(self._session)
        customer = await customer_repo.get_by_id(customer_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)
        
        return await self._jobs.list_by_customer(
            customer_id,
            pagination=pagination,
            sorting=sorting,
        )

    # ------------------------------------------------------------------
    # Writes

    async def create_job(self, data: dict[str, Any]) -> Job:
        """
        Create a new job from an approved quotation.

        Business rules:
        - Quotation must exist
        - Quotation must be APPROVED
        - Only one job per quotation (duplicate check)
        """
        quotation_id = data.get("quotation_id")
        if not quotation_id:
            raise ValidationError("quotation_id is required")

        # Validate quotation exists
        quotation = await self._quotations.get_by_id(quotation_id)
        if quotation is None:
            raise EntityNotFoundError("Quotation", quotation_id)

        # Validate quotation is approved
        if quotation.status != QuotationStatus.APPROVED:
            raise BusinessRuleViolation(
                "Only approved quotations can have jobs created"
            )

        # Check for duplicate job for this quotation
        existing_job = await self._jobs.get_by_quotation(quotation_id)
        if existing_job is not None:
            raise DuplicateEntityError(
                "Job",
                "quotation_id",
                str(quotation_id),
                "Job already exists for this quotation"
            )

        # Create job with pending status
        job_data = {
            "quotation_id": quotation_id,
            "status": JobStatus.PENDING,
            "notes": data.get("notes"),
        }

        job = Job(**job_data)
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)

        # Log activity
        await self._log_activity(
            job_id=job.id,
            action="job_created",
            description=f"Job created for quotation {quotation.quotation_number}",
        )

        return job

    async def update_job(
        self,
        job_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Job:
        """
        Update job details (dates, notes).

        Cannot update quotation_id or status (use update_status).
        Terminal jobs cannot be edited.
        """
        job = await self.get_job(job_id)

        # Prevent editing terminal jobs
        if job.status in _TERMINAL_STATUSES:
            raise BusinessRuleViolation(
                f"Cannot edit job in terminal status: {job.status.value}"
            )

        # Update allowed fields
        allowed_fields = {
            "measurement_date",
            "production_start",
            "production_end",
            "installation_date",
            "delivery_date",
            "notes",
        }

        for field, value in data.items():
            if field in allowed_fields:
                setattr(job, field, value)

        await self._session.flush()
        await self._session.refresh(job)

        # Log activity for significant date changes
        if "production_start" in data and data["production_start"]:
            await self._log_activity(
                job_id=job.id,
                action="production_started",
                description=f"Production started on {data['production_start']}",
            )
        if "installation_date" in data and data["installation_date"]:
            await self._log_activity(
                job_id=job.id,
                action="installation_scheduled",
                description=f"Installation scheduled for {data['installation_date']}",
            )

        return job

    async def update_status(
        self,
        job_id: uuid.UUID,
        new_status: JobStatus,
    ) -> Job:
        """
        Update job status following business rules.

        Validates:
        - Job exists
        - Transition is allowed
        - Terminal states cannot be changed
        """
        job = await self.get_job(job_id)

        # Terminal states cannot be changed
        if job.status in _TERMINAL_STATUSES:
            raise BusinessRuleViolation(
                f"Cannot change status from terminal state: {job.status.value}"
            )

        # Validate transition
        allowed = _ALLOWED_TRANSITIONS.get(job.status, frozenset())
        if new_status not in allowed:
            raise BusinessRuleViolation(
                f"Invalid status transition from {job.status.value} to {new_status.value}"
            )

        old_status = job.status
        job.status = new_status

        # Auto-set dates based on status
        if new_status == JobStatus.IN_PRODUCTION and not job.production_start:
            job.production_start = date.today()
        elif new_status == JobStatus.COMPLETED and not job.completion_date:
            job.completion_date = date.today()

        await self._session.flush()
        await self._session.refresh(job)

        # Log status change
        await self._log_activity(
            job_id=job.id,
            action="status_changed",
            description=f"Status changed from {old_status.value} to {new_status.value}",
        )

        # Log specific milestone activities
        if new_status == JobStatus.COMPLETED:
            await self._log_activity(
                job_id=job.id,
                action="job_completed",
                description="Job marked as completed",
            )

        return job

    # ------------------------------------------------------------------
    # Activity Logging

    async def _log_activity(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        description: str,
    ) -> None:
        """Create an activity log entry for the job."""
        activity = ActivityLog(
            job_id=job_id,
            action=action,
            description=description,
        )
        self._session.add(activity)
        await self._session.flush()
