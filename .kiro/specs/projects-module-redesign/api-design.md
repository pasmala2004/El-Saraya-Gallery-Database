# Projects Module - API Design

**Feature ID**: `projects-module-redesign`  
**Version**: 1.0  
**Created**: 2026-07-21

---

## API Strategy

**Principle**: Reuse existing endpoints wherever possible. Only create new endpoints when aggregation is required for performance.

**Existing Endpoints**: 90% reused  
**New Endpoints**: 10% (optional, for optimization)

---

## Existing Endpoints (Reused)

### Jobs (Projects)

#### List All Jobs
```http
GET /api/v1/jobs
```

**Query Parameters**:
- None required (fetch all)

**Response**: `200 OK`
```json
{
  "jobs": [
    {
      "id": 123,
      "quotation_id": 456,
      "customer_id": 789,
      "status": "measuring",
      "priority": "high",
      "measurement_date": "2026-07-25",
      "production_start": null,
      "production_end": null,
      "installation_date": null,
      "completion_date": null,
      "expected_delivery_date": "2026-08-15",
      "notes": "Customer prefers morning",
      "created_at": "2026-07-21T10:00:00Z",
      "updated_at": "2026-07-21T14:30:00Z"
    }
  ]
}
```

**Usage**: Project list page  
**Frontend Aggregation**: Yes (enrich with customer, quotation, payment data)  
**Performance**: <1s for 100 jobs

---

#### Get Single Job
```http
GET /api/v1/jobs/{id}
```

**Path Parameters**:
- `id` (integer, required): Job ID

**Response**: `200 OK`
```json
{
  "id": 123,
  "quotation_id": 456,
  "customer_id": 789,
  "status": "measuring",
  "priority": "high",
  "measurement_date": "2026-07-25",
  "production_start": null,
  "production_end": null,
  "installation_date": null,
  "completion_date": null,
  "expected_delivery_date": "2026-08-15",
  "notes": "Customer prefers morning installations",
  "created_at": "2026-07-21T10:00:00Z",
  "updated_at": "2026-07-21T14:30:00Z"
}
```

**Errors**:
- `404 Not Found`: Job does not exist

**Usage**: Project details page header  
**Performance**: <200ms

---

#### Update Job
```http
PUT /api/v1/jobs/{id}
```

**Path Parameters**:
- `id` (integer, required): Job ID

**Request Body**:
```json
{
  "status": "in_production",
  "priority": "high",
  "measurement_date": "2026-07-25",
  "production_start": "2026-07-26",
  "production_end": null,
  "installation_date": null,
  "completion_date": null,
  "expected_delivery_date": "2026-08-15",
  "notes": "Updated notes"
}
```

**Response**: `200 OK`
```json
{
  "id": 123,
  "status": "in_production",
  // ... updated fields
  "updated_at": "2026-07-21T15:00:00Z"
}
```

**Errors**:
- `404 Not Found`: Job does not exist
- `400 Bad Request`: Invalid status transition
- `422 Unprocessable Entity`: Validation error

**Usage**: Workflow stage completion, date updates  
**Side Effects**: May create ActivityLog entry (backend)

---

### Quotations

#### Get Quotation
```http
GET /api/v1/quotations/{id}
```

**Path Parameters**:
- `id` (integer, required): Quotation ID

**Response**: `200 OK`
```json
{
  "id": 456,
  "quotation_number": "QT-2024-0456",
  "customer_id": 789,
  "status": "approved",
  "final_price": "50000.00",
  "discount": 10.00,
  "valid_until": "2026-08-01",
  "notes": "10% discount applied",
  "created_at": "2026-07-10T09:00:00Z",
  "items": [
    {
      "id": 1,
      "product_id": 101,
      "product_name": "Kitchen Cabinet Set",
      "quantity": 1,
      "unit_price": "30000.00",
      "total": "30000.00"
    },
    {
      "id": 2,
      "product_id": 102,
      "product_name": "Bedroom Wardrobe",
      "quantity": 2,
      "unit_price": "12500.00",
      "total": "25000.00"
    }
  ]
}
```

**Usage**: Project details page quotation section  
**Performance**: <200ms

---

#### Update Quotation Status
```http
PATCH /api/v1/quotations/{id}/status
```

**Path Parameters**:
- `id` (integer, required): Quotation ID

**Request Body**:
```json
{
  "status": "approved"
}
```

**Response**: `200 OK`
```json
{
  "id": 456,
  "status": "approved",
  "job": {
    "id": 123,
    "quotation_id": 456,
    "status": "pending",
    // ... job fields
  }
}
```

