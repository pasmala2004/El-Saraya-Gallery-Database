# Implementation Tasks: Automatic Job Creation on Quotation Approval

## Task 1: Backend - Add Response Schema
**Status:** completed  
**Priority:** high  
**Estimated effort:** 15 minutes

### Description
Create new response schema for quotation status update that includes optional job object when approval creates a job.

### Acceptance Criteria
- [x] `QuotationWithJobResponse` schema created in `app/schemas/quotation.py`
- [x] Includes `quotation: QuotationRead` field
- [x] Includes `job: Optional[JobRead]` field
- [x] Schema has proper Pydantic config for ORM mode

### Implementation Notes
```python
# app/schemas/quotation.py
from typing import Optional
from .job import JobRead

class QuotationWithJobResponse(BaseModel):
    quotation: QuotationRead
    job: Optional[JobRead] = None
    
    class Config:
        from_attributes = True
```

---

## Task 2: Backend - Add Repository Helper Method
**Status:** completed  
**Priority:** high  
**Estimated effort:** 15 minutes

### Description
Add helper method to check if a job already exists for a quotation to prevent duplicate job creation.

### Acceptance Criteria
- [x] `get_by_quotation_id()` method added to `JobRepository`
- [x] Returns `Optional[Job]`
- [x] Filters by `quotation_id`
- [x] Returns first match or None

### Implementation Notes
```python
# app/repositories/job.py
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

---

## Task 3: Backend - Implement Job Creation Helper
**Status:** completed  
**Priority:** high  
**Estimated effort:** 30 minutes

### Description
Create internal service helper that creates a job from an approved quotation within the same database transaction.

### Acceptance Criteria
- [x] `_create_job_from_quotation()` function created in `app/services/quotation.py`
- [x] Creates Job with status='pending'
- [x] Creates ActivityLog entry with action='job_created'
- [x] Uses `db.flush()` not `db.commit()` (transaction continues)
- [x] Returns Job instance
- [x] Handles UUID generation

### Implementation Notes
```python
# app/services/quotation.py
import uuid
from datetime import datetime

