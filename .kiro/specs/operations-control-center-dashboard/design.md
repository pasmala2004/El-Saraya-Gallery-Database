# Design Document

## Overview

The Operations Control Center Dashboard is designed as an **operational ERP dashboard** focused on helping gallery assistants manage daily tasks, not an executive analytics dashboard. The primary goal is to surface what needs attention today and provide a visual pipeline for tracking job progress through stages.

### Design Principles

1. **Action-Oriented**: Every element should answer "what do I need to do today?"
2. **Pipeline-Centric**: The main feature is a visual board showing all active jobs in their current stage
3. **Performance-First**: Single aggregated API request, <500ms response time target
4. **Future-Proof**: Architecture supports drag & drop, calendar view, engineer workload, charts, reports, and AI recommendations
5. **Real-Time Updates**: Cards automatically update as backend status changes

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              DashboardPage Component                    │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  KPIGrid (6 operational KPI cards)               │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  PipelineBoard (7 columns, job cards)            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐ │ │
│  │  │  AlertsPanel    │  │  RecentActivity              │ │ │
│  │  └─────────────────┘  └──────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP GET /api/v1/dashboard
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  DashboardRouter  →  DashboardService                  │ │
│  │                         │                               │ │
│  │                         ▼                               │ │
│  │                  DashboardRepository                    │ │
│  │                  (SQL Aggregations)                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    └──────────────┘
```


---

## Components and Interfaces

### Frontend Architecture

### Component Hierarchy

```
DashboardPage
├── DashboardFilters (future: date range, engineer filter)
├── KPIGrid
│   ├── KPICard (Total Active Jobs)
│   ├── KPICard (Quotations Waiting for Response)
│   ├── KPICard (Measurements Scheduled Today)
│   ├── KPICard (Installations Scheduled Today)
│   ├── KPICard (Overdue Payments)
│   └── KPICard (Jobs Delayed)
├── PipelineBoard
│   ├── PipelineColumn (Quotation)
│   │   └── JobPipelineCard[]
│   ├── PipelineColumn (Measurement)
│   │   └── JobPipelineCard[]
│   ├── PipelineColumn (Deposit Received)
│   │   └── JobPipelineCard[]
│   ├── PipelineColumn (Manufacturing)
│   │   └── JobPipelineCard[]
│   ├── PipelineColumn (Installation)
│   │   └── JobPipelineCard[]
│   ├── PipelineColumn (Completed - auto-hide after 7 days)
│   │   └── JobPipelineCard[]
│   └── PipelineColumn (Rejected)
│       └── JobPipelineCard[]
├── AlertsPanel
│   └── AlertItem[]
└── RecentActivity
    └── ActivityItem[]
```

### Component Specifications

#### 1. DashboardPage

**Purpose**: Root container for the operational dashboard

**State Management**:
- `dashboardData`: Aggregated dashboard response from API
- `isLoading`: Boolean for loading state
- `error`: Error object if API request fails
- `lastRefreshed`: Timestamp of last data fetch

**API Integration**:
```typescript
GET /api/v1/dashboard
Response: DashboardResponse (see Backend Architecture)
```


**Responsibilities**:
- Fetch dashboard data on mount
- Auto-refresh every 30 seconds
- Handle loading and error states
- Pass data down to child components
- Manage future filters (not implemented yet)

**File**: `frontend/src/pages/Dashboard.tsx`

---

#### 2. KPIGrid

**Purpose**: Container for operational KPI cards displayed in a responsive grid

**Props**:
```typescript
interface KPIGridProps {
  kpis: {
    totalActiveJobs: number;
    quotationsWaitingResponse: number;
    measurementsScheduledToday: number;
    installationsScheduledToday: number;
    overduePayments: number;
    jobsDelayed: number;
  };
}
```

**Layout**:
- Desktop (≥1024px): 6 columns (all cards in one row)
- Tablet (768px-1023px): 3 columns (2 rows)
- Mobile (<768px): 2 columns (3 rows)

**File**: `frontend/src/components/dashboard/KPIGrid.tsx`

---

#### 3. KPICard

**Purpose**: Display a single operational metric with icon, label, value, and optional trend

**Props**:
```typescript
interface KPICardProps {
  label: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  color: 'blue' | 'green' | 'yellow' | 'orange' | 'red' | 'purple';
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  onClick?: () => void;
}
```

**Visual Design**:
- White background with shadow
- Icon in colored circle (top-right)
- Label (text-sm, gray-600)
- Value (text-3xl, bold, gray-900)
- Optional trend indicator (text-xs, colored)
- Hover: elevated shadow, cursor pointer if onClick provided

**File**: `frontend/src/components/dashboard/KPICard.tsx`

---

#### 4. PipelineBoard

**Purpose**: Main visual board showing all active jobs organized by stage

**Props**:
```typescript
interface PipelineBoardProps {
  pipeline: {
    quotation: JobPipelineCardData[];
    measurement: JobPipelineCardData[];
    depositReceived: JobPipelineCardData[];
    manufacturing: JobPipelineCardData[];
    installation: JobPipelineCardData[];
    completed: JobPipelineCardData[];
    rejected: JobPipelineCardData[];
  };
}
```


**Layout**:
- Horizontal scroll container
- 7 columns side-by-side
- Each column has fixed width (280px)
- Column header with stage name and count badge
- Scrollable card list within each column

**Future Extensions**:
- Drag & drop between columns (react-beautiful-dnd)
- Column collapse/expand
- Sort options (by date, priority, customer)

**File**: `frontend/src/components/dashboard/PipelineBoard.tsx`

---

#### 5. PipelineColumn

**Purpose**: Container for a single pipeline stage with header and job cards

**Props**:
```typescript
interface PipelineColumnProps {
  title: string;
  count: number;
  color: string;
  jobs: JobPipelineCardData[];
  onCardClick: (jobId: string) => void;
}
```

**Visual Design**:
- Column header: stage title + count badge
- Background color matching stage
- Scrollable card container
- Empty state: "No jobs in {stage}"

**File**: `frontend/src/components/dashboard/PipelineColumn.tsx`

---

#### 6. JobPipelineCard

**Purpose**: Display comprehensive job information in a compact card format

**Props**:
```typescript
interface JobPipelineCardData {
  jobId: string;
  quotationNumber: string;
  customerName: string;
  currentStatus: string;
  assignedEngineer: string | null;
  lastActivity: string; // relative time: "2 hours ago"
  daysInStage: number;
  paymentProgress: {
    paid: number;
    total: number;
    percentage: number;
  };
  priority: 'high' | 'medium' | 'low';
  measurementDate: string | null;
  installationDate: string | null;
  isOverdue: boolean;
}

