# Measurements API Reference

Quick reference for the Measurements module REST API.

---

## Base URLs
```
/api/v1/jobs/{job_id}/measurements
/api/v1/measurements
/api/v1/measurement-items
```

---

## Measurement Endpoints

### 1. List Job Measurements
List all measurements for a specific job.

```http
GET /api/v1/jobs/{job_id}/measurements
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Page size (1-100) |
| `offset` | integer | 0 | Rows to skip |
| `sort_by` | string | measurement_number | Field to sort by |
| `sort_order` | string | desc | `asc` or `desc` |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "measurement_number": 2,
      "visit_date": "2026-07-26",
      "measured_by": "Ahmed Hassan",
      "notes": "Second visit - adjustments needed",
      "created_at": "2026-07-26T10:00:00",
      "updated_at": "2026-07-26T10:00:00"
    },
    {
      "id": "uuid",
      "job_id": "uuid",
      "measurement_number": 1,
      "visit_date": "2026-07-20",
      "measured_by": "Ahmed Hassan",
      "notes": "First visit",
      "created_at": "2026-07-20T14:00:00",
      "updated_at": "2026-07-20T14:00:00"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Errors:**
- `404` - Job not found

---

### 2. Create Measurement
Create a new measurement for a job.

```http
POST /api/v1/jobs/{job_id}/measurements
```

**Request Body:**
```json
{
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "First measurement visit - kitchen area"
}
```

All fields are optional.

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "measurement_number": 1,
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "First measurement visit - kitchen area",
  "created_at": "2026-07-25T10:00:00",
  "updated_at": "2026-07-25T10:00:00"
}
```

**Business Rules:**
- Job must exist (404 if not)
- measurement_number auto-increments from 1
- Unlimited measurement visits allowed per job
- Activity log created: `measurement_created`

**Errors:**
- `404` - Job not found

---

### 3. Get Measurement by ID
Retrieve a single measurement.

```http
GET /api/v1/measurements/{measurement_id}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "measurement_number": 1,
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "First visit",
  "created_at": "2026-07-25T10:00:00",
  "updated_at": "2026-07-25T10:00:00"
}
```

**Errors:**
- `404` - Measurement not found

---

### 4. Update Measurement
Update measurement details.

```http
PUT /api/v1/measurements/{measurement_id}
```

**Request Body:**
```json
{
  "visit_date": "2026-07-26",
  "measured_by": "Updated Person",
  "notes": "Updated notes"
}
```

All fields are optional. Only include fields you want to update.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "measurement_number": 1,
  "visit_date": "2026-07-26",
  "measured_by": "Updated Person",
  "notes": "Updated notes",
  "created_at": "2026-07-25T10:00:00",
  "updated_at": "2026-07-26T11:00:00"
}
```

**Business Rules:**
- Cannot change job_id or measurement_number (immutable)
- Activity log created: `measurement_updated`

**Errors:**
- `404` - Measurement not found

---

## Measurement Item Endpoints

### 5. List Measurement Items
List all items for a measurement.

```http
GET /api/v1/measurements/{measurement_id}/items
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "measurement_id": "uuid",
    "quotation_item_id": "uuid",
    "room_name": "Kitchen",
    "piece_number": "K-001",
    "width": "250.50",
    "height": "180.75",
    "quantity": 2,
    "notes": "Corner cabinet",
    "created_at": "2026-07-25T11:00:00",
    "updated_at": "2026-07-25T11:00:00"
  },
  {
    "id": "uuid",
    "measurement_id": "uuid",
    "quotation_item_id": "uuid",
    "room_name": "Living Room",
    "piece_number": "L-001",
    "width": "300.00",
    "height": "200.00",
    "quantity": 1,
    "notes": "Wall unit",
    "created_at": "2026-07-25T11:30:00",
    "updated_at": "2026-07-25T11:30:00"
  }
]
```

**Errors:**
- `404` - Measurement not found

---

### 6. Add Measurement Item
Add an item to a measurement.

```http
POST /api/v1/measurements/{measurement_id}/items
```

**Request Body:**
```json
{
  "quotation_item_id": "uuid",
  "room_name": "Kitchen",
  "piece_number": "K-001",
  "width": "250.50",
  "height": "180.75",
  "quantity": 2,
  "notes": "Corner cabinet"
}
```

**Required Fields:**
- `quotation_item_id` (UUID)
- `quantity` (integer > 0)

**Optional Fields:**
- `room_name` (string, max 100 chars)
- `piece_number` (string, max 100 chars)
- `width` (decimal >= 0)
- `height` (decimal >= 0)
- `notes` (text, max 5000 chars)

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "measurement_id": "uuid",
  "quotation_item_id": "uuid",
  "room_name": "Kitchen",
  "piece_number": "K-001",
  "width": "250.50",
  "height": "180.75",
  "quantity": 2,
  "notes": "Corner cabinet",
  "created_at": "2026-07-25T11:00:00",
  "updated_at": "2026-07-25T11:00:00"
}
```

