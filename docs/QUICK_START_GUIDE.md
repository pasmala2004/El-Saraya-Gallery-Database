# Quick Start - Implementation Guide

## Your Next 3 Tasks (DO THIS FIRST)

### Task 1: Create JobRepository (2 hours)
```python
# app/repositories/job.py

class JobRepository(GenericRepository[Job]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Job)
    
    async def list_by_status(self, status: JobStatus) -> list[Job]:
        stmt = select(Job).where(Job.status == status)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_by_customer(self, customer_id: UUID) -> list[Job]:
        stmt = select(Job).join(Quotation).where(
            Quotation.customer_id == customer_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
```

**Then**: Add to `app/api/deps.py` for dependency injection

---

### Task 2: Create JobService (3 hours)
```python
# app/services/job.py

class JobService(BaseService[Job]):
    def __init__(
        self,
        session: AsyncSession,
        repository: JobRepository,
        quotation_repository: QuotationRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Job")
        self._quotations = quotation_repository or QuotationRepository(session)
    
    async def create_from_quotation(self, quotation_id: UUID) -> Job:
        # Verify quotation exists and is APPROVED
        # Create Job with status=PENDING
        # Link to quotation
        # Return created job
        
    async def update_status(self, job_id: UUID, new_status: JobStatus) -> Job:
        # Validate status transition
        # Update job status
        # Return updated job
```

**Key Business Rules:**
- Can only create job from APPROVED quotation
- Status transitions: pending → measuring → in_production → ... → completed
- Cannot modify completed jobs

---

### Task 3: Create API Routes (2 hours)
```python
# app/api/v1/jobs.py

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=JobListResponse)
async def list_jobs(
    service: Annotated[JobService, Depends(get_job_service)],
    status: JobStatus | None = None,
    limit: int = 20,
    offset: int = 0,
):
    # List jobs with optional status filter

@router.post("/quotations/{quotation_id}/jobs", response_model=JobRead)
async def create_job_from_quotation(
    quotation_id: UUID,
    service: Annotated[JobService, Depends(get_job_service)],
):
    # Create job from approved quotation

@router.patch("/{job_id}/status", response_model=JobRead)
async def update_job_status(
    job_id: UUID,
    body: JobStatusUpdate,
    service: Annotated[JobService, Depends(get_job_service)],
):
    # Update job status with validation
```

**Then**: Add to `app/api/v1/router.py`:
```python
from app.api.v1 import jobs
router.include_router(jobs.router)
```

---

## Pattern Reference: Copy from Quotations

### For JobRepository → Copy from: QuotationRepository
- Pattern: Inherited GenericRepository + custom queries
- Same: Filtering, pagination, sorting

### For JobService → Copy from: QuotationService
- Pattern: Status validation, business rules, multi-repo coordination
- **Reference the allowed transitions structure**

### For API Routes → Copy from: quotations.py
- Pattern: FastAPI routes, dependency injection, error handling
- Same: Response models, query parameters, status codes

---

## Frontend Integration (When Backend Ready)

### 1. Create API Service
```typescript
// frontend/src/services/jobs.ts
import axios from 'axios';
import { Job, JobStatus } from '../types';

export async function listJobs(status?: JobStatus) {
  const response = await axios.get('/api/v1/jobs', {
    params: { status }
  });
  return response.data;
}

export async function createJobFromQuotation(quotationId: string) {
  const response = await axios.post(
    `/api/v1/quotations/${quotationId}/jobs`
  );
  return response.data;
}

export async function updateJobStatus(jobId: string, status: JobStatus) {
  const response = await axios.patch(
    `/api/v1/jobs/${jobId}/status`,
    { status }
  );
  return response.data;
}
```

### 2. Update Jobs Page
```tsx
// frontend/src/pages/Jobs.tsx
import { useTranslation, translateJobStatus } from '../i18n';
import { formatDate } from '../utils';

export default function Jobs() {
  const { t } = useTranslation();
  
  // Load jobs from API
  // Display as table with:
  // - Job number
  // - Customer (via quotation)
  // - Status (translated to Arabic)
  // - Dates (formatted with ar-EG locale)
  // - Action buttons
}
```

