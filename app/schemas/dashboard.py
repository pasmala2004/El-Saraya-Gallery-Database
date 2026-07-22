"""Dashboard schemas."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentProgressDTO(BaseModel):
    """Payment progress information for a job."""

    paid: Decimal = Field(..., description="Total amount paid")
    total: Decimal = Field(..., description="Total amount expected")
    percentage: Decimal = Field(..., description="Percentage paid (0-100)")


class JobPipelineCardDTO(BaseModel):
    """Job card data for pipeline board."""

    job_id: str = Field(..., description="Job UUID")
    job_number: str = Field(..., description="Job reference number")
    quotation_number: str = Field(..., description="Quotation number")
    customer_name: str = Field(..., description="Customer full name")
    current_status: str = Field(..., description="Current job status")
    assigned_engineer: str | None = Field(None, description="Assigned engineer name")
    last_activity: str = Field(..., description="Last activity relative time")
    days_in_stage: int = Field(..., description="Days in current stage")
    payment_progress: PaymentProgressDTO
    priority: str = Field(..., description="Priority: high | medium | low")
    measurement_date: str | None = Field(None, description="Measurement date ISO format")
    installation_date: str | None = Field(None, description="Installation date ISO format")
    is_overdue: bool = Field(..., description="Whether job is overdue")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PipelineDTO(BaseModel):
    """Pipeline columns with job cards."""

    quotation: list[JobPipelineCardDTO] = Field(default_factory=list)
    measurement: list[JobPipelineCardDTO] = Field(default_factory=list)
    deposit_received: list[JobPipelineCardDTO] = Field(default_factory=list, alias="depositReceived")
    manufacturing: list[JobPipelineCardDTO] = Field(default_factory=list)
    installation: list[JobPipelineCardDTO] = Field(default_factory=list)
    completed: list[JobPipelineCardDTO] = Field(default_factory=list)
    rejected: list[JobPipelineCardDTO] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class KPIsDTO(BaseModel):
    """Operational KPIs for dashboard."""

    total_active_jobs: int = Field(..., description="Count of active jobs")
    quotations_waiting_response: int = Field(..., description="Quotations awaiting customer response")
    measurements_scheduled_today: int = Field(..., description="Measurements scheduled for today")
    installations_scheduled_today: int = Field(..., description="Installations scheduled for today")
    overdue_payments: int = Field(..., description="Count of overdue payments")
    jobs_delayed: int = Field(..., description="Count of delayed jobs")



class AlertDTO(BaseModel):
    """Alert for items requiring attention."""

    id: str = Field(..., description="Alert unique identifier")
    type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Severity: critical | warning | info")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    entity_id: str = Field(..., description="Related entity UUID")
    entity_type: str = Field(..., description="Entity type: job | quotation | payment")
    days_overdue: int = Field(..., description="Days overdue/delayed")


class ActivityDTO(BaseModel):
    """Recent activity entry."""

    id: str = Field(..., description="Activity log UUID")
    type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(..., description="Activity timestamp")
    relative_time: str = Field(..., description="Relative time (e.g., '2 hours ago')")
    entity_id: str = Field(..., description="Related entity UUID")
    entity_type: str = Field(..., description="Entity type")
    customer_name: str = Field(..., description="Associated customer name")


class MetadataDTO(BaseModel):
    """Response metadata."""

    generated_at: datetime = Field(..., description="Response generation timestamp")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")


class DashboardResponse(BaseModel):
    """Complete dashboard data response."""

    kpis: KPIsDTO
    pipeline: PipelineDTO
    alerts: list[AlertDTO] = Field(default_factory=list)
    recent_activity: list[ActivityDTO] = Field(default_factory=list, alias="recentActivity")
    metadata: MetadataDTO

    class Config:
        populate_by_name = True