**Business Rules:**
- Measurement must exist (404 if not)
- QuotationItem must exist (404 if not)
- **QuotationItem must belong to same quotation as Job** (422 if not)
- width >= 0 (422 if negative)
- height >= 0 (422 if negative)
- quantity > 0 (422 if zero or negative)
- Activity log created: `measurement_item_added`

**Errors:**
- `404` - Measurement or QuotationItem not found
- `422` - Validation error or business rule violation

---

### 7. Update Measurement Item
Update a measurement item.

```http
PUT /api/v1/measurement-items/{item_id}
```

**Request Body:**
```json
{
  "room_name": "Updated Kitchen",
  "piece_number": "K-001A",
  "width": "260.00",
  "height": "185.50",
  "quantity": 3,
  "notes": "Adjusted measurements after site review"
}
```

All fields are optional. Only include fields you want to update.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "measurement_id": "uuid",
  "quotation_item_id": "uuid",
  "room_name": "Updated Kitchen",
  "piece_number": "K-001A",
  "width": "260.00",
  "height": "185.50",
  "quantity": 3,
  "notes": "Adjusted measurements after site review",
  "created_at": "2026-07-25T11:00:00",
  "updated_at": "2026-07-25T15:00:00"
}
```

**Business Rules:**
- Item must exist (404 if not)
- If changing quotation_item_id, must belong to same quotation as Job (422 if not)
- width >= 0 (422 if negative)
- height >= 0 (422 if negative)
- quantity > 0 (422 if zero or negative)
- Activity log created: `measurement_item_edited`

**Errors:**
- `404` - Item not found
- `422` - Validation error or business rule violation

---

## Data Types

### Measurement Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Read-only | Measurement ID |
| `job_id` | UUID | Required | Job reference (immutable) |
| `measurement_number` | integer | Auto | Auto-increments from 1 per job |
| `visit_date` | date (YYYY-MM-DD) | Optional | Measurement visit date |
| `measured_by` | string (max 255) | Optional | Person who took measurements |
| `notes` | text (max 5000) | Optional | Measurement notes |
| `created_at` | datetime | Auto | Creation timestamp |
| `updated_at` | datetime | Auto | Last update timestamp |

### Measurement Item Fields
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | UUID | Read-only | Item ID |
| `measurement_id` | UUID | Required | Measurement reference |
| `quotation_item_id` | UUID | Required | QuotationItem reference |
| `room_name` | string (max 100) | Optional | Room name/location |
| `piece_number` | string (max 100) | Optional | Piece identifier |
| `width` | decimal (10,2) | Optional | Width >= 0 |
| `height` | decimal (10,2) | Optional | Height >= 0 |
| `quantity` | integer | Required | Quantity > 0 |
| `notes` | text (max 5000) | Optional | Item notes |
| `created_at` | datetime | Auto | Creation timestamp |
| `updated_at` | datetime | Auto | Last update timestamp |

---

## Activity Log Actions

All activity logs are created automatically:

| Action | When | Description |
|--------|------|-------------|
| `measurement_created` | Measurement created | "Measurement #{number} created" |
| `measurement_updated` | Measurement updated | "Measurement #{number} updated" |
| `measurement_item_added` | Item added | "Item added to measurement #{number}" |
| `measurement_item_edited` | Item updated | "Item in measurement #{number} edited" |

---

## Error Responses

All endpoints follow the standard error format:

```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `404` - Not Found (Job, Measurement, QuotationItem, Item)
- `422` - Unprocessable Entity (Business rule violation, validation error)
- `500` - Internal Server Error