interface JobPipelineCardProps {
  data: JobPipelineCardData;
  onClick: () => void;
}
```

**Visual Design**:
```
┌─────────────────────────────────────┐
│ [Priority Bar - colored top border] │
│                                      │
│ Customer Name          [Days Badge]  │
│ Quotation #Q-2024-001                │
│                                      │
│ 👤 Engineer Name (if assigned)       │
│ 🕐 Last activity: 2 hours ago        │
│                                      │
│ Payment Progress:                    │
│ ▓▓▓▓▓▓▓▓░░░░ 8,000 / 10,000 (80%)  │
│                                      │
│ 📅 Measurement: Jan 15               │
│ 📅 Installation: Jan 22              │
└─────────────────────────────────────┘
```


**Priority Colors**:
- High: Red (#EF4444) - overdue or critical
- Medium: Yellow (#F59E0B) - approaching deadline
- Low: Green (#10B981) - on track

**Overdue Indicator**: Red border + red badge

**File**: `frontend/src/components/dashboard/JobPipelineCard.tsx`

---

#### 7. AlertsPanel

**Purpose**: Display urgent items requiring immediate attention

**Props**:
```typescript
interface Alert {
  id: string;
  type: 'quotation_waiting' | 'measurement_overdue' | 'manufacturing_delayed' | 
        'installation_overdue' | 'payment_overdue' | 'job_inactive';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  entityId: string;
  entityType: 'job' | 'quotation' | 'payment';
  daysOverdue: number;
}

interface AlertsPanelProps {
  alerts: Alert[];
}
```

**Visual Design**:
- Sorted by severity (critical → warning → info)
- Icon based on alert type
- Severity color coding
- Click navigates to related entity
- Show top 10, "View All" link for more

**File**: `frontend/src/components/dashboard/AlertsPanel.tsx`

---

#### 8. RecentActivity

**Purpose**: Timeline of recent system operations

**Props**:
```typescript
interface Activity {
  id: string;
  type: 'customer_created' | 'quotation_created' | 'quotation_approved' | 
        'measurement_completed' | 'payment_received' | 'job_started' | 
        'installation_completed';
  description: string;
  timestamp: string; // ISO 8601
  relativeTime: string; // "2 hours ago"
  entityId: string;
  entityType: 'customer' | 'quotation' | 'job' | 'payment' | 'measurement';
  customerName: string;
}

interface RecentActivityProps {
  activities: Activity[];
}
```

**Visual Design**:
- Vertical timeline with icons
- Most recent at top
- Icon + color coding per activity type
- Relative time display
- Click navigates to entity
- Show 10 most recent

**File**: `frontend/src/components/dashboard/RecentActivity.tsx`

---

#### 9. DashboardFilters (Future)

**Purpose**: Allow filtering dashboard data by date range, engineer, status

**Props** (Future):
```typescript
interface DashboardFiltersProps {
  onFilterChange: (filters: FilterState) => void;
}
```

**Not implemented in initial version** - architecture supports adding later

**File**: `frontend/src/components/dashboard/DashboardFilters.tsx` (future)

---


## Backend Architecture

### API Endpoint Design

**Single Aggregated Endpoint**:
```
GET /api/v1/dashboard
Response: 200 OK
Content-Type: application/json
```

**Response Schema** (`DashboardResponse`):
```typescript
{
  "kpis": {
    "totalActiveJobs": number,
    "quotationsWaitingResponse": number,
    "measurementsScheduledToday": number,
    "installationsScheduledToday": number,
    "overduePayments": number,
    "jobsDelayed": number
  },
  "pipeline": {
    "quotation": JobPipelineCardData[],
    "measurement": JobPipelineCardData[],
    "depositReceived": JobPipelineCardData[],
    "manufacturing": JobPipelineCardData[],
    "installation": JobPipelineCardData[],
    "completed": JobPipelineCardData[],
    "rejected": JobPipelineCardData[]
  },
  "alerts": Alert[],
  "recentActivity": Activity[],
  "metadata": {
    "generatedAt": "2024-01-15T10:30:00Z",
    "executionTimeMs": number
  }
}
```

---

### Backend Component Architecture

#### 1. DashboardRouter

**File**: `app/api/v1/dashboard.py`

**Responsibilities**:
- Define HTTP GET route `/api/v1/dashboard`
- Dependency injection for database session
- Call DashboardService
- Return DashboardResponse DTO
- Handle exceptions and return appropriate HTTP error codes


**Implementation Sketch**:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.services.dashboard import DashboardService
from app.schemas.dashboard import DashboardResponse

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(deps.get_db)
) -> DashboardResponse:
    """
    Retrieve aggregated dashboard data for operations control center.
    
    Returns KPIs, pipeline view, alerts, and recent activity.
    Target response time: <500ms
    """
    service = DashboardService(db)
    return await service.get_dashboard_data()
```

