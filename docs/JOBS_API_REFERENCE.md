# Jobs API Reference

Quick reference for the Jobs module REST API.

---

## Base URL
```
/api/v1/jobs
```

---

## Endpoints

### 1. Create Job
Create a new job from an approved quotation.

```http
POST /api/v1/jobs
```

**Request Body:**
```json
{
  "quotation_id": "uuid",
  "notes": "Optional notes"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "quotation_id": "uuid",
  "status": "pending",
  "measurement_date": null,
  "production_start": null,
  "production_end": null,
  "installation_date": null,
  "delivery_date": null,
  "completion_date": null,
  "notes": "Optional notes",
  "created_at": "2026-07-20T13:00:00",
  "updated_at": "2026-07-20T13:00:00"
}
```

**Business Rules:**
- Quotation must exist (404 if not)
- Quotation must be APPROVED (422 if not)
- Only one job per quotation (409 if duplicate)
- Job starts in `pending` status
- Activity log created: `job_created`

---

### 2. List Jobs
List all jobs with optional filtering, sorting, and pagination.

```http
GET /api/v1/jobs
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by job status | `?status=pending` |
| `customer` | uuid | Filter by customer ID | `?customer=uuid` |
| `quotation` | uuid | Filter by quotation ID | `?quotation=uuid` |
| `created_after` | date | Jobs created after date | `?created_after=2026-01-01` |
| `created_before` | date | Jobs created before date | `?created_before=2026-12-31` |
| `limit` | integer | Page size (default 50) | `?limit=20` |
| `offset` | integer | Rows to skip (default 0) | `?offset=40` |
| `sort_by` | string | Sort field | `?sort_by=created_at` |
| `sort_order` | string | `asc` or `desc` | `?sort_order=desc` |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "quotation_id": "uuid",
      "status": "pending",
      "measurement_date": null,
      "production_start": null,
      "production_end": null,
      "installation_date": null,
      "delivery_date": null,
      "completion_date": null,
      "notes": "Notes",
      "created_at": "2026-07-20T13:00:00",
      "updated_at": "2026-07-20T13:00:00"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### 3. Get Job by ID
Retrieve a single job by its ID.

```http
GET /api/v1/jobs/{job_id}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "quotation_id": "uuid",
  "status": "in_production",
  "measurement_date": "2026-07-15",
  "production_start": "2026-07-18",
  "production_end": null,
  "installation_date": "2026-08-01",
  "delivery_date": null,
  "completion_date": null,
  "notes": "Customer wants dark wood finish",
  "created_at": "2026-07-20T13:00:00",
  "updated_at": "2026-07-20T14:30:00"
}
```

**Errors:**
- `404` - Job not found

---

### 4. Update Job
Update job dates and notes. Cannot update status (use PATCH /status) or quotation_id.

```http
PUT /api/v1/jobs/{job_id}
```

**Request Body:**
```json
{
  "measurement_date": "2026-07-15",
  "production_start": "2026-07-18",
  "production_end": "2026-07-25",
  "installation_date": "2026-08-01",
  "delivery_date": "2026-07-30",
  "notes": "Updated notes"
}
```

All fields are optional. Only include fields you want to update.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "quotation_id": "uuid",
  "status": "in_production",
  "measurement_date": "2026-07-15",
  "production_start": "2026-07-18",
  "production_end": "2026-07-25",
  "installation_date": "2026-08-01",
  "delivery_date": "2026-07-30",
  "completion_date": null,
  "notes": "Updated notes",
  "created_at": "2026-07-20T13:00:00",
  "updated_at": "2026-07-20T15:00:00"
}
```

**Business Rules:**
- Terminal jobs (`completed`, `cancelled`) cannot be edited (422)
- Setting `production_start` creates activity log: `production_started`
- Setting `installation_date` creates activity log: `installation_scheduled`

**Errors:**
- `404` - Job not found
- `422` - Terminal job cannot be edited

---

### 5. Update Job Status
Change job status following workflow rules.

```http
PATCH /api/v1/jobs/{job_id}/status
```

**Request Body:**
```json
{
  "status": "measuring"
}
```

**Valid Status Values:**
- `pending`
- `measuring`
- `in_production`
- `ready_for_installation`
- `installed`
- `completed`
- `cancelled`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "quotation_id": "uuid",
  "status": "measuring",
  "measurement_date": null,
  "production_start": null,
  "production_end": null,
  "installation_date": null,
  "delivery_date": null,
  "completion_date": null,
  "notes": "Notes",
  "created_at": "2026-07-20T13:00:00",
  "updated_at": "2026-07-20T15:30:00"
}
```

**Status Workflow:**
```
pending → measuring → in_production → ready_for_installation → installed → completed
   ↓          ↓              ↓                    ↓                 ↓