async def _create_job_from_quotation(
    db: Session,
    quotation: Quotation
) -> Job:
    job = Job(
        id=str(uuid.uuid4()),
        quotation_id=quotation.id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.flush()
    
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

---

## Task 4: Backend - Update Quotation Status Service
**Status:** completed  
**Priority:** high  
**Estimated effort:** 45 minutes

### Description
Modify the quotation status update service to automatically create job when status changes to 'approved', with atomic transaction handling.

### Acceptance Criteria
- [x] `update_quotation_status()` updated in `app/services/quotation.py`
- [x] Check if job already exists before creating
- [x] Call `_create_job_from_quotation()` when status='approved' and no job exists
- [x] All operations in single transaction
- [x] Rollback on any error
- [x] Return `QuotationWithJobResponse`
- [x] Refresh both quotation and job objects after commit

### Implementation Notes
```python
async def update_quotation_status(
    db: Session,
    quotation_id: str,
    new_status: QuotationStatus
) -> QuotationWithJobResponse:
    try:
        quotation = await quotation_repo.get_by_id(db, quotation_id)
        if not quotation:
            raise NotFoundException("Quotation not found")
        
        existing_job = await job_repo.get_by_quotation_id(db, quotation_id)
        
        quotation.status = new_status
        quotation.updated_at = datetime.utcnow()
        
        created_job = None
        if new_status == QuotationStatus.APPROVED and not existing_job:
            created_job = await _create_job_from_quotation(db, quotation)
        
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
```

---

## Task 5: Backend - Update API Endpoint
**Status:** completed  
**Priority:** high  
**Estimated effort:** 20 minutes

### Description
Update the quotation status API endpoint to use new response schema and handle new service response.

### Acceptance Criteria
- [x] `PATCH /quotations/{id}/status` endpoint updated
- [x] Response model changed to `QuotationWithJobResponse`
- [x] Error handling for `NotFoundException` and `DatabaseException`
- [x] API documentation updated with new response structure
- [x] Status codes remain: 200 (success), 404 (not found), 500 (error)

### Implementation Notes
```python
# app/api/v1/quotations.py
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

---

## Task 6: Backend - Run Diagnostics and Test
**Status:** completed  
**Priority:** high  
**Estimated effort:** 15 minutes

### Description
Verify backend implementation has no TypeScript/linting errors and test the endpoint manually.

### Acceptance Criteria
- [x] No Python linting errors
- [x] No import errors
- [x] Backend server starts successfully
- [x] Test approval endpoint via Swagger/curl
- [x] Verify job is created in database
- [x] Verify activity log is created
- [x] Verify rollback works (simulate error)

### Test Command
```bash
# Start backend
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Test via curl
curl -X PATCH http://localhost:8000/api/v1/quotations/{id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

---

## Task 7: Frontend - Update API Types
**Status:** completed  
**Priority:** high  
**Estimated effort:** 15 minutes

### Description
Update frontend API service to handle new response structure from quotation status update.

### Acceptance Criteria
- [x] `QuotationWithJobResponse` interface created in `frontend/src/types/index.ts`
- [x] `quotationsApi.updateStatus()` return type updated
- [x] Handles response with both quotation and job objects

### Implementation Notes
```typescript
// frontend/src/types/index.ts
export interface QuotationWithJobResponse {
  quotation: Quotation;
  job: Job | null;
}

// frontend/src/services/quotations.ts
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
```

---

## Task 8: Frontend - Update ProjectDetails Component
**Status:** completed  
**Priority:** high  
**Estimated effort:** 30 minutes

### Description
Update the approval handler in ProjectDetails to navigate to job page when job is created and invalidate all affected caches.

### Acceptance Criteria
- [x] `updateQuotationStatusMutation` handles new response type
- [x] Navigates to `/jobs/{job.id}` when job is created
- [x] Invalidates 'quotations', 'jobs', and 'dashboard' queries
- [x] Shows success toast
- [x] Shows error toast on failure
- [x] Stays on quotation page if no job created (non-approval status)

### Implementation Notes
```typescript
// frontend/src/pages/ProjectDetails.tsx
const updateQuotationStatusMutation = useMutation({
  mutationFn: (status: QuotationStatus) => 
    quotationsApi.updateStatus(activeQuotation!.id, status),
  onSuccess: (response) => {
    toast.success(t('success.updated'));
    
    queryClient.invalidateQueries({ queryKey: ['quotations'] });
    queryClient.invalidateQueries({ queryKey: ['jobs'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    
    if (response.job) {
      navigate(`/jobs/${response.job.id}`);
    } else {
      setIsStatusModalOpen(false);
    }
  },
  onError: () => toast.error(t('errors.generic')),
});
```

---

## Task 9: Frontend - Update Jobs Page (Remove Create Job Button)
**Status:** pending  
**Priority:** low  
**Estimated effort:** 15 minutes

### Description
Remove or hide the "Create Job" button and modal from Jobs page since jobs are now created automatically on approval.

### Acceptance Criteria
- [ ] "Add Project" button removed or hidden from Jobs page header
- [ ] Create job modal removed or commented out
- [ ] `handleCreateJob` function removed or commented out
- [ ] Clean up unused state variables
- [ ] Clean up unused query for available quotations

### Implementation Notes
```typescript
// frontend/src/pages/Jobs.tsx
// Remove or comment out:
// - Add Project button in header
// - isCreateModalOpen state
// - selectedQuotationId state
// - handleCreateJob function
// - Create Job Modal JSX
```

**Note:** This is optional cleanup and can be done in a future sprint.

---

## Task 10: Frontend - Update QuotationsWaitingPanel on Dashboard
**Status:** pending  
**Priority:** low  
**Estimated effort:** 20 minutes

### Description
Update dashboard panel that shows approved quotations to use the new automatic job creation flow.

### Acceptance Criteria
- [ ] Remove "Create Job" button from quotations waiting panel
- [ ] Update to show that job is created automatically
- [ ] Update tooltips/help text to reflect new workflow
- [ ] Ensure cache invalidation refreshes the panel

### Implementation Notes
This component may no longer need "Create Job" actions since jobs are created automatically. Review `frontend/src/components/dashboard/QuotationsWaitingPanel.tsx` and update accordingly.

**Note:** This is optional cleanup and can be done in a future sprint.

---

## Task 11: Frontend - Run Diagnostics and Test
**Status:** pending  
**Priority:** high  
**Estimated effort:** 20 minutes

### Description
Verify frontend implementation has no errors and test the complete approval flow end-to-end.

### Acceptance Criteria
- [ ] No TypeScript errors
- [ ] No linting errors
- [ ] Frontend compiles successfully
- [ ] Test approval flow:
  - [ ] Open quotation details
  - [ ] Click "Approve" button
  - [ ] Verify success toast appears
  - [ ] Verify navigation to job details page
  - [ ] Verify job ID in URL
  - [ ] Verify job details load correctly
  - [ ] Verify dashboard updates
  - [ ] Verify projects list updates
- [ ] Test error handling (disconnect backend, approve, verify error toast)

### Test Steps
```bash
# Start frontend
cd frontend
npm run dev

# Manual testing:
1. Navigate to quotation details (non-approved)
2. Click "Approve" button
3. Observe automatic navigation to job details
4. Verify job was created
5. Check dashboard for updates
6. Check projects list for new job
```

---

## Task 12: Integration Testing
**Status:** pending  
**Priority:** high  
**Estimated effort:** 30 minutes

### Description
Perform end-to-end integration testing of the complete workflow with both backend and frontend running.

### Acceptance Criteria
- [ ] Create test quotation with items
- [ ] Approve quotation via frontend
- [ ] Verify job created in database
- [ ] Verify activity log created
- [ ] Verify navigation to job details
- [ ] Verify dashboard reflects changes
- [ ] Test idempotency (approve already-approved quotation)
- [ ] Test rollback (simulate database error)
- [ ] Test with multiple quotations
- [ ] Test with different quotation statuses

### Test Scenarios
1. **Happy Path:** Draft → Approved → Job Created → Navigate
2. **Already Approved:** Approve again → No duplicate job
3. **Error Handling:** Database down → No approval, no job
4. **Multiple Approvals:** Approve 3 quotations → 3 jobs created
5. **Status Changes:** Draft → Sent → Approved → Job only on approved

---

## Implementation Order

### Phase 1: Backend (Tasks 1-6)
Execute in order: 1 → 2 → 3 → 4 → 5 → 6

**Estimated time:** 2.5 hours

### Phase 2: Frontend (Tasks 7-11)
Execute in order: 7 → 8 → 11 (Tasks 9-10 are optional cleanup)

**Estimated time:** 1.5 hours

### Phase 3: Integration (Task 12)
Execute after both backend and frontend complete

**Estimated time:** 30 minutes

### Total Estimated Time: 4.5 hours

---

## Rollback Plan

If issues are discovered in production:

1. **Backend Rollback:** Deploy previous version of `quotation_service.py` and `quotations.py` API
2. **Frontend Rollback:** Deploy previous version with manual job creation
3. **Data Cleanup:** Identify and handle any orphaned jobs (unlikely due to transaction atomicity)

---

## Success Metrics

After deployment, monitor:
- ✅ 100% of approved quotations have jobs
- ✅ Zero failed transactions in logs
- ✅ User complaints about manual job creation = 0
- ✅ Average approval-to-job-details time < 2 seconds
- ✅ Zero duplicate jobs created

---

## Notes

- All tasks marked as "high" priority must be completed for feature to work
- Tasks marked "low" priority are cleanup and can be deferred
- Backend changes are backward compatible
- Frontend gracefully handles old API response (no job field)
- Database schema unchanged - no migrations needed