---

#### 2. DashboardService

**File**: `app/services/dashboard.py`

**Responsibilities**:
- Orchestrate data retrieval from DashboardRepository
- Calculate derived metrics (e.g., payment progress percentages)
- Map pipeline stages to job status enums
- Determine job priority based on business rules
- Assemble DashboardResponse DTO
- Measure execution time


**Key Methods**:
```python
class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = DashboardRepository(db)
    
    async def get_dashboard_data(self) -> DashboardResponse:
        """Main entry point - orchestrates all data retrieval"""
        
    def _calculate_kpis(self, raw_data) -> KPIsDTO:
        """Calculate operational KPIs from raw data"""
        
    def _build_pipeline(self, jobs_data) -> PipelineDTO:
        """Map jobs to pipeline stages"""
        
    def _map_job_to_pipeline_stage(self, job) -> str:
        """Business logic: job status → pipeline stage"""
        
    def _calculate_job_priority(self, job) -> str:
        """Business logic: determine if job is high/medium/low priority"""
        
    def _is_job_overdue(self, job) -> bool:
        """Check if job exceeds expected duration for current stage"""
        
    def _generate_alerts(self, jobs_data, payments_data) -> list[Alert]:
        """Identify items requiring immediate attention"""
        
    def _format_recent_activity(self, activity_logs) -> list[Activity]:
        """Format activity logs with relative time"""
```

**Pipeline Stage Mapping Logic**:
```python
def _map_job_to_pipeline_stage(self, job) -> str:
    """
    Maps Job.status + payment status → pipeline stage
    """
    if job.status in [JobStatus.PENDING]:
        # Check if quotation is sent
        if job.quotation.status == QuotationStatus.SENT:
            return "quotation"
        return "quotation"
        
    elif job.status == JobStatus.MEASURING:
        return "measurement"
        
    elif job.status == JobStatus.IN_PRODUCTION:
        # Check if deposit payment is paid
        deposit = [p for p in job.payments if p.payment_type == PaymentType.DEPOSIT]
        if deposit and deposit[0].status == PaymentStatus.PAID:
            return "depositReceived"
        return "measurement"  # Still waiting for deposit
        
    elif job.status == JobStatus.READY_FOR_INSTALLATION:
        return "manufacturing"
        
    elif job.status == JobStatus.INSTALLED:
        return "installation"
        
    elif job.status == JobStatus.COMPLETED:
        # Auto-hide after 7 days
        if (datetime.now() - job.completion_date).days <= 7:
            return "completed"
        return None  # Don't show on board
        
    elif job.status == JobStatus.CANCELLED:
        # Check if quotation was rejected
        if job.quotation.status == QuotationStatus.REJECTED:
            return "rejected"
        return None  # Don't show cancelled jobs
```

**Priority Calculation Logic**:
```python
def _calculate_job_priority(self, job) -> str:
    """
    High: Overdue or payment issues
    Medium: Approaching deadline
    Low: On track
    """
    if self._is_job_overdue(job):
        return "high"
        
    # Check payment issues
    overdue_payments = [p for p in job.payments 
                       if p.status == PaymentStatus.OVERDUE]
    if overdue_payments:
        return "high"
        
    # Check if approaching deadline (within 3 days)
    days_in_stage = self._calculate_days_in_stage(job)
    expected_duration = self._get_expected_duration_for_stage(job.status)
    
    if days_in_stage >= (expected_duration * 0.8):  # 80% of expected time
        return "medium"
        
    return "low"
```

---

#### 3. DashboardRepository

**File**: `app/repositories/dashboard.py`

**Responsibilities**:
- Execute optimized SQL queries with JOINs and aggregations
- Avoid N+1 query problems
- Use eager loading for relationships (selectinload, joinedload)
- Return raw data structures for service layer processing

**Key Queries**:
```python
class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_jobs_with_relations(self) -> list[Job]:
        """
        Fetch all active jobs with eager-loaded relationships:
        - quotation
        - quotation.customer
        - payments
        - measurements
        - activity_logs (latest only)
        
        Use: selectinload() for collections, joinedload() for single relations
        """
        
    def get_kpi_counts(self) -> dict:
        """
        Single query with multiple COUNT aggregations using CASE statements
        """
        
    def get_recent_activity_logs(self, limit: int = 10) -> list[ActivityLog]:
        """
        Fetch recent activity logs with eager-loaded job and customer
        ORDER BY created_at DESC
        LIMIT {limit}
        """
```