cancelled  cancelled      cancelled            cancelled         cancelled
```

**Business Rules:**
- Only valid transitions allowed (422 if invalid)
- Terminal states (`completed`, `cancelled`) cannot be changed (422)
- Status → `in_production`: auto-sets `production_start` to today
- Status → `completed`: auto-sets `completion_date` to today
- Activity log created: `status_changed`
- Status → `completed`: additional activity log `job_completed`

**Errors:**
- `404` - Job not found
- `422` - Invalid transition or terminal status

---

### 6. Get Job by Quotation
Retrieve the job associated with a specific quotation.

```http
GET /api/v1/quotations/{quotation_id}/job
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "quotation_id": "uuid",
  "status": "pending",
  "measurement_date": null,
  "production_start": null,
  "production_end": null,
  "installation_date": null,
  "delivery_date": null,
  "completion_date": null,
  "notes": "Notes",
  "created_at": "2026-07-20T13:00:00",
  "updated_at": "2026-07-20T13:00:00"
}
```

**Response if no job exists:** `200 OK`
```json
null
```

**Errors:**
- None (returns null if no job)

---

### 7. List Customer Jobs
List all jobs for a specific customer.

```http
GET /api/v1/customers/{customer_id}/jobs
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Page size (default 50) |
| `offset` | integer | Rows to skip (default 0) |
| `sort_by` | string | Sort field |
| `sort_order` | string | `asc` or `desc` |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "quotation_id": "uuid",
      "status": "completed",
      "measurement_date": "2026-06-01",
      "production_start": "2026-06-05",
      "production_end": "2026-06-15",
      "installation_date": "2026-06-20",
      "delivery_date": "2026-06-20",
      "completion_date": "2026-06-21",
      "notes": "Finished successfully",
      "created_at": "2026-06-01T10:00:00",
      "updated_at": "2026-06-21T16:00:00"
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0
}
```

**Errors:**
- `404` - Customer not found

---

## Job Status Enum

| Status | Description |
|--------|-------------|
| `pending` | Job created, awaiting measurement |
| `measuring` | On-site measurement in progress |
| `in_production` | Manufacturing the product |
| `ready_for_installation` | Product ready, awaiting installation |
| `installed` | Product installed at customer site |
| `completed` | Job finished (terminal) |
| `cancelled` | Job cancelled (terminal) |

---

## Activity Log Actions

All activity logs are created automatically:

| Action | When | Description |
|--------|------|-------------|
| `job_created` | Job created | "Job created for quotation Q-2026-XXX" |
| `status_changed` | Status updated | "Status changed from pending to measuring" |
| `production_started` | production_start set | "Production started on 2026-07-18" |
| `installation_scheduled` | installation_date set | "Installation scheduled for 2026-08-01" |
| `job_completed` | Status → completed | "Job marked as completed" |

---

## Error Responses

All endpoints follow the standard error format:

```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `404` - Not Found (Job, Quotation, Customer)
- `409` - Conflict (Duplicate job for quotation)
- `422` - Unprocessable Entity (Business rule violation, invalid transition)
- `500` - Internal Server Error

---

## Example Workflows

### Complete Job Lifecycle
```bash
# 1. Create job from approved quotation
POST /api/v1/jobs
{"quotation_id": "uuid"}

# 2. Schedule measurement
PATCH /api/v1/jobs/{id}/status
{"status": "measuring"}

# 3. Record measurement date
PUT /api/v1/jobs/{id}
{"measurement_date": "2026-07-15"}

# 4. Move to production
PATCH /api/v1/jobs/{id}/status
{"status": "in_production"}
# → production_start auto-set to today

# 5. Production complete
PATCH /api/v1/jobs/{id}/status
{"status": "ready_for_installation"}

# 6. Schedule installation
PUT /api/v1/jobs/{id}
{"installation_date": "2026-08-01"}

# 7. Install at customer site
PATCH /api/v1/jobs/{id}/status
{"status": "installed"}

# 8. Complete job
PATCH /api/v1/jobs/{id}/status
{"status": "completed"}
# → completion_date auto-set to today
```

### Cancel Job
```bash
# Cancel from any non-terminal status
PATCH /api/v1/jobs/{id}/status
{"status": "cancelled"}
```

### Find Customer's Jobs
```bash
# Get all jobs for a customer
GET /api/v1/customers/{customer_id}/jobs?sort_by=created_at&sort_order=desc
```

### Filter Active Jobs
```bash
# Get all jobs not yet completed
GET /api/v1/jobs?status=pending
GET /api/v1/jobs?status=measuring
GET /api/v1/jobs?status=in_production
```

---

## Testing

Run all job tests:
```bash
python -m pytest tests/test_jobs.py -v
```

16 tests cover:
- Job creation (business rules, validation)
- Job retrieval (by ID, by quotation, by customer)
- Job updates (dates, notes, terminal protection)
- Status workflow (transitions, terminal protection, cancellation)
- Filtering and pagination
- Error handling (404, 409, 422)