**Side Effects**: 
- Creates Job automatically if status = 'approved'
- Creates ActivityLog entry

**Usage**: Approve quotation button in project details

---

### Payments

#### List Payments for Job
```http
GET /api/v1/payments?job_id={job_id}
```

**Query Parameters**:
- `job_id` (integer, required): Filter by job

**Response**: `200 OK`
```json
{
  "payments": [
    {
      "id": 1,
      "job_id": 123,
      "payment_order": 1,
      "payment_type": "deposit",
      "payment_method": "bank",
      "percentage": 30.00,
      "amount": "15000.00",
      "due_date": "2026-07-20",
      "paid_date": "2026-07-19",
      "status": "paid",
      "notes": "Bank transfer received",
      "created_at": "2026-07-15T09:00:00Z"
    },
    {
      "id": 2,
      "job_id": 123,
      "payment_order": 2,
      "payment_type": "production",
      "payment_method": "cash",
      "percentage": 40.00,
      "amount": "20000.00",
      "due_date": "2026-08-05",
      "paid_date": null,
      "status": "pending",
      "notes": "",
      "created_at": "2026-07-15T09:05:00Z"
    }
  ]
}
```

**Usage**: Project details payments section  
**Frontend Calculation**: Total paid, remaining, progress percentage  
**Performance**: <200ms

---

#### Create Payment
```http
POST /api/v1/payments
```

**Request Body**:
```json
{
  "job_id": 123,
  "payment_order": 3,
  "payment_type": "final",
  "payment_method": "instapay",
  "percentage": 30.00,
  "amount": "15000.00",
  "due_date": "2026-08-20",
  "notes": "Final payment on completion"
}
```

**Response**: `201 Created`
```json
{
  "id": 3,
  "job_id": 123,
  "payment_order": 3,
  "payment_type": "final",
  "payment_method": "instapay",
  "percentage": 30.00,
  "amount": "15000.00",
  "due_date": "2026-08-20",
  "paid_date": null,
  "status": "pending",
  "notes": "Final payment on completion",
  "created_at": "2026-07-21T16:00:00Z"
}
```

**Errors**:
- `404 Not Found`: Job does not exist
- `422 Unprocessable Entity`: Validation error (negative amount, missing fields)

**Side Effects**: Creates ActivityLog entry ("Payment added")

**Usage**: Add payment modal in project details

---

#### Mark Payment as Paid
```http
PATCH /api/v1/payments/{id}/status
```

**Path Parameters**:
- `id` (integer, required): Payment ID

**Request Body**:
```json
{
  "status": "paid",
  "paid_date": "2026-07-21"
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "status": "paid",
  "paid_date": "2026-07-21",
  // ... other fields
  "updated_at": "2026-07-21T16:30:00Z"
}
```

**Side Effects**: Creates ActivityLog entry ("Payment #1 marked paid")

**Usage**: Mark as paid button in payments section

---

### Measurements

#### List Measurements for Job
```http
GET /api/v1/measurements?job_id={job_id}
```

**Query Parameters**:
- `job_id` (integer, required): Filter by job

**Response**: `200 OK`
```json
{
  "measurements": [
    {
      "id": 1,
      "job_id": 123,
      "visit_date": "2026-07-22",
      "measured_by": "Ahmed Hassan",
      "notes": "Measured kitchen and bedrooms",
      "created_at": "2026-07-21T10:00:00Z",
      "items": [
        {
          "id": 1,
          "measurement_id": 1,
          "room": "Kitchen",
          "width": 3.50,
          "height": 2.80,
          "quantity": 1,
          "notes": "U-shaped layout"
        },
        {
          "id": 2,
          "measurement_id": 1,
          "room": "Master Bedroom",
          "width": 4.00,
          "height": 2.60,
          "quantity": 1,
          "notes": "Corner wardrobe"
        }
      ]
    }
  ]
}
```

**Usage**: Project details measurements section  
**Performance**: <200ms

---

#### Create Measurement
```http
POST /api/v1/measurements
```

**Request Body**:
```json
{
  "job_id": 123,
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "Second visit for additional rooms"
}
```

**Response**: `201 Created`
```json
{
  "id": 2,
  "job_id": 123,
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "Second visit for additional rooms",
  "created_at": "2026-07-21T17:00:00Z",
  "items": []
}
```

**Side Effects**: Creates ActivityLog entry ("Measurement #2 scheduled")

