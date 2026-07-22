# Technical Design: Automatic Job Creation on Quotation Approval

## Overview

This feature implements automatic job creation when a quotation is approved, eliminating manual workflow steps and ensuring data consistency. When a user approves a quotation, the system will atomically create the corresponding job and activity log entry, with proper rollback on failure.

## High-Level Design

### Current Workflow (Manual)
```
User → Approve Quotation
     ↓
Quotation status = "approved"
     ↓
User navigates to Jobs page
     ↓
User clicks "Create Job"
     ↓
User selects quotation from dropdown
     ↓
Job created
```

**Problems:**
- Manual steps create friction
- Approved quotations can exist without jobs
- No atomic transaction guarantee
- Users can forget to create job

### New Workflow (Automatic)
```
User → Approve Quotation
     ↓
Backend Transaction:
  1. Update quotation.status = "approved"
  2. Create job record (quotation_id → job)
  3. Create activity log entry
  4. COMMIT or ROLLBACK ALL
     ↓
Response to Frontend:
  - Quotation object (with status = approved)
  - Job object (newly created)
     ↓
Frontend:
  - Invalidate queries (quotations, jobs, dashboard)
  - Navigate to job details page
```

**Benefits:**
- Atomic operation (all-or-nothing)
- Zero manual steps
- Data consistency guaranteed
- Immediate feedback

### System Components Affected

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                            │
├─────────────────────────────────────────────────────────┤
│  ProjectDetails.tsx                                      │
│  └─ handleApproveQuotation()                            │
│     └─ quotationsApi.updateStatus(id, 'approved')      │
│        └─ Receives: { quotation, job }                  │
│        └─ Navigate to /jobs/{job.id}                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                  Backend API Layer                       │
├─────────────────────────────────────────────────────────┤
│  app/api/v1/quotations.py                               │
│  └─ PATCH /quotations/{id}/status                       │
│     └─ Validates status transition                      │
│     └─ Calls service layer                              │
│     └─ Returns: QuotationWithJobResponse                │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                           │
├─────────────────────────────────────────────────────────┤
│  app/services/quotation.py                              │
│  └─ update_quotation_status()                           │
│     └─ if new_status == "approved":                     │
│        └─ create_job_from_quotation()                   │
│           └─ Within same DB transaction:                │
│              1. Update quotation status                  │
│              2. Create job                               │
│              3. Create activity log                      │
│              4. COMMIT or ROLLBACK                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                Repository Layer                          │
├─────────────────────────────────────────────────────────┤
│  app/repositories/quotation.py                          │
│  app/repositories/job.py                                │
│  app/repositories/activity_log.py (if exists)           │
└─────────────────────────────────────────────────────────┘
```

### Data Model

```python
# Existing tables - no schema changes needed
Quotation
├─ id: UUID
├─ status: QuotationStatus
└─ ...

Job
├─ id: UUID
├─ quotation_id: UUID (FK)
├─ status: JobStatus = 'pending'
└─ ...

ActivityLog (if exists)
├─ id: UUID
├─ job_id: UUID (FK)
├─ action: str
├─ description: str
└─ created_at: datetime
```

### Transaction Guarantee

```sql
BEGIN TRANSACTION;
  -- Step 1: Update quotation
  UPDATE quotations 
  SET status = 'approved', updated_at = NOW()
  WHERE id = :quotation_id;
  
  -- Step 2: Create job
  INSERT INTO jobs (id, quotation_id, status, created_at, updated_at)
  VALUES (:job_id, :quotation_id, 'pending', NOW(), NOW());
  
  -- Step 3: Create activity log
  INSERT INTO activity_logs (id, job_id, action, description, created_at)
  VALUES (:log_id, :job_id, 'job_created', 'Job created from approved quotation', NOW());
  
COMMIT;  -- Or ROLLBACK on any error
```

## Low-Level Design

### Backend Implementation

#### 1. New Response Schema
```python
# app/schemas/quotation.py

from pydantic import BaseModel
from typing import Optional
from .job import JobRead

class QuotationStatusUpdate(BaseModel):
    status: QuotationStatus

class QuotationWithJobResponse(BaseModel):
    """Response when approval creates a job"""
    quotation: QuotationRead
    job: Optional[JobRead] = None
    
    class Config:
        from_attributes = True
```

#### 2. Service Layer Logic
```python
# app/services/quotation.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Quotation, Job, ActivityLog
from app.schemas.quotation import QuotationWithJobResponse
from app.repositories import quotation_repo, job_repo
import uuid

