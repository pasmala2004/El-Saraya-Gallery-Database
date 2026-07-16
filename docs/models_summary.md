# SQLAlchemy Models Summary

> **Status:** Implemented — Updated with business-specific improvements  
> All 11 models are implemented using SQLAlchemy 2.0 typed declarative mapping.

---

## Model Hierarchy

```
BaseEntity (abstract — id, created_at, updated_at)
├── Customer
├── ProductCategory
├── Product
├── Quotation
├── QuotationItem
├── Job
├── Measurement
├── MeasurementItem
├── Payment
├── ActivityLog
└── Report
```

---

## Models Overview

### 1. Customer
**Table:** `customers`

| Field              | Type         | Constraints |
|--------------------|--------------|-------------|
| id                 | UUID         | PK          |
| full_name          | String(255)  | NOT NULL    |
| phone_number       | String(50)   | NOT NULL    |
| alternative_phone  | String(50)   | nullable    |
| address            | Text         | nullable    |
| city               | String(100)  | nullable    |
| location_url       | String(500)  | nullable    |
| notes              | Text         | nullable    |
| created_at         | DateTime(tz) | NOT NULL    |
| updated_at         | DateTime(tz) | NOT NULL    |

**Relationships:**
- `quotations` → many Quotation (cascade all, delete-orphan)

**New:** `location_url` for Google Maps links

---

### 2. ProductCategory
**Table:** `product_categories`

| Field      | Type        | Constraints        |
|------------|-------------|--------------------|
| id         | UUID        | PK                 |
| name       | String(100) | NOT NULL, UNIQUE   |
| created_at | DateTime(tz)| NOT NULL           |
| updated_at | DateTime(tz)| NOT NULL           |

**Relationships:**
- `products` → many Product (cascade all, delete-orphan)

---

### 3. Product
**Table:** `products`

| Field       | Type        | Constraints          |
|-------------|-------------|----------------------|
| id          | UUID        | PK                   |
| category_id | UUID        | FK → product_categories.id, NOT NULL, indexed |
| name        | String(255) | NOT NULL             |
| active      | Boolean     | NOT NULL, default=True |
| created_at  | DateTime(tz)| NOT NULL             |
| updated_at  | DateTime(tz)| NOT NULL             |

**Relationships:**
- `category` → ProductCategory (joined)
- `quotation_items` → many QuotationItem

**Examples:** Sliding Window, Casement Window, French Door, Kitchen, Smart Lock

---

### 4. Quotation
**Table:** `quotations`

| Field             | Type               | Constraints                  |
|-------------------|--------------------|------------------------------|
| id                | UUID               | PK                           |
| quotation_number  | String(50)         | NOT NULL, UNIQUE, indexed    |
| customer_id       | UUID               | FK → customers.id, NOT NULL, indexed |
| quotation_date    | Date               | NOT NULL                     |
| status            | quotation_status   | NOT NULL, default=DRAFT      |
| total_price       | Numeric(12,2)      | NOT NULL, default=0.00       |
| discount          | Numeric(12,2)      | NOT NULL, default=0.00       |
| final_price       | Numeric(12,2)      | NOT NULL, default=0.00       |
| notes             | Text               | nullable                     |
| created_at        | DateTime(tz)       | NOT NULL                     |
| updated_at        | DateTime(tz)       | NOT NULL                     |

**Relationships:**
- `customer` → Customer (joined)
- `items` → many QuotationItem (cascade all, delete-orphan)
- `job` → Job (uselist=False, cascade all, delete-orphan)

**Enum:** `quotation_status` = draft | sent | approved | rejected | cancelled

---

### 5. QuotationItem
**Table:** `quotation_items`

| Field        | Type          | Constraints                 |
|--------------|---------------|-----------------------------|
| id           | UUID          | PK                          |
| quotation_id | UUID          | FK → quotations.id, NOT NULL, indexed |
| product_id   | UUID          | FK → products.id, NOT NULL, indexed |
| quantity     | SmallInteger  | NOT NULL, default=1         |
| unit_price   | Numeric(12,2) | NOT NULL, default=0.00      |
| total_price  | Numeric(12,2) | NOT NULL, default=0.00      |
| description  | String(500)   | nullable                    |
| notes        | Text          | nullable                    |
| created_at   | DateTime(tz)  | NOT NULL                    |
| updated_at   | DateTime(tz)  | NOT NULL                    |