**Optimized KPI Query Example**:
```python
def get_kpi_counts(self) -> dict:
    """
    Single SQL query to calculate all KPIs using COUNT with CASE
    """
    from sqlalchemy import func, case
    from datetime import date as dt_date
    
    today = dt_date.today()
    
    result = self.db.query(
        # Total active jobs
        func.count(Job.id).filter(
            Job.status.in_([
                JobStatus.PENDING,
                JobStatus.MEASURING,
                JobStatus.IN_PRODUCTION,
                JobStatus.READY_FOR_INSTALLATION,
                JobStatus.INSTALLED
            ])
        ).label("total_active_jobs"),
        
        # Measurements scheduled today
        func.count(Job.id).filter(
            Job.measurement_date == today
        ).label("measurements_today"),
        
        # Installations scheduled today
        func.count(Job.id).filter(
            Job.installation_date == today
        ).label("installations_today"),
        
    ).one()
    
    return result._asdict()
```


**Optimized Active Jobs Query Example**:
```python
def get_active_jobs_with_relations(self) -> list[Job]:
    """
    Fetch all active jobs with all needed relations in minimal queries
    """
    from sqlalchemy.orm import selectinload, joinedload
    
    jobs = (
        self.db.query(Job)
        .filter(
            Job.status.in_([
                JobStatus.PENDING,
                JobStatus.MEASURING,
                JobStatus.IN_PRODUCTION,
                JobStatus.READY_FOR_INSTALLATION,
                JobStatus.INSTALLED,
                JobStatus.COMPLETED,
            ])
        )
        .options(
            joinedload(Job.quotation).joinedload(Quotation.customer),
            selectinload(Job.payments),
            selectinload(Job.measurements),
            selectinload(Job.activity_logs).limit(1),  # Only latest
        )
        .all()
    )
    
    return jobs
```

---

#### 4. Schemas (DTOs)

**File**: `app/schemas/dashboard.py`

**Schema Definitions**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class KPIsDTO(BaseModel):
    total_active_jobs: int
    quotations_waiting_response: int
    measurements_scheduled_today: int
    installations_scheduled_today: int
    overdue_payments: int
    jobs_delayed: int
```



class PaymentProgressDTO(BaseModel):
    paid: float
    total: float
    percentage: float

class JobPipelineCardDTO(BaseModel):
    job_id: str
    quotation_number: str
    customer_name: str
    current_status: str
    assigned_engineer: Optional[str] = None
    last_activity: str  # relative time
    days_in_stage: int
    payment_progress: PaymentProgressDTO
    priority: str  # 'high' | 'medium' | 'low'
    measurement_date: Optional[str] = None
    installation_date: Optional[str] = None
    is_overdue: bool

class PipelineDTO(BaseModel):
    quotation: list[JobPipelineCardDTO]
    measurement: list[JobPipelineCardDTO]
    depositReceived: list[JobPipelineCardDTO] = Field(alias="deposit_received")
    manufacturing: list[JobPipelineCardDTO]
    installation: list[JobPipelineCardDTO]
    completed: list[JobPipelineCardDTO]
    rejected: list[JobPipelineCardDTO]

class AlertDTO(BaseModel):
    id: str
    type: str
    severity: str  # 'critical' | 'warning' | 'info'
    title: str
    description: str
    entity_id: str
    entity_type: str
    days_overdue: int

class ActivityDTO(BaseModel):
    id: str
    type: str
    description: str
    timestamp: datetime
    relative_time: str
    entity_id: str
    entity_type: str
    customer_name: str
```



class MetadataDTO(BaseModel):
    generated_at: datetime
    execution_time_ms: int

class DashboardResponse(BaseModel):
    kpis: KPIsDTO
    pipeline: PipelineDTO
    alerts: list[AlertDTO]
    recent_activity: list[ActivityDTO] = Field(alias="recentActivity")
    metadata: MetadataDTO
    
    class Config:
        populate_by_name = True
