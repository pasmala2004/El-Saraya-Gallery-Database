# Quotation Status Workflow

## Status Lifecycle State Machine

```
┌─────────┐
│  DRAFT  │ (Initial state - editable)
└────┬────┘
     │
     │ requires ≥1 item
     ▼
┌──────────────────────────┐
│ WAITING_FOR_MEASUREMENT  │
└─────┬───────────┬────────┘
      │           │
      │           └──────────────┐
      ▼                          ▼
┌───────────┐              ┌────────────┐
│  MEASURED │              │ CANCELLED  │ ◄──────┐
└─────┬─────┘              └────────────┘        │
      │                      [TERMINAL]          │
      │                                          │
      ├──────────────┬────────────────┐          │
      │              │                │          │
      │ direct path  │                │          │
      │              ▼                ▼          │
      │      ┌──────────────┐   ┌──────────┐    │
      │      │ UNDER_       │   │   SENT   │    │
      │      │ NEGOTIATION  ├──→│          │    │
      │      └──────┬───────┘   └─────┬────┘    │
      │             │ requires ≥1     │          │
      │             │ item            │          │
      │             └─────────────────┤          │
      │                               │          │
      │                 ┌─────────────┘          │
      │                 │ back to               │
      │                 │ negotiation           │
      │                 ▼                       │
      │         ┌──────────────┐                │
      │         │ UNDER_       │                │
      │         │ NEGOTIATION  │                │
      │         └──────┬───────┘                │
      │                │                        │
      │                ├────────────────────────┤
      │                │                        │
      └────────────────┼────────────────────────┘
                       │
                       │ requires ≥1 item
                       ▼
                 ┌──────────┐
                 │   SENT   │
                 └─────┬────┘
                       │
         ┌─────────────┼────────────┬──────────────┐
         │             │            │              │
         ▼             ▼            ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
   │ APPROVED │  │ REJECTED │  │ CANCELLED│  │   EXPIRED  │
   └──────────┘  └──────────┘  └──────────┘  └────────────┘
   [TERMINAL]    [TERMINAL]    [TERMINAL]    [TERMINAL]
```

## State Descriptions

### 1. DRAFT
- **Description:** Initial state when quotation is created
- **Editable:** Yes - can modify discount, notes, date, add/remove items
- **Transitions to:**
  - `waiting_for_measurement` (requires ≥1 item)

### 2. WAITING_FOR_MEASUREMENT
- **Description:** Quotation sent to field team for site measurement
- **Editable:** No
- **Transitions to:**
  - `measured` (measurement completed)
  - `cancelled` (customer cancels before measurement)

### 3. MEASURED
- **Description:** Site measurement completed, ready for pricing/negotiation
- **Editable:** No
- **Transitions to:**
  - `under_negotiation` (start price negotiations)
  - `sent` (direct path - skip negotiation, requires ≥1 item)

### 4. UNDER_NEGOTIATION
- **Description:** Active price/terms negotiation with customer
- **Editable:** No
- **Transitions to:**
  - `sent` (send quotation to customer, requires ≥1 item)
  - `cancelled` (negotiations failed)

### 5. SENT
- **Description:** Official quotation sent to customer for approval
- **Editable:** No
- **Transitions to:**
  - `under_negotiation` (customer requests changes)
  - `approved` (customer accepts, requires ≥1 item)
  - `rejected` (customer declines)
  - `cancelled` (business cancels)

### 6. APPROVED (Terminal)
- **Description:** Customer approved quotation, ready for Job creation
- **Editable:** No
- **Transitions to:** None - terminal state
- **Next Step:** Create Job entity

### 7. REJECTED (Terminal)
- **Description:** Customer declined the quotation
- **Editable:** No
- **Transitions to:** None - terminal state

### 8. CANCELLED (Terminal)
- **Description:** Business cancelled the quotation
- **Editable:** No
- **Transitions to:** None - terminal state

### 9. EXPIRED (Terminal)
- **Description:** Quotation validity period expired
- **Editable:** No
- **Transitions to:** None - terminal state
- **Note:** Currently not auto-set; requires future implementation

## Business Rules

### Item Requirements
These transitions require at least one quotation item:
- `draft` → `waiting_for_measurement`
- `measured` → `sent`
- `under_negotiation` → `sent`
- `sent` → `approved`

### Editability Rules
- **Editable:** Only `draft` status
- **Locked:** All non-draft statuses
- **Terminal:** Cannot modify or change status from terminal states

### Cancellation Policy
Can cancel from:
- `waiting_for_measurement`
- `under_negotiation`
- `sent`

Cannot cancel from:
- `draft` (delete instead)
- `measured` (must transition first)
- Any terminal state

## Workflow Patterns

### Pattern 1: Simple Direct Flow
**Use Case:** Standard quotation without negotiation
```
draft → waiting_for_measurement → measured → sent → approved
```
**Time:** 3-7 days typical

### Pattern 2: Negotiation Loop
**Use Case:** Price negotiations required
```
draft → waiting_for_measurement → measured → 
under_negotiation ↔ sent → approved
```
**Time:** 1-4 weeks typical