**Relationships:**
- `quotation` → Quotation (joined)
- `product` → Product (joined)
- `measurement_items` → many MeasurementItem (cascade all, delete-orphan)

**Note:** Width/height are NOT stored here — they belong to MeasurementItem.

---

### 6. Job
**Table:** `jobs`

| Field             | Type         | Constraints                      |
|-------------------|--------------|----------------------------------|
| id                | UUID         | PK                               |
| quotation_id      | UUID         | FK → quotations.id, NOT NULL, UNIQUE, indexed |
| status            | job_status   | NOT NULL, default=PENDING        |
| measurement_date  | Date         | nullable                         |
| production_start  | Date         | nullable                         |
| production_end    | Date         | nullable                         |
| installation_date | Date         | nullable                         |
| delivery_date     | Date         | nullable                         |
| completion_date   | Date         | nullable                         |
| notes             | Text         | nullable                         |
| created_at        | DateTime(tz) | NOT NULL                         |
| updated_at        | DateTime(tz) | NOT NULL                         |

**Relationships:**
- `quotation` → Quotation (joined)
- `measurements` → many Measurement (cascade all, delete-orphan)
- `payments` → many Payment (cascade all, delete-orphan)

**Enum:** `job_status` = pending | measuring | in_production | ready_for_installation | installed | completed | cancelled

**Note:** Renamed from `ready_for_delivery` to `ready_for_installation` for business accuracy

---

### 7. Measurement
**Table:** `measurements`

| Field              | Type         | Constraints              |
|--------------------|--------------|--------------------------|
| id                 | UUID         | PK                       |
| job_id             | UUID         | FK → jobs.id, NOT NULL, indexed |
| measurement_number | SmallInteger | NOT NULL, default=1      |
| visit_date         | Date         | nullable                 |
| measured_by        | String(255)  | nullable                 |
| notes              | Text         | nullable                 |
| created_at         | DateTime(tz) | NOT NULL                 |
| updated_at         | DateTime(tz) | NOT NULL                 |

**Relationships:**
- `job` → Job (joined)
- `items` → many MeasurementItem (cascade all, delete-orphan)

**Notes:** 
- `measurement_number` supports repeated site visits (1st visit = 1, re-measure = 2, etc.)
- `measured_by` tracks who performed the measurement (no Users table required)

---

### 8. MeasurementItem
**Table:** `measurement_items`

| Field             | Type          | Constraints                   |
|-------------------|---------------|-------------------------------|
| id                | UUID          | PK                            |
| measurement_id    | UUID          | FK → measurements.id, NOT NULL, indexed |
| quotation_item_id | UUID          | FK → quotation_items.id, NOT NULL, indexed |
| room_name         | String(100)   | nullable                      |
| piece_number      | String(100)   | nullable                      |
| width             | Numeric(10,2) | nullable                      |
| height            | Numeric(10,2) | nullable                      |
| quantity          | SmallInteger  | NOT NULL, default=1           |
| notes             | Text          | nullable                      |
| created_at        | DateTime(tz)  | NOT NULL                      |
| updated_at        | DateTime(tz)  | NOT NULL                      |

**Relationships:**
- `measurement` → Measurement (joined)
- `quotation_item` → QuotationItem (joined)

**New:** `piece_number` to identify specific pieces (e.g., "Window 1", "Door 2", "Kitchen Island")

---

### 9. Payment
**Table:** `payments`

| Field          | Type            | Constraints                |
|----------------|-----------------|----------------------------|
| id             | UUID            | PK                         |
| job_id         | UUID            | FK → jobs.id, NOT NULL, indexed |
| payment_order  | SmallInteger    | NOT NULL                   |
| payment_type   | payment_type    | NOT NULL                   |
| payment_method | payment_method  | NOT NULL                   |
| percentage     | Numeric(5,2)    | NOT NULL, default=0.00     |
| amount         | Numeric(12,2)   | NOT NULL, default=0.00     |
| due_date       | Date            | nullable                   |
| paid_date      | Date            | nullable                   |
| status         | payment_status  | NOT NULL, default=PENDING  |
| notes          | Text            | nullable                   |
| created_at     | DateTime(tz)    | NOT NULL                   |
| updated_at     | DateTime(tz)    | NOT NULL                   |

**Relationships:**
- `job` → Job (joined)