```

---

## Data Models

### Dashboard Response Schema

The primary data model for the dashboard is `DashboardResponse`, which aggregates all operational data in a single API response. See "Schemas (DTOs)" section in Components and Interfaces for complete definitions.

### Entity Relationships

The dashboard data model leverages existing ERP entities:
- **Job** → **Quotation** → **Customer** (core relationship chain)
- **Job** → **Payments[]** (payment tracking)
- **Job** → **Measurements[]** (measurement scheduling)
- **Job** → **ActivityLog[]** (activity history)

### Pipeline Stage Mapping

Jobs are mapped to pipeline stages based on `Job.status` and related payment/quotation status. See "Business Logic Rules" section for complete mapping table.

---

## Correctness Properties

### Data Consistency

1. **KPI Accuracy**: All KPI counts MUST match actual database state at time of query execution
2. **Pipeline Completeness**: Every active job MUST appear in exactly one pipeline column
3. **Payment Progress**: Payment progress percentage MUST equal (sum of paid amounts) / (sum of total amounts) * 100
4. **Alert Accuracy**: Alerts MUST only be generated when thresholds defined in business rules are met
5. **Activity Chronology**: Recent activity MUST be ordered by created_at timestamp descending

### Performance Guarantees

1. **Response Time**: API endpoint MUST respond within 500ms for databases with up to 1000 active jobs
2. **Query Efficiency**: Dashboard data MUST be retrieved using no more than 4 database queries (no N+1)
3. **Memory Usage**: Frontend MUST handle rendering up to 200 job cards without performance degradation

### Business Rule Enforcement

1. **Priority Calculation**: Job priority MUST be deterministic based on defined rules
2. **Stage Transitions**: Pipeline stage mapping MUST reflect both job status and payment conditions
3. **Alert Severity**: Alert severity levels MUST match defined thresholds consistently

---

## Error Handling

### Backend Error Scenarios

| Error Condition | HTTP Status | Response | Recovery Strategy |
|----------------|-------------|----------|-------------------|
| Database connection failure | 503 Service Unavailable | `{"error": "Service temporarily unavailable"}` | Retry with exponential backoff |
| Query timeout (>5s) | 504 Gateway Timeout | `{"error": "Request timeout"}` | Retry with reduced query scope |
| Invalid data in database | 200 OK | Partial data + warning in logs | Skip invalid records, return valid data |
| Unexpected exception | 500 Internal Server Error | `{"error": "Internal server error"}` | Log full traceback, alert monitoring |

### Frontend Error Scenarios

| Error Condition | User Experience | Recovery Action |
|----------------|-----------------|-----------------|
| Network error | "Unable to connect to server" message + retry button | User clicks retry → re-fetch |
| HTTP 5xx | "Server error occurred" message + retry button | User clicks retry → re-fetch |
| Timeout (>10s) | "Request timed out" message + retry button | User clicks retry → re-fetch |
| Partial API response | Render available data + error banner for missing sections | Auto-retry failed sections after 5s |
| Cache stale (>30s) | Display refresh indicator icon | Auto-refresh on user click |

### Graceful Degradation

1. **Missing Job Data**: If job missing required fields, exclude from pipeline but include in alert
2. **Missing Customer Name**: Display "Unknown Customer" placeholder
3. **Missing Payment Data**: Display payment progress as 0% instead of error
4. **No Activity Logs**: Display "No recent activities" empty state
5. **No Alerts**: Display "No critical alerts" empty state

---

## Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│  Frontend: DashboardPage mounts                                 │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  HTTP GET /api/v1/dashboard                                     │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  DashboardRouter: Route handler                                 │
│  - Inject database session                                      │
│  - Create DashboardService instance                             │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  DashboardService: get_dashboard_data()                         │
│  1. Call repository.get_active_jobs_with_relations()            │
│  2. Call repository.get_kpi_counts()                            │
│  3. Call repository.get_recent_activity_logs(limit=10)          │
│  4. Calculate derived metrics (priority, payment %)             │
│  5. Map jobs to pipeline stages                                 │
│  6. Generate alerts based on business rules                     │
│  7. Format activity with relative time                          │
│  8. Assemble DashboardResponse DTO                              │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  DashboardRepository: Execute optimized SQL                     │
│  - Query 1: KPI counts (single aggregation query)               │
│  - Query 2: Active jobs with eager-loaded relations             │
│  - Query 3: Recent activity logs (LIMIT 10)                     │
│  Total queries: ~3-4 (no N+1 problem)                           │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  PostgreSQL: Execute queries with indexes                       │
│  - Use indexes on: status, measurement_date, installation_date  │
│  - JOIN quotations, customers, payments                         │
│  - Return aggregated results                                    │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  DashboardResponse JSON returned to frontend                    │
│  Target: <500ms total execution time                            │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Frontend: Render dashboard components                          │
│  - KPIGrid renders 6 cards                                      │
│  - PipelineBoard renders 7 columns with job cards               │
│  - AlertsPanel renders sorted alerts                            │
│  - RecentActivity renders timeline                              │
│  - Auto-refresh every 30 seconds                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Performance Optimization Strategy

### Backend Optimizations

1. **Single Aggregated Endpoint**: One API call instead of multiple
2. **SQL Aggregations**: COUNT, SUM, AVG calculated in database
3. **Eager Loading**: Use selectinload/joinedload to avoid N+1
4. **Database Indexes**: Ensure indexes on frequently queried columns
5. **Query Result Caching**: Consider Redis for 30-second cache (future)
6. **Connection Pooling**: SQLAlchemy pool configured appropriately


### Frontend Optimizations

1. **Response Caching**: React Query with 30-second staleTime
2. **Lazy Loading**: Code-split dashboard page if needed
3. **Skeleton Loaders**: Display placeholders during load
4. **Debounced Refresh**: Prevent refresh spam
5. **Virtualized Lists**: If pipeline columns have >50 cards (future)
6. **Memoization**: Use React.memo for JobPipelineCard

---

## Database Indexes Required

Ensure the following indexes exist (most should already exist from migrations):

```sql
-- Jobs table
CREATE INDEX IF NOT EXISTS ix_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS ix_jobs_measurement_date ON jobs(measurement_date);
CREATE INDEX IF NOT EXISTS ix_jobs_installation_date ON jobs(installation_date);
CREATE INDEX IF NOT EXISTS ix_jobs_completion_date ON jobs(completion_date);

-- Quotations table
CREATE INDEX IF NOT EXISTS ix_quotations_status ON quotations(status);

-- Payments table
CREATE INDEX IF NOT EXISTS ix_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS ix_payments_due_date ON payments(due_date);