**Usage**: Add measurement modal in project details

---

### Customers

#### Get Customer
```http
GET /api/v1/customers/{id}
```

**Path Parameters**:
- `id` (integer, required): Customer ID

**Response**: `200 OK`
```json
{
  "id": 789,
  "name": "Mohamed Ali",
  "phone": "+201234567890",
  "address": "123 Main St, Cairo, Egypt",
  "notes": "Prefers morning appointments",
  "created_at": "2026-01-15T08:00:00Z"
}
```

**Usage**: Project details customer section, project list enrichment  
**Performance**: <100ms

---

### Activity Logs

#### List Activity Logs for Job
```http
GET /api/v1/activity-logs?job_id={job_id}
```

**Query Parameters**:
- `job_id` (integer, required): Filter by job

**Response**: `200 OK`
```json
{
  "activity_logs": [
    {
      "id": 1,
      "job_id": 123,
      "user_id": null,
      "action": "project_created",
      "description": "Project created from Quotation QT-2024-0456",
      "metadata": {
        "quotation_id": 456,
        "customer_id": 789
      },
      "created_at": "2026-07-21T10:00:00Z"
    },
    {
      "id": 2,
      "job_id": 123,
      "user_id": 1,
      "action": "quotation_approved",
      "description": "Quotation QT-2024-0456 approved",
      "metadata": {
        "quotation_id": 456
      },
      "created_at": "2026-07-21T10:15:00Z"
    },
    {
      "id": 3,
      "job_id": 123,
      "user_id": 1,
      "action": "payment_added",
      "description": "Payment #1 added: EGP 15,000",
      "metadata": {
        "payment_id": 1,
        "amount": "15000.00",
        "payment_type": "deposit"
      },
      "created_at": "2026-07-21T11:00:00Z"
    }
  ]
}
```

**Usage**: Project details timeline and activity sections  
**Performance**: <300ms  
**Sorting**: Descending by `created_at` (newest first)

---

## New Endpoints (Optional)

### Project Summary (Aggregated Data)

**Status**: Optional - implement only if performance issues occur with multiple requests

```http
GET /api/v1/projects/{id}/summary
```

**Purpose**: Single request for all project header data

**Path Parameters**:
- `id` (integer, required): Job ID

**Response**: `200 OK`
```json
{
  "project": {
    "project_id": 123,
    "job_id": 123,
    "quotation_id": 456,
    "quotation_number": "QT-2024-0456",
    
    "customer": {
      "id": 789,
      "name": "Mohamed Ali",
      "phone": "+201234567890",
      "address": "123 Main St, Cairo, Egypt"
    },
    
    "status": "measuring",
    "priority": "high",
    
    "financial": {
      "total": 50000.00,
      "paid": 15000.00,
      "remaining": 35000.00,
      "progress": 30.00,
      "overdue_amount": 0.00
    },
    
    "dates": {
      "created": "2026-07-21T10:00:00Z",
      "expected_delivery": "2026-08-15",
      "last_updated": "2026-07-21T14:30:00Z"
    },
    
    "stages": {
      "quotation": { "completed": true, "date": "2026-07-21" },
      "measurement": { "completed": false, "date": null },
      "deposit": { "completed": false, "date": null },
      "production": { "completed": false, "date": null },
      "installation": { "completed": false, "date": null },
      "completed": { "completed": false, "date": null }
    }
  }
}
```

**Backend Implementation**:
```python
# app/api/v1/projects.py
@router.get("/{id}/summary")
async def get_project_summary(
    id: int,
    db: Session = Depends(get_db)
):
    job = await job_service.get_by_id(db, id)
    quotation = await quotation_service.get_by_id(db, job.quotation_id)
    customer = await customer_service.get_by_id(db, job.customer_id)
    payments = await payment_service.get_by_job_id(db, id)
    
    total_paid = sum(p.amount for p in payments if p.status == 'paid')
    total = float(quotation.final_price)
    
    return {
        "project": {
            "project_id": job.id,
            "job_id": job.id,
            "quotation_id": quotation.id,
            "quotation_number": quotation.quotation_number,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "address": customer.address
            },
            "status": job.status,
            "priority": job.priority,
            "financial": {
                "total": total,
                "paid": total_paid,
                "remaining": total - total_paid,
                "progress": (total_paid / total * 100) if total > 0 else 0,
                "overdue_amount": calculate_overdue(payments)
            },
            "dates": {
                "created": job.created_at,
                "expected_delivery": job.expected_delivery_date,
                "last_updated": job.updated_at
            },
            "stages": calculate_stages(job)
        }
    }
```

