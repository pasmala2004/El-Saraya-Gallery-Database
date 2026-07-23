"""
Activity Logs API endpoints.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogRead, ActivityLogListResponse

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


@router.get(
    "",
    response_model=ActivityLogListResponse,
    summary="List activity logs",
    description=(
        "Retrieve activity logs with optional filters.\n\n"
        "**Query Parameters**:\n"
        "- job_id: Filter by job\n"
        "- quotation_id: Filter by quotation\n"
        "- limit/offset: Pagination\n\n"
        "**Ordering**: Most recent first (created_at DESC)"
    ),
)
def list_activity_logs(
    db: Session = Depends(deps.get_db),
    job_id: Optional[UUID] = Query(None, description="Filter by job ID"),
    quotation_id: Optional[UUID] = Query(None, description="Filter by quotation ID"),
    limit: int = Query(100, ge=1, le=100, description="Max items"),
    offset: int = Query(0, ge=0, description="Skip items"),
):
    """List activity logs with optional filters."""
    query = db.query(ActivityLog)
    
    if job_id:
        query = query.filter(ActivityLog.job_id == job_id)
    if quotation_id:
        query = query.filter(ActivityLog.quotation_id == quotation_id)
    
    total = query.count()
    items = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return ActivityLogListResponse(
        items=[ActivityLogRead.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{activity_log_id}",
    response_model=ActivityLogRead,
    summary="Get activity log",
    description="Retrieve a single activity log entry by ID.",
)
def get_activity_log(
    activity_log_id: UUID,
    db: Session = Depends(deps.get_db),
):
    """Get activity log by ID."""
    from app.core.exceptions import NotFoundException
    
    log = db.query(ActivityLog).filter(ActivityLog.id == activity_log_id).first()
    if not log:
        raise NotFoundException(f"Activity log {activity_log_id} not found")
    
    return ActivityLogRead.model_validate(log)