-- Activity logs table
CREATE INDEX IF NOT EXISTS ix_activity_logs_created_at ON activity_logs(created_at);
```

---

## Business Logic Rules

### Pipeline Stage Mapping

| Job Status              | Payment Condition       | Pipeline Stage    |
|------------------------|-------------------------|-------------------|
| PENDING                | Any                     | Quotation         |
| MEASURING              | Any                     | Measurement       |
| IN_PRODUCTION          | Deposit NOT paid        | Measurement       |
| IN_PRODUCTION          | Deposit PAID            | Deposit Received  |
| READY_FOR_INSTALLATION | Any                     | Manufacturing     |
| INSTALLED              | Any                     | Installation      |
| COMPLETED              | ≤7 days since completion | Completed         |
| COMPLETED              | >7 days since completion | Hidden            |
| CANCELLED              | Quotation REJECTED       | Rejected          |
| CANCELLED              | Other                    | Hidden            |

### Job Priority Rules

| Condition                                    | Priority |
|---------------------------------------------|----------|
| Days in stage > expected duration           | High     |
| Has overdue payment                         | High     |
| Days in stage ≥ 80% of expected duration    | Medium   |
| Otherwise                                   | Low      |

### Expected Duration Per Stage

| Job Status              | Expected Duration (days) |
|------------------------|--------------------------|
| PENDING                | 7                        |
| MEASURING              | 3                        |
| IN_PRODUCTION          | 14                       |
| READY_FOR_INSTALLATION | 7                        |
| INSTALLED              | 3                        |

### Alert Generation Rules

| Alert Type                | Condition                                                    | Severity |
|--------------------------|-------------------------------------------------------------|----------|
| Quotation Waiting        | Quotation status = SENT AND >14 days since sent_date        | Warning  |
| Quotation Waiting        | Quotation status = SENT AND >21 days since sent_date        | Critical |
| Measurement Overdue      | Job status = MEASURING AND >7 days in stage                 | Critical |
| Manufacturing Delayed    | Job status = IN_PRODUCTION AND >21 days in stage            | Warning  |
| Manufacturing Delayed    | Job status = IN_PRODUCTION AND >30 days in stage            | Critical |
| Installation Overdue     | Job status = READY_FOR_INSTALLATION AND >10 days in stage   | Critical |
| Payment Overdue          | Payment status = OVERDUE AND 1-7 days past due              | Warning  |
| Payment Overdue          | Payment status = OVERDUE AND >7 days past due               | Critical |
| Job Inactive             | No activity log entries in last 7 days                      | Warning  |

---

## Future Extensibility Architecture

The design supports adding these features later without major refactoring:

### 1. Drag & Drop Between Stages

**Frontend Changes**:
- Add `react-beautiful-dnd` library
- Wrap `PipelineColumn` in `Droppable`
- Wrap `JobPipelineCard` in `Draggable`
- Add `onDragEnd` handler to `PipelineBoard`
- Call API to update job status when card dropped

**Backend Changes**:
- Add `PATCH /api/v1/jobs/{job_id}/status` endpoint
- Validate status transitions
- Update job status and log activity

**No changes needed**: Component structure, data fetching, schemas

---

### 2. Calendar View

**Frontend Changes**:
- Add `DashboardViewToggle` component (Board | Calendar)
- Create `CalendarView` component using existing `dashboardData`
- Display jobs on calendar by measurement_date or installation_date

**Backend Changes**:
- None - calendar view uses same API response

**No changes needed**: API, repository, service logic

---

### 3. Engineer Workload

**Frontend Changes**:
- Add `assigned_engineer` filter in `DashboardFilters`
- Display engineer-specific metrics in new KPI card
- Highlight jobs assigned to selected engineer

**Backend Changes**:
- Add `assigned_engineer` field to Job model (migration)
- Update DashboardRepository query to include engineer filter
- Add engineer workload KPI calculation

**No changes needed**: Component architecture remains same

---

### 4. Charts & Reports

**Frontend Changes**:
- Add `ChartsSection` component below pipeline
- Use recharts or similar library
- Display revenue trends, job completion rates, etc.

**Backend Changes**:
- Add `GET /api/v1/dashboard/analytics` endpoint
- DashboardRepository adds time-series queries
- Return aggregated metrics grouped by week/month

**No changes needed**: Existing dashboard endpoint and components

---

### 5. AI Recommendations

**Frontend Changes**:
- Add `RecommendationsPanel` component
- Display AI-generated suggestions (e.g., "Job #123 may need priority")

**Backend Changes**:
- Add `GET /api/v1/dashboard/recommendations` endpoint
- Implement ML model or rule-based AI engine
- Analyze job patterns and suggest actions

**No changes needed**: Core dashboard structure

---

## Error Handling Strategy

### Frontend Error Handling

1. **Network Errors**: Display "Unable to connect" with retry button
2. **HTTP 4xx**: Display "Invalid request" (unlikely for GET)
3. **HTTP 5xx**: Display "Server error, please try again" with retry
4. **Timeout**: Display "Request timed out" after 10 seconds
5. **Partial Failures**: If API returns partial data, render what's available + error indicator

### Backend Error Handling

1. **Database Connection Failure**: Return HTTP 503 Service Unavailable
2. **Query Timeout**: Return HTTP 504 Gateway Timeout
3. **Invalid Data**: Log error, skip invalid records, return partial data
4. **Unexpected Exception**: Log full traceback, return HTTP 500 with generic message

---

## Testing Strategy

### Frontend Testing

**Unit Tests**:
- KPICard rendering with different props
- JobPipelineCard priority color logic
- Relative time formatting functions
- Alert severity sorting

**Integration Tests**:
- DashboardPage fetches data and renders components
- Auto-refresh triggers API call after 30 seconds
- Error states display correctly

**E2E Tests** (Playwright/Cypress):
- Dashboard loads with real data
- Click job card navigates to job detail page
- Click alert navigates to related entity
- Responsive layout on mobile/tablet/desktop

### Backend Testing

**Unit Tests**:
- DashboardService._calculate_job_priority() logic
- DashboardService._map_job_to_pipeline_stage() mapping
- Alert generation rules
- Relative time formatting

**Integration Tests**:
- GET /api/v1/dashboard returns 200 with valid schema
- Response includes all expected fields
- KPI calculations match database state
- Pipeline stages contain correct jobs

**Performance Tests**:
- Measure response time with 100 jobs in database
- Verify <500ms target
- Check query count (should be ≤4)
- Load test with concurrent requests

---

## Monitoring & Observability

### Metrics to Track

1. **Response Time**: P50, P95, P99 for `/api/v1/dashboard`
2. **Error Rate**: 4xx and 5xx responses
3. **Database Query Time**: Time spent in repository layer
4. **Active Jobs Count**: Trend over time
5. **Alert Count**: Number of critical alerts generated


### Logging

**Backend**:
```python
logger.info(
    "Dashboard data requested",
    extra={
        "execution_time_ms": execution_time,
        "active_jobs_count": len(jobs),
        "alerts_count": len(alerts)
    }
)
```

**Frontend**:
```javascript
console.log('[Dashboard] Data loaded', {
  kpis: data.kpis,
  pipelineJobCount: Object.values(data.pipeline).flat().length,
  executionTime: data.metadata.executionTimeMs
});
```

---

## Security Considerations

1. **Authentication**: Dashboard endpoint requires authenticated user (future)
2. **Authorization**: Users can only see jobs/customers they have permission for (future)
3. **Rate Limiting**: Implement rate limiting on API endpoint (e.g., 60 requests/minute)
4. **SQL Injection**: Use SQLAlchemy ORM - parameterized queries only
5. **Data Exposure**: Don't expose sensitive payment details in pipeline cards

---

## Internationalization

### Translation Keys

**KPI Labels**:
```json
{
  "dashboard.kpi.totalActiveJobs": "Total Active Jobs",
  "dashboard.kpi.quotationsWaiting": "Quotations Waiting",
  "dashboard.kpi.measurementsToday": "Measurements Today",
  "dashboard.kpi.installationsToday": "Installations Today",
  "dashboard.kpi.overduePayments": "Overdue Payments",
  "dashboard.kpi.jobsDelayed": "Jobs Delayed"
}
```

**Pipeline Stages**:
```json
{
  "dashboard.pipeline.quotation": "Quotation",
  "dashboard.pipeline.measurement": "Measurement",
  "dashboard.pipeline.depositReceived": "Deposit Received",
  "dashboard.pipeline.manufacturing": "Manufacturing",
  "dashboard.pipeline.installation": "Installation",
  "dashboard.pipeline.completed": "Completed",
  "dashboard.pipeline.rejected": "Rejected"
}
```


**Alert Types**:
```json
{
  "dashboard.alert.quotationWaiting": "Quotation Waiting for Customer Response",
  "dashboard.alert.measurementOverdue": "Measurement Overdue",
  "dashboard.alert.manufacturingDelayed": "Manufacturing Delayed",
  "dashboard.alert.installationOverdue": "Installation Overdue",
  "dashboard.alert.paymentOverdue": "Payment Overdue",
  "dashboard.alert.jobInactive": "Job Inactive"
}
```

**Activity Types**:
```json
{
  "dashboard.activity.customerCreated": "Customer created",
  "dashboard.activity.quotationCreated": "Quotation created",
  "dashboard.activity.quotationApproved": "Quotation approved",
  "dashboard.activity.measurementCompleted": "Measurement completed",
  "dashboard.activity.paymentReceived": "Payment received",
  "dashboard.activity.jobStarted": "Job started",
  "dashboard.activity.installationCompleted": "Installation completed"
}
```

---

## File Structure

### Backend Files

```
app/
├── api/
│   └── v1/
│       ├── dashboard.py          # NEW: Dashboard router
│       └── router.py             # MODIFIED: Add dashboard router
├── services/
│   └── dashboard.py              # NEW: DashboardService
├── repositories/
│   └── dashboard.py              # NEW: DashboardRepository
└── schemas/
    └── dashboard.py              # NEW: Dashboard DTOs
