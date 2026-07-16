# Database Schema Plan

> **Status:** Planned — models not yet implemented.  
> This document is the single source of truth for the database schema
> before SQLAlchemy models are written.  Update it here first, then
> implement the models.

---

## Inheritance rule

Every model inherits from `BaseEntity` (not directly from `Base`).

```
Base  (DeclarativeBase — metadata registry only)
 └── BaseEntity  (abstract — id, created_at, updated_at)
      ├── Customer
      ├── Quotation
      ├── Job
      ├── Measurement
      ├── Payment
      └── … future models
```

---

## Tables

### `customers`

| Column               | Type                        | Constraints              |
|----------------------|-----------------------------|--------------------------|
| id                   | UUID                        | PK, default gen_random_uuid() |
| full_name            | VARCHAR(255)                | NOT NULL                 |
| phone_number         | VARCHAR(50)                 | NOT NULL                 |
| alternative_phone    | VARCHAR(50)                 | nullable                 |
| address              | TEXT                        | nullable                 |
| city                 | VARCHAR(100)                | nullable                 |
| notes                | TEXT                        | nullable                 |
| created_at           | TIMESTAMPTZ                 | NOT NULL, default now()  |
| updated_at           | TIMESTAMPTZ                 | NOT NULL, default now()  |

---

### `quotations`

| Column               | Type                        | Constraints              |
|----------------------|-----------------------------|--------------------------|
| id                   | UUID                        | PK                       |
| customer_id          | UUID                        | FK → customers.id, NOT NULL |
| status               | quotation_status (enum)     | NOT NULL                 |
| total_amount         | NUMERIC(12, 2)              | NOT NULL                 |
| notes                | TEXT                        | nullable                 |
| created_at           | TIMESTAMPTZ                 | NOT NULL                 |
| updated_at           | TIMESTAMPTZ                 | NOT NULL                 |

---

### `jobs`

| Column               | Type                        | Constraints              |
|----------------------|-----------------------------|--------------------------|
| id                   | UUID                        | PK                       |
| quotation_id         | UUID                        | FK → quotations.id, NOT NULL |
| status               | job_status (enum)           | NOT NULL                 |
| measurement_date     | DATE                        | nullable                 |
| production_start     | DATE                        | nullable                 |
| production_end       | DATE                        | nullable                 |
| installation_date    | DATE                        | nullable                 |
| delivery_date        | DATE                        | nullable                 |
| completion_date      | DATE                        | nullable                 |
| notes                | TEXT                        | nullable                 |
| created_at           | TIMESTAMPTZ                 | NOT NULL                 |
| updated_at           | TIMESTAMPTZ                 | NOT NULL                 |

---

### `measurements`

| Column               | Type                        | Constraints              |
|----------------------|-----------------------------|--------------------------|
| id                   | UUID                        | PK                       |
| job_id               | UUID                        | FK → jobs.id, NOT NULL   |
| measurement_number   | SMALLINT                    | NOT NULL, default 1      |
| notes                | TEXT                        | nullable                 |
| created_at           | TIMESTAMPTZ                 | NOT NULL                 |
| updated_at           | TIMESTAMPTZ                 | NOT NULL                 |

> `measurement_number` supports repeated site visits for the same job
> (first visit = 1, re-measure = 2, …).

---

### `payments`

| Column               | Type                        | Constraints              |
|----------------------|-----------------------------|--------------------------|
| id                   | UUID                        | PK                       |
| job_id               | UUID                        | FK → jobs.id, NOT NULL   |
| payment_order        | SMALLINT                    | NOT NULL                 |
| amount               | NUMERIC(12, 2)              | NOT NULL                 |
| payment_type         | payment_type (enum)         | NOT NULL                 |
| payment_date         | DATE                        | nullable                 |
| notes                | TEXT                        | nullable                 |
| created_at           | TIMESTAMPTZ                 | NOT NULL                 |
| updated_at           | TIMESTAMPTZ                 | NOT NULL                 |

> `payment_order` defines the installment sequence (1 = first payment,
> 2 = second, …) independently of the payment method.

---

## Enums (to be implemented in `app/enums/`)

### `quotation_status`  → `app/enums/quotation.py`
| Value        | Meaning                          |
|--------------|----------------------------------|
| draft        | Not yet sent to customer         |
| sent         | Sent, awaiting response          |
| approved     | Customer accepted                |
| rejected     | Customer declined                |
| cancelled    | Internally cancelled             |

### `job_status`  → `app/enums/job.py`
| Value               | Meaning                     |
|---------------------|-----------------------------|
| pending             | Quotation approved, not started |
| measuring           | Measurement visit scheduled |
| in_production       | Fabrication underway        |
| ready_for_delivery  | Ready to install/deliver    |
| installed           | On-site installation done   |
| completed           | Job fully closed            |
| cancelled           | Job cancelled               |

### `payment_type`  → `app/enums/payment.py`
| Value        | Meaning                          |
|--------------|----------------------------------|
| cash         | Cash payment                     |
| bank_transfer| Bank / wire transfer             |
| cheque       | Cheque                           |
| online       | Online / card payment            |
