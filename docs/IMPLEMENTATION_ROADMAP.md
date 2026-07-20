# Implementation Roadmap - Detailed Guidance

## Phase 1: Jobs Module (2-3 Days)

### Step 1: Create JobRepository

**File**: `app/repositories/job.py`

**Pattern to Follow** (from QuotationRepository):
```python
class JobRepository(GenericRepository[Job]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Job)
    
    async def list_by_status(self, status: JobStatus) -> list[Job]:
        # Filter jobs by status
        
    async def list_by_customer(self, customer_id: UUID) -> list[Job]:
        # Via quotation join
        
    async def search(self, filters: JobFilters) -> tuple[list[Job], int]:
        # Status, date range, customer filters
```

**What to include**:
- Filter by status (pending, in_production, etc.)
- Filter by date range (production_start, installation_date)
- List by customer (join through quotation)
- Count by status for dashboard

---

### Step 2: Create MeasurementRepository

**File**: `app/repositories/measurement.py`

**Pattern**:
```python
class MeasurementRepository(GenericRepository[Measurement]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Measurement)
    
    async def list_by_job(self, job_id: UUID) -> list[Measurement]:
        # Get all measurements for a job
        
    async def get_latest(self, job_id: UUID) -> Measurement | None:
        # Most recent measurement visit
```

---

### Step 3: Create JobService

**File**: `app/services/job.py`

**Key Business Logic**:
```python
# Status lifecycle:
# pending → measuring → in_production → ready_for_installation → 
# installed → completed (or cancelled at any point)

# Rules:
# - Can only create from APPROVED quotation
# - Cannot modify completed jobs
# - measurement_date triggers "measuring" status
# - production_start triggers "in_production"
# - installation_date triggers "installed"
# - completion_date triggers "completed"

# Multi-repo orchestration:
# - QuotationRepository (verify approved)
# - JobRepository (CRUD)
# - MeasurementRepository (manage measurements)
# - PaymentRepository (later: ensure payments tracked)
```

**Implementation Reference**: Use QuotationService as template for:
- Status transition validation
- Business rule enforcement
- Multi-repository coordination

---

### Step 4: Create MeasurementService

**File**: `app/services/measurement.py`

**Responsibilities**:
```python
# Create measurement for a job
# Add measurement items (link to quotation items)
# Record visit details (date, who measured, notes)
# Support multiple measurements per job (measurement_number auto-increments)
```

---

### Step 5: Create API Routes

**File**: `app/api/v1/jobs.py`

**Endpoints**:
```
GET    /jobs                       # List jobs (filter by status, dates)
GET    /jobs/{job_id}              # Job detail with measurements
POST   /quotations/{q_id}/jobs     # Create job from approved quotation
PATCH  /jobs/{job_id}/status       # Advance job status
GET    /jobs/{job_id}/measurements # List measurements for job
POST   /jobs/{job_id}/measurements # Record site measurement
GET    /measurements/{m_id}        # Measurement detail
```

**Add to router**: `app/api/v1/router.py`
```python
from app.api.v1 import jobs
router.include_router(jobs.router)
```

---

### Step 6: Create Frontend Services

**File**: `frontend/src/services/jobs.ts`

```typescript
// API calls:
// - listJobs(filters)
// - getJob(id)
// - createJobFromQuotation(quotationId)
// - updateJobStatus(jobId, newStatus)
// - recordMeasurement(jobId, data)
// - listMeasurements(jobId)
```

---

### Step 7: Create Frontend Pages

**File**: `frontend/src/pages/Jobs.tsx`

**Components**:
1. JobsList - table with status badges
2. JobDetail - view job + measurements + payments
3. MeasurementForm - record site measurements
4. StatusTransition - buttons to advance status

**Arabic Integration** (Already set up):
```tsx
const { t } = useTranslation();
<h1>{t('jobs.title')}</h1>
<span>{translateJobStatus(job.status)}</span>
<p>{formatDate(job.production_start)}</p>
```

---

## Phase 2: Payments Module (2 Days)

### Step 1: Create PaymentRepository

**File**: `app/repositories/payment.py`

**Methods**:
```python
# Filter by:
# - status (pending, paid, overdue)
# - due_date range
# - payment_type (deposit, production, final)
# 
# Special: Calculate overdue (due_date < today and status != paid)
```

---