```

### Frontend Files

```
frontend/src/
├── pages/
│   └── Dashboard.tsx             # MODIFIED: Replace existing
├── components/
│   └── dashboard/
│       ├── KPIGrid.tsx           # NEW
│       ├── KPICard.tsx           # NEW
│       ├── PipelineBoard.tsx     # NEW
│       ├── PipelineColumn.tsx    # NEW
│       ├── JobPipelineCard.tsx   # NEW
│       ├── AlertsPanel.tsx       # NEW
│       ├── RecentActivity.tsx    # NEW
│       └── DashboardFilters.tsx  # FUTURE
├── hooks/
│   └── useDashboard.ts           # NEW: Custom hook for data fetching
└── types/
    └── dashboard.ts              # NEW: TypeScript types
```

---

## Implementation Phases

### Phase 1: Backend Foundation (Priority 1)
1. Create DashboardRepository with optimized queries
2. Create DashboardService with business logic
3. Create dashboard schemas/DTOs
4. Create dashboard router endpoint
5. Write unit tests for service logic
6. Write integration tests for API endpoint
7. Measure and optimize query performance

**Deliverable**: Working `/api/v1/dashboard` endpoint returning mock-compatible data

---

### Phase 2: Frontend Core Components (Priority 2)
1. Create TypeScript types for dashboard data
2. Create useDashboard hook for data fetching
3. Create KPICard component
4. Create KPIGrid component
5. Update DashboardPage to use new components
6. Add loading and error states
7. Add auto-refresh mechanism

**Deliverable**: Dashboard page showing KPI cards with real data

---

### Phase 3: Pipeline Board (Priority 3)
1. Create JobPipelineCard component with all details
2. Create PipelineColumn component
3. Create PipelineBoard component
4. Implement horizontal scroll
5. Add priority color coding
6. Add click navigation to job detail

**Deliverable**: Visual pipeline board showing all active jobs

---

### Phase 4: Alerts & Activity (Priority 4)
1. Create AlertsPanel component
2. Implement alert severity sorting
3. Create RecentActivity component
4. Implement relative time formatting
5. Add click navigation for alerts and activities

**Deliverable**: Complete operational dashboard with all sections

---

### Phase 5: Polish & Optimization (Priority 5)
1. Add responsive design for mobile/tablet
2. Implement caching with React Query
3. Add skeleton loaders
4. Performance testing and optimization
5. Accessibility improvements (ARIA labels, keyboard nav)
6. Write E2E tests

**Deliverable**: Production-ready dashboard meeting performance targets

---

## Acceptance Criteria Mapping

This design addresses all requirements from requirements.md with the following architectural adjustments:

### Approved Requirements (Implemented)

✅ **Req 1**: Real-Time Business Metrics Display  
→ Implemented via KPIs section with 6 operational metrics

✅ **Req 3**: Job Pipeline Monitoring  
→ Implemented via PipelineBoard as primary feature

✅ **Req 4**: Payment and Revenue Tracking  
→ Implemented via payment progress in JobPipelineCard + KPI

✅ **Req 5**: Activity Feed and Recent Operations  
→ Implemented via RecentActivity component

✅ **Req 6**: Alert System for Critical Events  
→ Implemented via AlertsPanel with severity sorting

✅ **Req 8**: Backend API for Dashboard Metrics  
→ Implemented via single aggregated endpoint

✅ **Req 9**: Backend API for Activity Feed  
→ Included in single dashboard endpoint

✅ **Req 10**: Backend API for Alerts  
→ Included in single dashboard endpoint

✅ **Req 12**: Responsive Design and Mobile Support  
→ Grid layout adapts to screen size

✅ **Req 13**: Internationalization Support  
→ Translation keys defined for all text

✅ **Req 14**: Error Handling and Loading States  
→ Skeleton loaders, error messages, retry logic

✅ **Req 15**: Performance and Optimization  
→ Single API call, SQL aggregations, caching

### Architectural Changes from Original Requirements

❌ **Req 2**: Quotation Conversion Analytics (Charts removed)  
→ **Reason**: Operational dashboard prioritizes daily tasks over analytics  
→ **Future**: Can be added in separate analytics section

❌ **Req 7**: Visual Data Representations (Charts removed)  
→ **Reason**: Charts don't help gallery assistant with "what needs attention today"  
→ **Future**: Add charts tab or separate analytics dashboard

❌ **Req 11**: Backend API for Time-Series Data (Not needed)  
→ **Reason**: No charts = no time-series requirements  
→ **Future**: Add when implementing analytics features


### New Operational Features (Not in Original Requirements)

✅ **Pipeline-Centric Design**: Main feature is visual job board  
✅ **Actionable KPIs**: Metrics focused on today's tasks  
✅ **Job Priority System**: Visual indicators for urgent items  
✅ **Days in Stage Tracking**: Shows how long jobs have been in current status  
✅ **Payment Progress Bars**: Visual representation of payment status  
✅ **Smart Auto-Hide**: Completed jobs hidden after 7 days  

---

## Summary

This design transforms the dashboard from a generic business metrics display into a true **operations control center** for gallery assistants. The architecture:

1. **Prioritizes Daily Operations**: KPIs answer "what needs my attention today?"
2. **Centers on Pipeline**: Main feature is visual board showing job flow
3. **Provides Context**: Each job card shows all relevant information at a glance
4. **Surfaces Urgency**: Priority colors and alerts highlight what's critical
5. **Performs Efficiently**: Single aggregated API call, <500ms target
6. **Supports Growth**: Architecture allows adding drag & drop, calendar, charts, AI later

The design adheres to the approved requirements while shifting focus from analytics to operations, making it a practical tool for daily ERP management.

---

## Questions for Clarification

Before implementation, please confirm:

1. **Engineer Assignment**: Should we add `assigned_engineer` field to Job model now, or leave for future?
2. **Payment Progress Calculation**: Should it be based on amount paid vs total, or percentage of payment milestones completed?
3. **Activity Tracking**: Should we use existing ActivityLog model, or do we need more granular tracking?
4. **Auto-refresh Interval**: 30 seconds acceptable, or different cadence needed?
5. **Completed Jobs**: 7-day auto-hide confirmed, or different timeframe?

---

*Design Document Version: 1.0*  
*Last Updated: 2024-01-15*  
*Status: Ready for Review*