async def update_quotation_status(
    db: Session,
    quotation_id: str,
    new_status: QuotationStatus
) -> QuotationWithJobResponse:
    """
    Update quotation status.
    If status changes to 'approved', automatically create job.
    """
    try:
        # Get existing quotation
        quotation = await quotation_repo.get_by_id(db, quotation_id)
        if not quotation:
            raise NotFoundException("Quotation not found")
        
        # Check if quotation already has a job
        existing_job = await job_repo.get_by_quotation_id(db, quotation_id)
        
        # Update status
        quotation.status = new_status
        quotation.updated_at = datetime.utcnow()
        
        created_job = None
        
        # Auto-create job on approval
        if new_status == QuotationStatus.APPROVED and not existing_job:
            created_job = await _create_job_from_quotation(
                db, 
                quotation
            )
        
        # Commit transaction
        db.commit()
        db.refresh(quotation)
        
        if created_job:
            db.refresh(created_job)
        
        return QuotationWithJobResponse(
            quotation=quotation,
            job=created_job
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Failed to update quotation: {str(e)}")


async def _create_job_from_quotation(
    db: Session,
    quotation: Quotation
) -> Job:
    """
    Create job from approved quotation.
    Called within the same transaction.
    """
    job_data = {
        "id": str(uuid.uuid4()),
        "quotation_id": quotation.id,
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    job = Job(**job_data)
    db.add(job)
    db.flush()  # Get ID but don't commit yet
    
    # Create activity log
    activity = ActivityLog(
        id=str(uuid.uuid4()),
        job_id=job.id,
        action="job_created",
        description="Job automatically created from approved quotation",
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    return job
```

#### 3. API Endpoint Update
```python
# app/api/v1/quotations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.quotation import QuotationStatusUpdate, QuotationWithJobResponse
from app.services import quotation_service
from app.api.deps import get_db

router = APIRouter()

@router.patch(
    "/{quotation_id}/status",
    response_model=QuotationWithJobResponse
)
async def update_quotation_status(
    quotation_id: str,
    status_update: QuotationStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update quotation status.
    
    When status changes to 'approved', automatically creates
    a job and returns both quotation and job in response.
    
    Transaction is atomic - if job creation fails,
    quotation status update is rolled back.
    """
    try:
        result = await quotation_service.update_quotation_status(
            db=db,
            quotation_id=quotation_id,
            new_status=status_update.status
        )
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 4. Repository Helper
```python
# app/repositories/job.py

from sqlalchemy.orm import Session
from app.models import Job
from typing import Optional

class JobRepository:
    # ... existing methods ...
    
    async def get_by_quotation_id(
        self,
        db: Session,
        quotation_id: str
    ) -> Optional[Job]:
        """Check if job already exists for quotation"""
        return db.query(Job).filter(
            Job.quotation_id == quotation_id
        ).first()
```

### Frontend Implementation

#### 1. Update API Service
```typescript
// frontend/src/services/quotations.ts

export interface QuotationWithJobResponse {
  quotation: Quotation;
  job: Job | null;
}

export const quotationsApi = {
  // ... existing methods ...
  
  updateStatus: async (
    id: string, 
    status: QuotationStatus
  ): Promise<QuotationWithJobResponse> => {
    const { data } = await api.patch<QuotationWithJobResponse>(
      `/quotations/${id}/status`, 
      { status }
    );
    return data;
  },
};
```

#### 2. Update Component Handler
```typescript
// frontend/src/pages/ProjectDetails.tsx

const updateQuotationStatusMutation = useMutation({
  mutationFn: (status: QuotationStatus) => 
    quotationsApi.updateStatus(activeQuotation!.id, status),
  onSuccess: (response) => {
    toast.success(t('success.updated'));
    
    // Invalidate all affected queries
    queryClient.invalidateQueries({ queryKey: ['quotations'] });
    queryClient.invalidateQueries({ queryKey: ['jobs'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    
    // If job was created, navigate to it
    if (response.job) {
      navigate(`/jobs/${response.job.id}`);
    } else {
      setIsStatusModalOpen(false);
    }
  },
  onError: () => toast.error(t('errors.generic')),
});
```

### Error Handling

#### Backend Error Scenarios
```python
# Scenario 1: Quotation not found
if not quotation:
    raise NotFoundException("Quotation not found")

# Scenario 2: Job already exists
if existing_job:
    # Just update status, don't create duplicate job
    # Return existing job in response
    return QuotationWithJobResponse(
        quotation=quotation,
        job=existing_job
    )

# Scenario 3: Database constraint violation
try:
    db.commit()
except IntegrityError:
    db.rollback()
    raise DatabaseException("Failed to create job")

# Scenario 4: Any other error
except Exception as e:
    db.rollback()
    raise DatabaseException(f"Unexpected error: {str(e)}")
```

#### Frontend Error Handling
```typescript
onError: (error) => {
  // Show error toast
  toast.error(t('errors.jobCreationFailed'));
  
  // Don't navigate away - stay on quotation page
  // User can retry or contact support
  setIsStatusModalOpen(false);
}
```

## Migration Strategy

### Phase 1: Backend Implementation
1. ✅ Add `QuotationWithJobResponse` schema
2. ✅ Implement `_create_job_from_quotation()` helper
3. ✅ Update `update_quotation_status()` service method
4. ✅ Update API endpoint response type
5. ✅ Add database transaction handling

### Phase 2: Frontend Integration
1. ✅ Update `quotationsApi.updateStatus()` types
2. ✅ Handle response with job object
3. ✅ Add navigation to job details on success
4. ✅ Update cache invalidation

### Phase 3: UI Cleanup (Future)
1. Remove "Create Job" button from Jobs page
2. Remove job creation modal
3. Update user documentation

## Testing Strategy

### Backend Tests
```python
def test_approve_quotation_creates_job():
    """Approving quotation should create job"""
    quotation = create_test_quotation(status="sent")
    
    response = update_quotation_status(
        db, quotation.id, QuotationStatus.APPROVED
    )
    
    assert response.quotation.status == QuotationStatus.APPROVED
    assert response.job is not None
    assert response.job.quotation_id == quotation.id
    assert response.job.status == JobStatus.PENDING

def test_approve_quotation_rollback_on_error():
    """Failed job creation should rollback quotation approval"""
    quotation = create_test_quotation(status="sent")
    
    # Simulate database error
    with patch('db.commit', side_effect=SQLAlchemyError):
        with pytest.raises(DatabaseException):
            update_quotation_status(
                db, quotation.id, QuotationStatus.APPROVED
            )
    
    # Verify quotation status unchanged
    db.refresh(quotation)
    assert quotation.status == QuotationStatus.SENT

def test_approve_already_approved_quotation():
    """Approving already-approved quotation with existing job"""
    quotation = create_test_quotation(status="approved")
    existing_job = create_test_job(quotation_id=quotation.id)
    
    response = update_quotation_status(
        db, quotation.id, QuotationStatus.APPROVED
    )
    
    assert response.job.id == existing_job.id
    # No duplicate job created
```

### Frontend Tests
```typescript
test('approving quotation navigates to job details', async () => {
  const mockResponse = {
    quotation: { id: 'q1', status: 'approved' },
    job: { id: 'j1', quotation_id: 'q1' }
  };
  
  mockApi.patch.mockResolvedValue({ data: mockResponse });
  
  render(<ProjectDetails />);
  await userEvent.click(screen.getByText('Approve'));
  
  await waitFor(() => {
    expect(navigate).toHaveBeenCalledWith('/jobs/j1');
  });
});
```

## Rollout Plan

1. **Deploy Backend** - With backward compatibility
2. **Test in Staging** - Verify atomic transactions
3. **Deploy Frontend** - Users see immediate navigation
4. **Monitor** - Check for errors in logs
5. **Cleanup** - Remove old "Create Job" UI (future sprint)

## Success Metrics

- ✅ 100% of approved quotations have corresponding jobs
- ✅ Zero orphaned approved quotations
- ✅ <500ms response time for approval + job creation
- ✅ Zero transaction rollbacks in production
- ✅ User workflow reduced by 3 clicks

## Security Considerations

- ✅ Transaction atomicity prevents inconsistent state
- ✅ Existing permissions model applies (who can approve)
- ✅ Activity log records audit trail
- ✅ No new security vulnerabilities introduced

## Performance Impact

- Negligible: Single INSERT into jobs table (~5ms)
- Single INSERT into activity_logs table (~5ms)
- Total overhead: ~10ms added to approval operation
- Benefits: Eliminates separate API call for job creation

## Alternative Approaches Considered

### ❌ Approach 1: Keep Manual Job Creation
**Rejected:** User friction, data inconsistency risk

### ❌ Approach 2: Create Job via Frontend API Call
**Rejected:** Not atomic, network failure risk

### ✅ Approach 3: Backend Atomic Transaction (Selected)
**Chosen:** Atomic, consistent, eliminates user steps