**Enums:**
- `payment_type` (business milestone) = deposit | production | final
- `payment_method` (how customer pays) = cash | bank_transfer | instapay | cheque | other
- `payment_status` = pending | paid | overdue | cancelled

**Important:** Separated `payment_type` (business milestone) from `payment_method` (payment mechanism)

---

### 10. ActivityLog
**Table:** `activity_logs`

| Field        | Type         | Constraints              |
|--------------|--------------|--------------------------|
| id           | UUID         | PK                       |
| job_id       | UUID         | FK → jobs.id, NOT NULL, indexed |
| action       | String(100)  | NOT NULL                 |
| description  | Text         | nullable                 |
| created_at   | DateTime(tz) | NOT NULL                 |
| updated_at   | DateTime(tz) | NOT NULL                 |

**Relationships:**
- `job` → Job (joined)

**Purpose:** Audit trail for Job activities and events throughout the lifecycle

---

### 11. Report
**Table:** `reports`

| Field        | Type         | Constraints        |
|--------------|--------------|--------------------|
| id           | UUID         | PK                 |
| report_date  | Date         | NOT NULL, indexed  |
| generated_at | DateTime(tz) | NOT NULL           |
| file_path    | String(500)  | NOT NULL           |
| created_at   | DateTime(tz) | NOT NULL           |
| updated_at   | DateTime(tz) | NOT NULL           |

**No relationships**

---

## Relationship Graph

```
Customer
  └─→ Quotation (1:N)
       ├─→ QuotationItem (1:N)
       │    ├─→ Product (N:1)
       │    │    └─→ ProductCategory (N:1)
       │    └─→ MeasurementItem (1:N)
       └─→ Job (1:1)
            ├─→ Measurement (1:N)
            │    └─→ MeasurementItem (1:N)
            ├─→ Payment (1:N)
            └─→ ActivityLog (1:N)

Report (standalone)
```

---

## Recent Business Improvements

### Payment Model Refactoring
**Separated payment type from payment method:**
- `payment_type` → Business milestone (Deposit, Production, Final)
- `payment_method` → How customer pays (Cash, Bank Transfer, Instapay, Cheque, Other)

This allows tracking business phases independently from the actual payment mechanism.

### JobStatus Clarification
**Renamed:** `ready_for_delivery` → `ready_for_installation`

More accurately reflects the business process where products are ready to be installed at the customer site.

### Measurement Enhancements
**Added:** `measured_by` field (String, nullable)

Tracks who performed the measurement without requiring a Users table. Can store employee names directly.

### MeasurementItem Identification
**Added:** `piece_number` field (String, nullable)

Identifies specific pieces being measured. Examples:
- "Window 1"
- "Door 2"
- "Kitchen Island"
- "Bathroom Window"

### Customer Location Tracking
**Added:** `location_url` field (String, nullable)

Stores Google Maps links or similar location URLs for easy navigation to customer sites.

### Activity Logging
**New Model:** `ActivityLog`

Provides audit trail for Job activities throughout the lifecycle. Tracks actions and descriptions with timestamps.

---

## Key Design Decisions

1. **Two-layer inheritance:** All models inherit from `BaseEntity`, not directly from `Base`, allowing future shared behavior like soft-delete or versioning.

2. **UUID primary keys:** Every table uses `UUID` with both Python-side and DB-side defaults for maximum flexibility.

3. **Timezone-aware timestamps:** `created_at` and `updated_at` use `DateTime(timezone=True)` with explicit UTC handling.

4. **Cascade rules:**
   - Parent → child: `cascade="all, delete-orphan"` (e.g., Customer → Quotations)
   - Lookup FKs: `ondelete="RESTRICT"` (e.g., Product → ProductCategory)

5. **Lazy loading strategy:**
   - Parent entities: `lazy="joined"` (eager load with JOIN)
   - Collections: `lazy="selectin"` (efficient N+1 avoidance) or `lazy="select"` (on-demand)

6. **No pricing on Product:** Unit prices live on `QuotationItem` so the same product can have different prices per quote.

7. **No dimensions on QuotationItem:** Width/height are measurement data and belong to `MeasurementItem`.

8. **Payment phases vs methods:** `payment_type` tracks business milestones (Deposit/Production/Final) while `payment_method` tracks how the customer pays.

9. **Measurement visits:** `measurement_number` allows multiple site visits per job without creating duplicate Job records.

10. **No Users table:** User-related fields like `measured_by` are simple strings, avoiding premature authentication complexity.
