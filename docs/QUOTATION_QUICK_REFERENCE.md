# Quotation Status - Quick Reference

## Status Values Overview

| Status | Type | Editable | Can Cancel | Next Steps |
|--------|------|----------|------------|------------|
| `draft` | Initial | ✅ Yes | ❌ (delete) | → waiting_for_measurement |
| `waiting_for_measurement` | Active | ❌ No | ✅ Yes | → measured, cancelled |
| `measured` | Active | ❌ No | ❌ No | → under_negotiation, sent |
| `under_negotiation` | Active | ❌ No | ✅ Yes | → sent, cancelled |
| `sent` | Active | ❌ No | ✅ Yes | → under_negotiation, approved, rejected, cancelled |
| `approved` | Terminal | ❌ No | ❌ No | Create Job |
| `rejected` | Terminal | ❌ No | ❌ No | - |
| `cancelled` | Terminal | ❌ No | ❌ No | - |
| `expired` | Terminal | ❌ No | ❌ No | - |

## Valid Transitions Matrix

| From \ To | draft | waiting | measured | negotiation | sent | approved | rejected | cancelled | expired |
|-----------|-------|---------|----------|-------------|------|----------|----------|-----------|---------|
| **draft** | - | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **waiting_for_measurement** | ❌ | - | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **measured** | ❌ | ❌ | - | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **under_negotiation** | ❌ | ❌ | ❌ | - | ✅ | ❌ | ❌ | ✅ | ❌ |
| **sent** | ❌ | ❌ | ❌ | ✅ | - | ✅ | ✅ | ✅ | ❌ |
| **approved** | ❌ | ❌ | ❌ | ❌ | ❌ | - | ❌ | ❌ | ❌ |
| **rejected** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | - | ❌ | ❌ |
| **cancelled** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | - | ❌ |
| **expired** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | - |

✅ = Valid transition | ❌ = Invalid transition | - = Same status (no-op)

## Item Requirements

| Transition | Requires Items |
|------------|----------------|
| draft → waiting_for_measurement | ✅ Required |
| waiting_for_measurement → measured | ❌ Not required |
| measured → under_negotiation | ❌ Not required |
| measured → sent | ✅ Required |
| under_negotiation → sent | ✅ Required |
| sent → under_negotiation | ❌ Not required |
| sent → approved | ✅ Required |
| sent → rejected | ❌ Not required |
| Any → cancelled | ❌ Not required |

## Common Workflows

### 1. Standard Flow (No Negotiation)
```
1. Create quotation (draft)
2. Add items
3. Request measurement (waiting_for_measurement)
4. Complete measurement (measured)
5. Send to customer (sent)
6. Customer approves (approved)
7. Create job
```

### 2. With Negotiation
```
1. Create quotation (draft)
2. Add items
3. Request measurement (waiting_for_measurement)
4. Complete measurement (measured)
5. Start negotiation (under_negotiation)
6. Send proposal (sent)
7. Customer wants changes (under_negotiation)
8. Send revised (sent)
9. Customer approves (approved)
10. Create job
```

### 3. Quick Cancellation
```
1. Create quotation (draft)
2. Add items
3. Request measurement (waiting_for_measurement)
4. Customer cancels (cancelled)
```

## API Endpoint

### Status Update
```http
PATCH /api/v1/quotations/{quotation_id}/status
```

**Request Body:**
```json
{
  "status": "waiting_for_measurement"
}
```

**Success Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "waiting_for_measurement",
  "quotation_number": "Q-2026-ABC123",
  ...
}
```

**Error Responses:**

| Status Code | Error Code | Reason |
|-------------|------------|--------|
| 404 | EntityNotFoundError | Quotation not found |
| 422 | invalid_quotation_status_transition | Invalid state transition |
| 422 | quotation_requires_items | Missing required items |
| 422 | quotation_not_editable | Attempt to edit non-draft |
| 422 | quotation_terminal | Attempt to modify terminal status |

## Code Examples

### Python Service Call
```python
from app.services.quotation import QuotationService

# Update status
quotation = await quotation_service.update_status(
    quotation_id=quotation_id,
    new_status=QuotationStatus.WAITING_FOR_MEASUREMENT
)
```

### Error Handling
```python
from app.core.exceptions import BusinessRuleViolation

try:
    await quotation_service.update_status(
        quotation_id=quotation_id,
        new_status=QuotationStatus.SENT
    )
except BusinessRuleViolation as e:
    if e.code == "invalid_quotation_status_transition":
        # Handle invalid transition
        pass
    elif e.code == "quotation_requires_items":
        # Handle missing items
        pass