### 3. Add Type Definitions
```typescript
// frontend/src/types/index.ts
export interface Job {
  id: string;
  quotation_id: string;
  status: JobStatus;
  measurement_date?: string;
  production_start?: string;
  production_end?: string;
  installation_date?: string;
  completion_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export type JobStatus = 
  | 'pending'
  | 'measuring'
  | 'in_production'
  | 'ready_for_installation'
  | 'installed'
  | 'completed'
  | 'cancelled';
```

---

## Files Checklist

### Backend Files to Create
- [ ] `app/repositories/job.py`
- [ ] `app/repositories/measurement.py`
- [ ] `app/services/job.py`
- [ ] `app/services/measurement.py`
- [ ] `app/schemas/job.py`
- [ ] `app/schemas/measurement.py`
- [ ] `app/api/v1/jobs.py`

### Frontend Files to Create/Update
- [ ] `frontend/src/services/jobs.ts`
- [ ] `frontend/src/pages/Jobs.tsx` (update from placeholder)
- [ ] Update `frontend/src/types/index.ts` with Job types

### Configuration Updates
- [ ] `app/api/v1/router.py` - add jobs router
- [ ] `app/api/deps.py` - add get_job_service dependency

---

## Testing Checklist

### Backend Tests
- [ ] Create job from approved quotation
- [ ] Reject creation from non-approved quotation
- [ ] Verify status transitions work
- [ ] Prevent invalid status changes
- [ ] List jobs by status
- [ ] List jobs by customer

### Frontend Tests
- [ ] Load jobs list from API
- [ ] Display job status in Arabic
- [ ] Format dates correctly (ar-EG)
- [ ] Click to view job detail
- [ ] Update job status button works

### Integration Tests
- [ ] Full workflow: Create quotation → Approve → Create job → Update status

---

## Architecture Decisions Already Made ✅

**Use These - Don't Change:**

1. ✅ Repository pattern with GenericRepository base
2. ✅ Service layer owns transactions
3. ✅ Pydantic for input/output validation
4. ✅ FastAPI for routes
5. ✅ Async/await throughout
6. ✅ Domain exceptions for errors
7. ✅ React Query for frontend data fetching
8. ✅ Arabic translations for UI text

**Follow These Patterns - Don't Invent New Ones:**

1. ✅ QuotationService for status lifecycle
2. ✅ CustomerRepository for filtering/searching
3. ✅ quotations.py API routes for endpoint structure
4. ✅ Error handling from core/exceptions.py

---

## Success Criteria

When Phase 1 (Jobs) is done:
✅ Create job from approved quotation  
✅ List jobs with status filter  
✅ Update job status  
✅ Record measurements  
✅ Full UI in Arabic  
✅ All tests passing  

---

## Time Estimate

| Task | Hours | Duration |
|------|-------|----------|
| JobRepository | 2 | Morning |
| JobService | 3 | Half day |
| API Routes | 2 | Morning |
| Schemas | 1 | 1 hour |
| Frontend Services | 2 | Morning |
| Frontend Pages | 3 | Half day |
| Testing | 2 | Morning |
| Fixes | 2 | If needed |
| **TOTAL** | **18** | **2-3 days** |

---

## No Unknowns - Everything is Clear ✅

- ✅ Database schema exists
- ✅ Models are defined
- ✅ Patterns are proven (from Quotations)
- ✅ Architecture is correct
- ✅ No refactoring needed

**You can start now with confidence.**

---

## Questions? Reference These:

- Database schema: `alembic/versions/a18031e1652d_*`
- Similar service: `app/services/quotation.py`
- Similar routes: `app/api/v1/quotations.py`
- Similar repository: `app/repositories/quotation.py`
- Frontend example: `frontend/src/pages/Quotations.tsx`

All answers are in the existing code.

---

**Status**: 🟢 READY TO START  
**Risk**: 🟢 LOW  
**Confidence**: 🟢 HIGH  

Begin whenever ready. Pattern is proven. Path is clear.