### Step 2: Create PaymentService

**File**: `app/services/payment.py`

**Business Logic**:
```python
# Record payment received
# Mark as paid (paid_date = today)
# Calculate outstanding balance
# Prevent overpayment (optional strict mode)
# Support partial payments

# Installment rules:
# - Payments must follow payment_order sequence
# - Each has payment_type (Deposit/Production/Final)
# - Percentage-based or fixed amount
# - Cannot delete, only cancel
```

---

### Step 3: Create API Routes

**File**: `app/api/v1/payments.py`

**Endpoints**:
```
GET    /jobs/{job_id}/payments          # Payment schedule
GET    /payments/{payment_id}           # Payment detail
POST   /payments                        # Record payment
PATCH  /payments/{payment_id}/status    # Mark paid/cancel
```

---

### Step 4-6: Frontend (Services, Pages, Components)

**Same pattern as Phase 1**
- `payments.ts` service
- `Payments.tsx` page
- Payment schedule, record payment dialog

---

## Implementation Checklist

### Jobs Module
- [ ] JobRepository (2 hrs)
- [ ] MeasurementRepository (1 hr)
- [ ] JobService (3 hrs)
- [ ] MeasurementService (2 hrs)
- [ ] API routes (2 hrs)
- [ ] Schemas (1 hr)
- [ ] Frontend services (2 hrs)
- [ ] Frontend pages (3 hrs)
- **Total**: 16 hours

### Payments Module
- [ ] PaymentRepository (1 hr)
- [ ] PaymentService (2 hrs)
- [ ] API routes (2 hrs)
- [ ] Schemas (1 hr)
- [ ] Frontend services (1 hr)
- [ ] Frontend pages (2 hrs)
- **Total**: 9 hours

### Testing & Fixes
- [ ] Integration testing (2 hrs)
- [ ] Bug fixes (2 hrs)
- **Total**: 4 hours

**Grand Total**: ~29 hours (4 development days)

---

## Code Quality Standards (Already Followed)

✅ Use existing patterns - don't invent new ones
✅ Type everything with TypeScript/Pydantic
✅ Write docstrings on public methods
✅ Test business rules in services
✅ Translate UI strings to Arabic
✅ Format currency/dates with provided utilities
✅ Handle errors with domain exceptions
✅ Use proper async/await

---

## Files to Create Summary

### Backend
```
app/
├── repositories/
│   ├── job.py
│   ├── measurement.py
│   └── payment.py
├── services/
│   ├── job.py
│   ├── measurement.py
│   └── payment.py
├── schemas/
│   ├── job.py
│   ├── measurement.py
│   └── payment.py
└── api/v1/
    ├── jobs.py
    ├── measurements.py (or in jobs.py)
    └── payments.py
```

### Frontend
```
frontend/src/
├── services/
│   ├── jobs.ts
│   ├── measurements.ts (or in jobs.ts)
│   └── payments.ts
└── pages/
    ├── Jobs.tsx (update from placeholder)
    └── Payments.tsx (update from placeholder)
```

---

## Testing Strategy

**Backend Testing**:
1. Create Job from Quotation (check status, relationship)
2. Advance Job status (validate transitions)
3. Record Measurement (link to items)
4. Record Payment (track amount, status)

**Frontend Testing**:
1. Load Jobs list (with real API)
2. View Job detail (show measurements)
3. Create measurement (save to backend)
4. Record payment (update outstanding balance)

---

## Success Criteria

✅ All Jobs/Payments endpoints functional  
✅ Status transitions working correctly  
✅ UI displays Arabic text  
✅ Currency/dates formatted properly  
✅ Business rules enforced (no invalid states)  
✅ Database relationships consistent  
✅ No N+1 queries  
✅ Error messages clear  

---

## Risk Mitigation

**If Jobs becomes complex:**
- Break status transitions into smaller methods
- Add extensive docstrings
- Reference QuotationService pattern

**If Payments has edge cases:**
- Document business rules first
- Add payment-specific tests
- Start with simple case (single payment)
- Add installments later

---

## Go/No-Go Checklist

Before starting Phase 1:
- [ ] Database schema verified (already done ✅)
- [ ] Models reviewed (already done ✅)
- [ ] Patterns understood (from existing code)
- [ ] Team aligned on requirements
- [ ] Design documents available

**Status**: 🟢 **READY TO START**