```

### TypeScript/JavaScript Client
```typescript
// Update status
async function updateQuotationStatus(
  quotationId: string,
  status: string
): Promise<Quotation> {
  const response = await fetch(
    `/api/v1/quotations/${quotationId}/status`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  return response.json();
}

// Usage
try {
  const quotation = await updateQuotationStatus(
    id,
    'waiting_for_measurement'
  );
  console.log('Status updated:', quotation.status);
} catch (error) {
  console.error('Failed to update status:', error.message);
}
```

## Business Logic Constants

### Service Layer (`app/services/quotation.py`)

```python
# Terminal statuses - no further transitions allowed
_TERMINAL_STATUSES: frozenset[QuotationStatus] = frozenset({
    QuotationStatus.APPROVED,
    QuotationStatus.REJECTED,
    QuotationStatus.CANCELLED,
    QuotationStatus.EXPIRED,
})

# Transitions that require at least one line item
_REQUIRES_ITEMS: frozenset[QuotationStatus] = frozenset({
    QuotationStatus.WAITING_FOR_MEASUREMENT,
    QuotationStatus.SENT,
    QuotationStatus.APPROVED,
})

# Allowed transitions mapping
_ALLOWED_TRANSITIONS: dict[QuotationStatus, frozenset[QuotationStatus]] = {
    QuotationStatus.DRAFT: 
        frozenset({QuotationStatus.WAITING_FOR_MEASUREMENT}),
    QuotationStatus.WAITING_FOR_MEASUREMENT: 
        frozenset({QuotationStatus.MEASURED, QuotationStatus.CANCELLED}),
    QuotationStatus.MEASURED: 
        frozenset({QuotationStatus.UNDER_NEGOTIATION, QuotationStatus.SENT}),
    QuotationStatus.UNDER_NEGOTIATION: 
        frozenset({QuotationStatus.SENT, QuotationStatus.CANCELLED}),
    QuotationStatus.SENT: 
        frozenset({
            QuotationStatus.UNDER_NEGOTIATION,
            QuotationStatus.APPROVED,
            QuotationStatus.REJECTED,
            QuotationStatus.CANCELLED,
        }),
    QuotationStatus.APPROVED: frozenset(),
    QuotationStatus.REJECTED: frozenset(),
    QuotationStatus.CANCELLED: frozenset(),
    QuotationStatus.EXPIRED: frozenset(),
}
```

## Database Schema

### Enum Type
```sql
CREATE TYPE quotation_status AS ENUM (
    'draft',
    'waiting_for_measurement',
    'measured',
    'under_negotiation',
    'sent',
    'approved',
    'rejected',
    'cancelled',
    'expired'
);
```

### Table Column
```sql
ALTER TABLE quotations
ADD COLUMN status quotation_status NOT NULL DEFAULT 'draft';

CREATE INDEX ix_quotations_status ON quotations(status);
```

## Testing Checklist

When testing quotation workflows, verify:

- [ ] Can create quotation in draft status
- [ ] Cannot transition without required items
- [ ] All valid transitions work correctly
- [ ] All invalid transitions are rejected with proper error codes
- [ ] Terminal statuses cannot be changed
- [ ] Only draft quotations can be edited
- [ ] Cancellation works from allowed statuses
- [ ] Negotiation loop (under_negotiation ↔ sent) works
- [ ] Direct path (measured → sent) works
- [ ] Status persists correctly in database
- [ ] API returns correct error messages
- [ ] Filtering by status works

## Migration Information

**Migration File:** `alembic/versions/c3f8a2d91e04_expand_quotation_status_enum.py`

**Added Values:**
- `waiting_for_measurement`
- `measured`
- `under_negotiation`
- `expired`

**Existing Values Preserved:**
- `draft`
- `sent`
- `approved`
- `rejected`
- `cancelled`

**Safety:** Uses `ADD VALUE IF NOT EXISTS` to avoid conflicts

**Downgrade:** Intentionally not supported (PostgreSQL enum limitation)

## Troubleshooting

### Problem: "Invalid status transition" error
**Solution:** Check the valid transitions matrix above. Ensure you're following the correct workflow path.

### Problem: "Quotation requires items" error
**Solution:** Add at least one quotation item before transitioning to waiting_for_measurement, sent, or approved.

### Problem: "Quotation not editable" error
**Solution:** Only draft quotations can be edited. Use status transitions for workflow progression.

### Problem: Cannot change status from approved/rejected/cancelled
**Solution:** These are terminal statuses. Create a new quotation if needed.

### Problem: Want to skip waiting_for_measurement
**Solution:** Not possible. Every quotation must progress through measurement workflow.

### Problem: Want to go directly from draft to sent
**Solution:** Must follow the workflow: draft → waiting_for_measurement → measured → sent

## Related Documentation

- **Full Workflow Guide:** [QUOTATION_WORKFLOW.md](./QUOTATION_WORKFLOW.md)
- **Implementation Summary:** [QUOTATION_STATUS_UPDATE_SUMMARY.md](../QUOTATION_STATUS_UPDATE_SUMMARY.md)
- **API Documentation:** OpenAPI schema at `/docs`
- **Tests:** `tests/test_quotations.py`

## Support

For questions or issues:
1. Check this quick reference first
2. Review the full workflow documentation
3. Examine test cases for examples
4. Check API error messages for specific guidance