**Performance**: <500ms (single query with joins)

**Decision**: Implement only if header load time with separate requests >1 second

---

### Complete Workflow Stage

**Status**: Recommended for cleaner semantics

```http
POST /api/v1/jobs/{id}/complete-stage
```

**Purpose**: Complete a workflow stage with automatic activity logging

**Path Parameters**:
- `id` (integer, required): Job ID

**Request Body**:
```json
{
  "stage": "measurement",
  "completed_by": 1,
  "completion_date": "2026-07-25",
  "notes": "All rooms measured successfully"
}
```

**Response**: `200 OK`
```json
{
  "job": {
    "id": 123,
    "status": "in_production",
    "measurement_date": "2026-07-25",
    // ... other fields
    "updated_at": "2026-07-25T15:00:00Z"
  },
  "activity_log": {
    "id": 10,
    "job_id": 123,
    "user_id": 1,
    "action": "stage_completed_measurement",
    "description": "Measurement stage completed",
    "metadata": {
      "stage": "measurement",
      "duration_days": 3,
      "next_stage": "deposit"
    },
    "created_at": "2026-07-25T15:00:00Z"
  }
}
```

**Backend Implementation**:
```python
# app/api/v1/jobs.py
@router.post("/{id}/complete-stage")
async def complete_stage(
    id: int,
    stage_data: StageCompletionRequest,
    db: Session = Depends(get_db)
):
    job = await workflow_service.complete_stage(
        db=db,
        job_id=id,
        stage=stage_data.stage,
        completed_by=stage_data.completed_by,
        completion_date=stage_data.completion_date,
        notes=stage_data.notes
    )
    
    activity_log = await activity_service.create(
        db=db,
        job_id=id,
        user_id=stage_data.completed_by,
        action=f"stage_completed_{stage_data.stage}",
        description=f"{stage_data.stage.capitalize()} stage completed",
        metadata={
            "stage": stage_data.stage,
            "duration_days": calculate_duration(job, stage_data.stage),
            "next_stage": get_next_stage(stage_data.stage)
        }
    )
    
    return {
        "job": job,
        "activity_log": activity_log
    }
```

**Side Effects**:
- Updates job status to next stage
- Records completion date in appropriate field (measurement_date, production_end, etc.)
- Creates ActivityLog entry automatically
- Calculates stage duration

**Usage**: "Complete Stage" button in workflow section

**Decision**: Implement in Step 3 (Workflow) for cleaner API semantics

---

## API Response Standards

### Success Responses

**Single Resource**: `200 OK`
```json
{
  "id": 123,
  "field1": "value1",
  // ... resource fields
}
```

**Resource Created**: `201 Created`
```json
{
  "id": 456,
  "field1": "value1",
  // ... created resource
}
```

**Collection**: `200 OK`
```json
{
  "resources": [
    { "id": 1, /* ... */ },
    { "id": 2, /* ... */ }
  ],
  "total": 2
}
```

### Error Responses

**Not Found**: `404 Not Found`
```json
{
  "detail": "Job with ID 999 not found"
}
```

**Validation Error**: `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "value must be greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Bad Request**: `400 Bad Request`
```json
{
  "detail": "Cannot complete measurement stage: measurement_date is required"
}
```

**Unauthorized**: `401 Unauthorized`
```json
{
  "detail": "Not authenticated"
}
```

**Forbidden**: `403 Forbidden`
```json
{
  "detail": "Insufficient permissions to delete job"
}
```

---

## API Performance Targets

| Endpoint | Target Response Time | Notes |
|----------|---------------------|-------|
| GET /jobs | <1000ms | For 100 jobs |
| GET /jobs/{id} | <200ms | Single job |
| GET /quotations/{id} | <200ms | With items |
| GET /payments?job_id={id} | <200ms | All payments for job |
| GET /measurements?job_id={id} | <200ms | With items |
| GET /activity-logs?job_id={id} | <300ms | All events |
| POST /payments | <300ms | Create + log |
| PATCH /payments/{id}/status | <300ms | Update + log |
| POST /jobs/{id}/complete-stage | <500ms | Complex logic |

**Caching Strategy**:
- Frontend: React Query (5 min cache)
- Backend: No caching initially (future: Redis for read-heavy endpoints)

**Pagination**:
- Not initially required
- Implement if any collection >200 items

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Related**: design.md, architecture.md

