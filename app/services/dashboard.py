"""Dashboard service."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.job import JobStatus
from app.enums.payment import PaymentStatus, PaymentType
from app.enums.quotation import QuotationStatus
from app.models.activity_log import ActivityLog
from app.models.job import Job
from app.models.payment import Payment
from app.models.quotation import Quotation
from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    ActivityDTO,
    AlertDTO,
    DashboardResponse,
    JobPipelineCardDTO,
    KPIsDTO,
    MetadataDTO,
    PaymentProgressDTO,
    PipelineDTO,
)


# Expected duration per stage (in days)
EXPECTED_DURATION: dict[JobStatus, int] = {
    JobStatus.PENDING: 7,
    JobStatus.MEASURING: 3,
    JobStatus.IN_PRODUCTION: 14,
    JobStatus.READY_FOR_INSTALLATION: 7,
    JobStatus.INSTALLED: 3,
}


class DashboardService:
    """
    Dashboard business logic.
    
    Responsibilities:
    - Orchestrate data retrieval from repository
    - Calculate derived metrics (priority, payment progress, etc.)
    - Map pipeline stages to job status
    - Generate alerts based on business rules
    - Format activity with relative time
    - Assemble DashboardResponse DTO
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = DashboardRepository(session)

    async def get_dashboard_data(self) -> DashboardResponse:
        """
        Main entry point - orchestrates all data retrieval.
        
        Returns complete dashboard data in <500ms target.
        """
        start_time = datetime.now()
        
        # Fetch all data (3-4 queries total)
        kpi_counts = await self._repository.get_kpi_counts()
        quotations_waiting = await self._repository.get_quotations_waiting_count()
        active_jobs = await self._repository.get_active_jobs_with_relations()
        recent_activities = await self._repository.get_recent_activity_logs(limit=10)
        
        # Calculate KPIs
        kpis = await self._calculate_kpis(kpi_counts, quotations_waiting, active_jobs)
        
        # Build pipeline
        pipeline = self._build_pipeline(active_jobs)
        
        # Generate alerts
        alerts = await self._generate_alerts(active_jobs)
        
        # Format activities
        formatted_activities = self._format_activities(recent_activities)
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        metadata = MetadataDTO(
            generated_at=datetime.now(),
            execution_time_ms=execution_time,
        )
        
        return DashboardResponse(
            kpis=kpis,
            pipeline=pipeline,
            alerts=alerts,
            recent_activity=formatted_activities,
            metadata=metadata,
        )


    async def _calculate_kpis(
        self,
        kpi_counts: dict[str, int],
        quotations_waiting: int,
        active_jobs: list[Job],
    ) -> KPIsDTO:
        """Calculate operational KPIs from raw data."""
        # Count jobs delayed (exceeding expected duration)
        jobs_delayed = sum(
            1 for job in active_jobs
            if self._is_job_overdue(job) and job.status != JobStatus.COMPLETED
        )
        
        return KPIsDTO(
            total_active_jobs=kpi_counts["total_active_jobs"],
            quotations_waiting_response=quotations_waiting,
            measurements_scheduled_today=kpi_counts["measurements_scheduled_today"],
            installations_scheduled_today=kpi_counts["installations_scheduled_today"],
            overdue_payments=kpi_counts["overdue_payments"],
            jobs_delayed=jobs_delayed,
        )

    def _build_pipeline(self, jobs: list[Job]) -> PipelineDTO:
        """Map jobs to pipeline stages."""
        pipeline: dict[str, list[JobPipelineCardDTO]] = {
            "quotation": [],
            "measurement": [],
            "deposit_received": [],
            "manufacturing": [],
            "installation": [],
            "completed": [],
            "rejected": [],
        }
        
        for job in jobs:
            stage = self._map_job_to_pipeline_stage(job)
            if stage is None:
                continue  # Skip jobs that shouldn't appear
            
            card = self._build_job_card(job)
            pipeline[stage].append(card)
        
        return PipelineDTO(**pipeline)

    def _map_job_to_pipeline_stage(self, job: Job) -> str | None:
        """
        Map job status + payment condition to pipeline stage.
        
        Returns None if job should be hidden.
        """
        # Rejected quotations go to rejected column
        if job.quotation.status == QuotationStatus.REJECTED:
            return "rejected"
        
        # Cancelled jobs with rejected quotations
        if job.status == JobStatus.CANCELLED:
            if job.quotation.status == QuotationStatus.REJECTED:
                return "rejected"
            return None  # Hide other cancelled jobs
        
        # Completed jobs: only show if completed within last 7 days
        if job.status == JobStatus.COMPLETED:
            if job.completion_date:
                days_since_completion = (datetime.now().date() - job.completion_date).days
                if days_since_completion <= 7:
                    return "completed"
            return None  # Hide old completed jobs
        
        # Map active job statuses
        if job.status == JobStatus.PENDING:
            return "quotation"
        
        elif job.status == JobStatus.MEASURING:
            return "measurement"
        
        elif job.status == JobStatus.IN_PRODUCTION:
            # Check if deposit is paid
            deposit_payment = next(
                (p for p in job.payments if p.payment_type == PaymentType.DEPOSIT),
                None
            )
            if deposit_payment and deposit_payment.status == PaymentStatus.PAID:
                return "deposit_received"
            return "measurement"  # Still waiting for deposit
        
        elif job.status == JobStatus.READY_FOR_INSTALLATION:
            return "manufacturing"
        
        elif job.status == JobStatus.INSTALLED:
            return "installation"
        
        return None


    def _build_job_card(self, job: Job) -> JobPipelineCardDTO:
        """Build job card DTO with all required information."""
        payment_progress = self._calculate_payment_progress(job)
        priority = self._calculate_job_priority(job)
        days_in_stage = self._calculate_days_in_stage(job)
        last_activity = self._get_last_activity_time(job)
        is_overdue = self._is_job_overdue(job)
        
        return JobPipelineCardDTO(
            job_id=str(job.id),
            job_number=f"J-{job.id.hex[:8].upper()}",  # Generate job number from ID
            quotation_number=job.quotation.quotation_number,
            customer_name=job.quotation.customer.full_name,
            current_status=job.status.value,
            assigned_engineer=None,  # Future: add engineer field to Job model
            last_activity=last_activity,
            days_in_stage=days_in_stage,
            payment_progress=payment_progress,
            priority=priority,
            measurement_date=job.measurement_date.isoformat() if job.measurement_date else None,
            installation_date=job.installation_date.isoformat() if job.installation_date else None,
            is_overdue=is_overdue,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    def _calculate_payment_progress(self, job: Job) -> PaymentProgressDTO:
        """Calculate payment progress for a job."""
        if not job.payments:
            return PaymentProgressDTO(
                paid=Decimal("0.00"),
                total=Decimal("0.00"),
                percentage=Decimal("0.00"),
            )
        
        total_amount = sum(p.amount for p in job.payments)
        paid_amount = sum(
            p.amount for p in job.payments
            if p.status == PaymentStatus.PAID
        )
        
        percentage = Decimal("0.00")
        if total_amount > 0:
            percentage = (paid_amount / total_amount * 100).quantize(Decimal("0.01"))
        
        return PaymentProgressDTO(
            paid=paid_amount,
            total=total_amount,
            percentage=percentage,
        )

    def _calculate_job_priority(self, job: Job) -> str:
        """
        Calculate job priority based on business rules.
        
        Returns: 'high' | 'medium' | 'low'
        """
        # High priority: Overdue or has overdue payments
        if self._is_job_overdue(job):
            return "high"
        
        overdue_payments = [
            p for p in job.payments
            if p.status == PaymentStatus.OVERDUE
        ]
        if overdue_payments:
            return "high"
        
        # Medium priority: Approaching deadline (≥80% of expected duration)
        days_in_stage = self._calculate_days_in_stage(job)
        expected_duration = EXPECTED_DURATION.get(job.status, 14)
        
        if days_in_stage >= (expected_duration * 0.8):
            return "medium"
        
        return "low"

    def _calculate_days_in_stage(self, job: Job) -> int:
        """Calculate days job has been in current stage."""
        # Use updated_at as proxy for stage change time
        return (datetime.now() - job.updated_at).days

    def _is_job_overdue(self, job: Job) -> bool:
        """Check if job exceeds expected duration for current stage."""
        expected_duration = EXPECTED_DURATION.get(job.status)
        if expected_duration is None:
            return False
        
        days_in_stage = self._calculate_days_in_stage(job)
        return days_in_stage > expected_duration

    def _get_last_activity_time(self, job: Job) -> str:
        """Get relative time of last activity."""
        if not job.activity_logs:
            return self._format_relative_time(job.updated_at)
        
        latest_activity = max(job.activity_logs, key=lambda a: a.created_at)
        return self._format_relative_time(latest_activity.created_at)


    async def _generate_alerts(self, active_jobs: list[Job]) -> list[AlertDTO]:
        """Generate alerts for items requiring attention."""
        alerts: list[AlertDTO] = []
        
        # Get additional alert sources
        overdue_payments = await self._repository.get_overdue_payments_with_job()
        stale_quotations = await self._repository.get_stale_quotations(days_threshold=14)
        
        # Alert: Overdue payments
        for payment in overdue_payments:
            days_overdue = 0
            if payment.due_date:
                days_overdue = (datetime.now().date() - payment.due_date).days
            
            severity = "critical" if days_overdue > 7 else "warning"
            
            alert = AlertDTO(
                id=str(uuid.uuid4()),
                type="payment_overdue",
                severity=severity,
                title="Payment Overdue",
                description=f"Payment for {payment.job.quotation.customer.full_name} is {days_overdue} days overdue",
                entity_id=str(payment.id),
                entity_type="payment",
                days_overdue=days_overdue,
            )
            alerts.append(alert)
        
        # Alert: Stale quotations
        for quotation in stale_quotations:
            days_waiting = (datetime.now() - quotation.updated_at).days
            severity = "critical" if days_waiting > 21 else "warning"
            
            alert = AlertDTO(
                id=str(uuid.uuid4()),
                type="quotation_waiting",
                severity=severity,
                title="Quotation Waiting for Response",
                description=f"Quotation {quotation.quotation_number} for {quotation.customer.full_name} waiting {days_waiting} days",
                entity_id=str(quotation.id),
                entity_type="quotation",
                days_overdue=days_waiting,
            )
            alerts.append(alert)
        
        # Alert: Jobs overdue for measurement
        for job in active_jobs:
            if job.status == JobStatus.MEASURING:
                days_in_stage = self._calculate_days_in_stage(job)
                if days_in_stage > 7:
                    alert = AlertDTO(
                        id=str(uuid.uuid4()),
                        type="measurement_overdue",
                        severity="critical",
                        title="Measurement Overdue",
                        description=f"Job for {job.quotation.customer.full_name} in measurement for {days_in_stage} days",
                        entity_id=str(job.id),
                        entity_type="job",
                        days_overdue=days_in_stage - 7,
                    )
                    alerts.append(alert)
        
        # Alert: Manufacturing delayed
        for job in active_jobs:
            if job.status == JobStatus.IN_PRODUCTION:
                days_in_stage = self._calculate_days_in_stage(job)
                if days_in_stage > 21:
                    severity = "critical" if days_in_stage > 30 else "warning"
                    alert = AlertDTO(
                        id=str(uuid.uuid4()),
                        type="manufacturing_delayed",
                        severity=severity,
                        title="Manufacturing Delayed",
                        description=f"Job for {job.quotation.customer.full_name} in production for {days_in_stage} days",
                        entity_id=str(job.id),
                        entity_type="job",
                        days_overdue=days_in_stage - 14,
                    )
                    alerts.append(alert)
        
        # Alert: Installation overdue
        for job in active_jobs:
            if job.status == JobStatus.READY_FOR_INSTALLATION:
                days_in_stage = self._calculate_days_in_stage(job)
                if days_in_stage > 10:
                    alert = AlertDTO(
                        id=str(uuid.uuid4()),
                        type="installation_overdue",
                        severity="critical",
                        title="Installation Overdue",
                        description=f"Job for {job.quotation.customer.full_name} ready for installation for {days_in_stage} days",
                        entity_id=str(job.id),
                        entity_type="job",
                        days_overdue=days_in_stage - 7,
                    )
                    alerts.append(alert)
        
        # Sort alerts: critical first, then by days overdue
        alerts.sort(
            key=lambda a: (
                0 if a.severity == "critical" else 1 if a.severity == "warning" else 2,
                -a.days_overdue,
            )
        )
        
        # Limit to top 100 alerts
        return alerts[:100]


    def _format_activities(self, activity_logs: list[ActivityLog]) -> list[ActivityDTO]:
        """Format activity logs with relative time."""
        activities: list[ActivityDTO] = []
        
        for log in activity_logs:
            try:
                customer_name = log.job.quotation.customer.full_name
            except AttributeError:
                customer_name = "Unknown Customer"
            
            activity = ActivityDTO(
                id=str(log.id),
                type=log.action,
                description=log.description or log.action,
                timestamp=log.created_at,
                relative_time=self._format_relative_time(log.created_at),
                entity_id=str(log.job_id),
                entity_type="job",
                customer_name=customer_name,
            )
            activities.append(activity)
        
        return activities

    def _format_relative_time(self, timestamp: datetime) -> str:
        """
        Format timestamp as relative time.
        
        Examples: "just now", "5 minutes ago", "2 hours ago", "3 days ago"
        """
        now = datetime.now()
        diff = now - timestamp
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        
        minutes = int(seconds / 60)
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        
        hours = int(minutes / 60)
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        days = diff.days
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''} ago"
        
        # For older items, show date
        return timestamp.strftime("%b %d, %Y")
