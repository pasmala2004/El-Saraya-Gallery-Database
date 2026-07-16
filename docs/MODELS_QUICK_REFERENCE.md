# Models Quick Reference

Quick lookup for field names, enums, and relationships when writing business logic.

---

## Enums

### QuotationStatus
```python
from app.enums.quotation import QuotationStatus

DRAFT, SENT, APPROVED, REJECTED, CANCELLED
```

### JobStatus
```python
from app.enums.job import JobStatus

PENDING, MEASURING, IN_PRODUCTION, READY_FOR_INSTALLATION, INSTALLED, COMPLETED, CANCELLED
```

### PaymentType (Business Milestone)
```python
from app.enums.payment import PaymentType

DEPOSIT, PRODUCTION, FINAL
```

### PaymentMethod (Payment Channel)
```python
from app.enums.payment import PaymentMethod

CASH, BANK_TRANSFER, INSTAPAY, CHEQUE, OTHER
```

### PaymentStatus
```python
from app.enums.payment import PaymentStatus

PENDING, PAID, OVERDUE, CANCELLED
```

---

## Common Field Names

### UUID Fields
- All models: `id` (PK, auto-generated)
- Foreign keys: `{parent}_id` (e.g., `customer_id`, `job_id`, `quotation_id`)

### Audit Fields (on all models via BaseEntity)
- `created_at` — DateTime(tz), auto-set on insert
- `updated_at` — DateTime(tz), auto-updated on change

### Status Fields
- `Customer` — no status (always active)
- `Quotation` — `status: QuotationStatus`
- `Job` — `status: JobStatus`
- `Payment` — `status: PaymentStatus`
- `Product` — `active: bool`

### Name/Title Fields
- `Customer.full_name` — String(255)
- `Product.name` — String(255)
- `ProductCategory.name` — String(100), unique
- `Quotation.quotation_number` — String(50), unique

### Money Fields
All use `Numeric(12, 2)` (up to 9,999,999,999.99):
- `Quotation.total_price`, `discount`, `final_price`
- `QuotationItem.unit_price`, `total_price`
- `Payment.amount`
- `Payment.percentage` — Numeric(5, 2) for 0.00 to 100.00

### Dimension Fields
- `MeasurementItem.width` — Numeric(10, 2)
- `MeasurementItem.height` — Numeric(10, 2)

### Date Fields
- `Quotation.quotation_date` — Date
- `Job.measurement_date`, `production_start`, `production_end`, `installation_date`, `delivery_date`, `completion_date` — Date
- `Measurement.visit_date` — Date
- `Payment.due_date`, `paid_date` — Date
- `Report.report_date` — Date

### Sequence/Order Fields
- `Measurement.measurement_number` — SmallInteger (1, 2, 3...)
- `Payment.payment_order` — SmallInteger (1, 2, 3...)

### Notes/Description Fields
All use `Text` (unlimited):
- Almost every model has a `notes` field
- `QuotationItem.description` — String(500) for short desc
- `ActivityLog.description` — Text

### New Business Fields
- `Customer.location_url` — String(500), Google Maps link
- `Measurement.measured_by` — String(255), employee name
- `MeasurementItem.piece_number` — String(100), e.g., "Window 1"
- `MeasurementItem.room_name` — String(100), e.g., "Living Room"
- `Payment.payment_method` — PaymentMethod enum
- `ActivityLog.action` — String(100), event type

---

## Relationships

### Customer
```python
customer.quotations  # → list[Quotation]
```

### ProductCategory
```python
category.products  # → list[Product]
```

### Product
```python
product.category  # → ProductCategory
product.quotation_items  # → list[QuotationItem]
```

### Quotation
```python
quotation.customer  # → Customer
quotation.items  # → list[QuotationItem]
quotation.job  # → Job | None (1:1)
```

### QuotationItem
```python
item.quotation  # → Quotation
item.product  # → Product
item.measurement_items  # → list[MeasurementItem]
```

### Job
```python
job.quotation  # → Quotation
job.measurements  # → list[Measurement]
job.payments  # → list[Payment]
job.activity_logs  # → list[ActivityLog]
```

### Measurement
```python
measurement.job  # → Job
measurement.items  # → list[MeasurementItem]
```

### MeasurementItem
```python
mitem.measurement  # → Measurement
mitem.quotation_item  # → QuotationItem
```

### Payment
```python
payment.job  # → Job
```

### ActivityLog
```python
log.job  # → Job
```

### Report
No relationships (standalone)

---

## Common Queries

### Get Customer with all Quotations
```python
customer = await session.get(Customer, customer_id)
# customer.quotations already loaded (lazy="selectin")
```

### Get Quotation with Items and Job
```python
quotation = await session.get(Quotation, quotation_id)
# quotation.customer already loaded (lazy="joined")
# quotation.items already loaded (lazy="selectin")
# quotation.job loaded on access (lazy="select")
```

### Get Job with full tree
```python
job = await session.get(Job, job_id)
# job.quotation loaded (lazy="joined")
# job.measurements loaded (lazy="selectin")
# job.payments loaded (lazy="selectin")
# job.activity_logs loaded on access (lazy="select")
```

### Filter by Status
```python
from sqlalchemy import select
from app.models import Quotation
from app.enums.quotation import QuotationStatus

stmt = select(Quotation).where(Quotation.status == QuotationStatus.APPROVED)
quotations = await session.execute(stmt)
```

### Get Payment breakdown for Job
```python
job = await session.get(Job, job_id)
deposit = [p for p in job.payments if p.payment_type == PaymentType.DEPOSIT]
production = [p for p in job.payments if p.payment_type == PaymentType.PRODUCTION]
final = [p for p in job.payments if p.payment_type == PaymentType.FINAL]
```

---

## Import Paths

```python
# Models
from app.models import (
    ActivityLog,
    Customer,
    Job,
    Measurement,
    MeasurementItem,
    Payment,
    Product,
    ProductCategory,
    Quotation,
    QuotationItem,
    Report,
)

# Enums
from app.enums.job import JobStatus
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType
from app.enums.quotation import QuotationStatus

# Database
from app.db.base import Base, BaseEntity
from app.db.session import AsyncSessionLocal, engine, get_db
```

---

## Cascade Behavior

### Delete Customer
→ Cascades to all Quotations
  → Cascades to all QuotationItems
  → Cascades to all Jobs
    → Cascades to all Measurements, Payments, ActivityLogs

### Delete Product
❌ **Blocked** if referenced by any QuotationItem (`ondelete="RESTRICT"`)

### Delete ProductCategory
❌ **Blocked** if any Products exist (`ondelete="RESTRICT"`)

### Delete Quotation
→ Cascades to QuotationItems and Job (if exists)

### Delete Job
→ Cascades to Measurements, Payments, ActivityLogs

### Delete Measurement
→ Cascades to MeasurementItems

### Delete QuotationItem
❌ **Blocked** if referenced by MeasurementItem (`ondelete="RESTRICT"`)

---

## Validation Tips

### Before creating Quotation
- Customer must exist
- At least one Product should be selected for items

### Before creating Job
- Quotation must be APPROVED
- Quotation should have at least one item

### Before creating Payment
- Job must exist
- `payment_order` should be sequential (1, 2, 3...)
- Total payment amounts should not exceed Job's final_price

### Before creating Measurement
- Job must exist
- `measurement_number` defaults to 1, increment for re-measures

### Before creating MeasurementItem
- Measurement must exist
- QuotationItem must exist and belong to the same Job's Quotation
- `piece_number` helps identify which specific piece this measurement is for
