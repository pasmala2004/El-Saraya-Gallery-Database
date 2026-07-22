"""Dashboard API routes."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.schemas.errors import ErrorResponse
from app.services.dashboard import DashboardService

router = APIRouter(tags=["dashboard"])


def get_dashboard_service(
    session: AsyncSession = Depends(get_db),
) -> DashboardService:
    """Dependency injection for dashboard service."""
    return DashboardService(session)


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description=(
        "Retrieve aggregated operational dashboard data including:\n\n"
        "- **KPIs**: Operational metrics for daily tasks\n"
        "- **Pipeline**: Visual job board with 7 columns\n"
        "- **Alerts**: Critical items requiring attention\n"
        "- **Recent Activity**: Latest 10 system operations\n\n"
        "**Performance**: Single aggregated endpoint, target <500ms response time.\n\n"
        "**Pipeline Columns**:\n"
        "- Quotation\n"
        "- Measurement\n"
        "- Deposit Received\n"
        "- Manufacturing\n"
        "- Installation\n"
        "- Completed (auto-hide after 7 days)\n"
        "- Rejected\n\n"
        "**Job Cards** include: customer, quotation #, status, payment progress, "
        "priority, dates, days in stage, last activity."
    ),
    responses={
        200: {
            "description": "Dashboard data retrieved successfully.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Server error during dashboard data aggregation.",
        },
    },
)
async def get_dashboard(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    """
    Retrieve complete dashboard data.
    
    This endpoint aggregates data from all ERP modules:
    - Customers
    - Quotations
    - Jobs
    - Measurements
    - Payments
    
    The dashboard does not own business state - it only presents
    aggregated views of existing data.
    """
    return await service.get_dashboard_data()