---

## Example Workflows

### Complete Measurement Workflow
```bash
# 1. Create first measurement for a job
POST /api/v1/jobs/{job_id}/measurements
{
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "Initial site visit"
}
# → Returns measurement with measurement_number: 1

# 2. Add items to the measurement
POST /api/v1/measurements/{measurement_id}/items
{
  "quotation_item_id": "{quotation_item_uuid}",
  "room_name": "Kitchen",
  "piece_number": "K-001",
  "width": "250.50",
  "height": "180.75",
  "quantity": 2
}

POST /api/v1/measurements/{measurement_id}/items
{
  "quotation_item_id": "{another_quotation_item_uuid}",
  "room_name": "Living Room",
  "width": "300.00",
  "height": "200.00",
  "quantity": 1
}

# 3. Update an item if adjustments needed
PUT /api/v1/measurement-items/{item_id}
{
  "width": "255.00",
  "notes": "Adjusted after consultation"
}

# 4. Create second measurement if re-measurement needed
POST /api/v1/jobs/{job_id}/measurements
{
  "visit_date": "2026-07-30",
  "measured_by": "Ahmed Hassan",
  "notes": "Re-measurement after design changes"
}
# → Returns measurement with measurement_number: 2
```

### List All Measurements for a Job
```bash
GET /api/v1/jobs/{job_id}/measurements?sort_by=measurement_number&sort_order=desc
```

### Get Measurement with All Items
```bash
# Get measurement details
GET /api/v1/measurements/{measurement_id}

# Get all items
GET /api/v1/measurements/{measurement_id}/items
```

---

## Validation Examples

### ✅ Valid Requests
```json
// Minimal measurement
{
  "visit_date": "2026-07-25"
}

// Complete measurement
{
  "visit_date": "2026-07-25",
  "measured_by": "Ahmed Hassan",
  "notes": "Detailed notes here"
}

// Minimal item (required fields only)
{
  "quotation_item_id": "uuid",
  "quantity": 1
}

// Complete item
{
  "quotation_item_id": "uuid",
  "room_name": "Kitchen",
  "piece_number": "K-001",
  "width": "250.50",
  "height": "180.75",
  "quantity": 2,
  "notes": "Corner cabinet"
}

// Dimensions can be zero
{
  "quotation_item_id": "uuid",
  "width": "0.00",
  "height": "0.00",
  "quantity": 1
}
```

### ❌ Invalid Requests
```json
// Negative width
{
  "quotation_item_id": "uuid",
  "width": "-10.00",  // ❌ Error: width must be >= 0
  "quantity": 1
}

// Negative height
{
  "quotation_item_id": "uuid",
  "height": "-5.00",  // ❌ Error: height must be >= 0
  "quantity": 1
}

// Zero quantity
{
  "quotation_item_id": "uuid",
  "quantity": 0  // ❌ Error: quantity must be > 0
}

// Negative quantity
{
  "quotation_item_id": "uuid",
  "quantity": -1  // ❌ Error: quantity must be > 0
}

// Missing quotation_item_id
{
  "quantity": 1  // ❌ Error: quotation_item_id is required
}
```

---

## Testing

Run all measurement tests:
```bash
python -m pytest tests/test_measurements.py -v
```

18 tests cover:
- Measurement creation (auto-increment, job validation)
- Measurement retrieval (by ID, list by job)
- Measurement updates
- Item creation (quotation validation, dimension validation)
- Item updates
- Cross-job quotation item validation
- Negative dimension rejection
- Zero/negative quantity rejection
- Error handling (404, 422)