### Pattern 3: Multiple Negotiation Rounds
**Use Case:** Complex negotiations with multiple iterations
```
draft → waiting_for_measurement → measured → 
under_negotiation → sent → 
under_negotiation → sent → 
under_negotiation → sent → approved
```
**Time:** 2-8 weeks typical

### Pattern 4: Early Cancellation
**Use Case:** Customer cancels before measurement
```
draft → waiting_for_measurement → cancelled
```

### Pattern 5: Rejection After Negotiation
**Use Case:** Customer declines after seeing final price
```
draft → waiting_for_measurement → measured → 
under_negotiation → sent → rejected
```

## API Usage Examples

### Create Draft Quotation
```http
POST /api/v1/quotations
Content-Type: application/json

{
  "customer_id": "11111111-1111-1111-1111-111111111111",
  "quotation_date": "2026-07-19",
  "discount": "0.00",
  "notes": "Standard aluminum windows"
}
```

### Add Items to Quotation
```http
POST /api/v1/quotations/{quotation_id}/items
Content-Type: application/json

{
  "product_id": "33333333-3333-3333-3333-333333333333",
  "quantity": 3,
  "unit_price": "2500.00",
  "description": "White aluminum frame\nDouble glazed glass",
  "notes": "Installation included"
}
```

### Progress Through Workflow
```http
# Step 1: Request measurement
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "waiting_for_measurement"
}

# Step 2: Mark measurement complete
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "measured"
}

# Step 3: Send to customer (direct path)
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "sent"
}

# Step 4: Approve
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "approved"
}
```

### Negotiation Flow
```http
# After measured status

# Step 1: Start negotiation
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "under_negotiation"
}

# Step 2: Send proposal
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "sent"
}

# Step 3: Customer requests changes - back to negotiation
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "under_negotiation"
}

# Step 4: Send revised proposal
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "sent"
}

# Step 5: Approve
PATCH /api/v1/quotations/{quotation_id}/status
Content-Type: application/json

{
  "status": "approved"
}
```

## Error Handling

### Common Error Responses

#### Invalid Transition
```json
{
  "error": "BusinessRuleViolation",
  "code": "invalid_quotation_status_transition",
  "message": "Invalid status transition: draft → sent"
}
```
**HTTP Status:** 422 Unprocessable Entity

#### Missing Items
```json
{
  "error": "BusinessRuleViolation",
  "code": "quotation_requires_items",
  "message": "Quotation must have at least one item before status waiting_for_measurement"
}
```
**HTTP Status:** 422 Unprocessable Entity

#### Not Editable
```json
{
  "error": "BusinessRuleViolation",
  "code": "quotation_not_editable",
  "message": "Quotation in status sent cannot be modified; only draft quotations are editable"
}
```
**HTTP Status:** 422 Unprocessable Entity

#### Terminal Status
```json
{
  "error": "BusinessRuleViolation",
  "code": "quotation_terminal",
  "message": "Quotation in terminal status approved cannot be modified"
}
```
**HTTP Status:** 422 Unprocessable Entity

## Implementation Notes

### Service Layer Validation
- `_ALLOWED_TRANSITIONS` - Defines valid state transitions
- `_TERMINAL_STATUSES` - Identifies terminal states
- `_REQUIRES_ITEMS` - Specifies statuses requiring items
- `_validate_transition()` - Enforces business rules

### Database Constraints
- Enum type: `quotation_status` (PostgreSQL)
- Column: `quotations.status` with NOT NULL constraint
- Default: `draft`
- Check constraints ensure data integrity

### Migration Safety
- Uses `ADD VALUE IF NOT EXISTS` for PostgreSQL enums
- Preserves existing data
- Intentionally irreversible (PostgreSQL enum limitation)

## Testing

See `tests/test_quotations.py` for comprehensive test coverage:
- Full lifecycle happy path
- Negotiation flow with multiple iterations
- Invalid transition attempts
- Terminal status enforcement
- Cancellation from multiple states
- Item requirement validation
- Direct path bypassing negotiation

**Test Coverage:** 16 tests, 100% pass rate

## Future Enhancements

### 1. Auto-Expiration
- Add `validity_date` field to quotation
- Background job to mark quotations as `expired`
- Configurable validity period (e.g., 30 days)

### 2. Status History
- Track all status transitions in `activity_log`
- Include timestamp, user, and reason
- Support audit trail requirements

### 3. Notifications
- Email to customer when status changes to `sent`
- Internal notification when quotation `approved`
- Reminder before quotation expires

### 4. Measurement Integration
- Link to Measurement entity
- Auto-transition to `measured` when measurement complete
- Attach measurement data to quotation

### 5. Job Creation
- Auto-create Job when status becomes `approved`
- Copy quotation items to job
- Link quotation to job entity

## References

- **Enum Definition:** `app/enums/quotation.py`
- **Model:** `app/models/quotation.py`
- **Service:** `app/services/quotation.py`
- **API:** `app/api/v1/quotations.py`
- **Migration:** `alembic/versions/c3f8a2d91e04_expand_quotation_status_enum.py`
- **Tests:** `tests/test_quotations.py`
