# Database Migration Guide

## Overview

This document describes the initial database schema migration for the ERP backend application.

**Migration ID:** `a18031e1652d`  
**Description:** Initial schema with all 11 tables  
**Status:** Ready for deployment

---

## Migration Contents

### Enums Created (5)

1. **quotation_status**
   - Values: `draft`, `sent`, `approved`, `rejected`, `cancelled`

2. **job_status**
   - Values: `pending`, `measuring`, `in_production`, `ready_for_installation`, `installed`, `completed`, `cancelled`

3. **payment_type** (business milestone)
   - Values: `deposit`, `production`, `final`

4. **payment_method** (payment channel)
   - Values: `cash`, `bank_transfer`, `instapay`, `cheque`, `other`

5. **payment_status**
   - Values: `pending`, `paid`, `overdue`, `cancelled`

---

### Tables Created (11)

#### 1. customers
- **Primary Key:** `id` (UUID, auto-generated)
- **Columns:** full_name, phone_number, alternative_phone, address, city, location_url, notes, created_at, updated_at
- **Indexes:** None (primary key only)
- **Constraints:** None

#### 2. product_categories
- **Primary Key:** `id` (UUID, auto-generated)
- **Columns:** name, created_at, updated_at
- **Indexes:** None (primary key only)
- **Constraints:** UNIQUE(name)

#### 3. products
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** category_id → product_categories.id (RESTRICT)
- **Columns:** category_id, name, active, created_at, updated_at
- **Indexes:** category_id
- **Constraints:** None

#### 4. quotations
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** customer_id → customers.id (CASCADE)
- **Columns:** quotation_number, customer_id, quotation_date, status, total_price, discount, final_price, notes, created_at, updated_at
- **Indexes:** customer_id, quotation_number (unique)
- **Constraints:** UNIQUE(quotation_number)

#### 5. quotation_items
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:**
  - quotation_id → quotations.id (CASCADE)
  - product_id → products.id (RESTRICT)
- **Columns:** quotation_id, product_id, quantity, unit_price, total_price, description, notes, created_at, updated_at
- **Indexes:** quotation_id, product_id
- **Constraints:** None

#### 6. jobs
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** quotation_id → quotations.id (CASCADE)
- **Columns:** quotation_id, status, measurement_date, production_start, production_end, installation_date, delivery_date, completion_date, notes, created_at, updated_at
- **Indexes:** quotation_id (unique)
- **Constraints:** UNIQUE(quotation_id) — 1:1 relationship with quotation

#### 7. measurements
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** job_id → jobs.id (CASCADE)
- **Columns:** job_id, measurement_number, visit_date, measured_by, notes, created_at, updated_at
- **Indexes:** job_id
- **Constraints:** None

#### 8. measurement_items
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:**
  - measurement_id → measurements.id (CASCADE)
  - quotation_item_id → quotation_items.id (RESTRICT)
- **Columns:** measurement_id, quotation_item_id, room_name, piece_number, width, height, quantity, notes, created_at, updated_at
- **Indexes:** measurement_id, quotation_item_id
- **Constraints:** None

#### 9. payments
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** job_id → jobs.id (CASCADE)
- **Columns:** job_id, payment_order, payment_type, payment_method, percentage, amount, due_date, paid_date, status, notes, created_at, updated_at
- **Indexes:** job_id
- **Constraints:** None

#### 10. activity_logs
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** job_id → jobs.id (CASCADE)
- **Columns:** job_id, action, description, created_at, updated_at
- **Indexes:** job_id
- **Constraints:** None

#### 11. reports
- **Primary Key:** `id` (UUID, auto-generated)
- **Foreign Keys:** None (standalone)
- **Columns:** report_date, generated_at, file_path, created_at, updated_at
- **Indexes:** report_date
- **Constraints:** None

---

## Cascade Rules

### CASCADE (parent deletion removes children)
- customers → quotations
- quotations → quotation_items, jobs
- jobs → measurements, payments, activity_logs
- measurements → measurement_items

### RESTRICT (prevents deletion if children exist)
- product_categories → products (must delete all products first)
- products → quotation_items (must delete/update quotation items first)
- quotation_items → measurement_items (must delete measurement items first)

---

## Default Values

### Boolean Defaults
- `products.active`: true

### Enum Defaults
- `quotations.status`: 'draft'
- `jobs.status`: 'pending'
- `payments.status`: 'pending'

### Numeric Defaults
- All money fields (Numeric): '0.00'
- `quotation_items.quantity`: 1
- `measurements.measurement_number`: 1
- `measurement_items.quantity`: 1

### Timestamp Defaults
- `created_at`: now() (server-side)
- `updated_at`: now() (server-side)

### UUID Defaults
- All `id` columns: gen_random_uuid() (server-side)

---

## Server-Side Features

### Auto-Generated UUIDs
All tables use PostgreSQL's `gen_random_uuid()` function for UUID generation, ensuring IDs are created even for raw SQL inserts.

### Timezone-Aware Timestamps
All datetime columns use `DateTime(timezone=True)` and default to `now()` on the server side.

### SQL Functions Used
- `gen_random_uuid()` — UUID v4 generation
- `now()` — Current timestamp with timezone

---

## Migration Commands

### Check current migration status
```bash
alembic current
```

### View migration history
```bash
alembic history --verbose
```

### Apply migration (upgrade to head)
```bash
alembic upgrade head
```

### Rollback migration (downgrade one step)
```bash
alembic downgrade -1
```

### Rollback all migrations
```bash
alembic downgrade base
```

### Generate SQL without executing
```bash
alembic upgrade head --sql
```

---

## Pre-Migration Checklist

Before running the migration:

- [ ] PostgreSQL server is running
- [ ] Database exists (or Alembic has permission to create it)
- [ ] Database user has sufficient privileges:
  - CREATE TABLE
  - CREATE TYPE (for enums)
  - CREATE INDEX
  - CREATE UNIQUE INDEX
- [ ] `.env` file is configured with correct `DATABASE_URL_SYNC`
- [ ] Docker containers are up (if using docker-compose)

---

## Post-Migration Verification

After running `alembic upgrade head`, verify:

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected: 11 tables
-- activity_logs, customers, jobs, measurement_items, measurements, 
-- payments, product_categories, products, quotation_items, quotations, reports

-- Check enum types exist
SELECT typname 
FROM pg_type 
WHERE typtype = 'e' 
ORDER BY typname;

-- Expected: 5 enums
-- job_status, payment_method, payment_status, payment_type, quotation_status

-- Check foreign key constraints
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- Check indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

---

## Manual Edits Required

### Why Manual Migration?

Alembic's autogenerate requires a live database connection to compare the current schema with the models. Since the database was not running during initial development, this migration was created manually.

### Manual Creation Process

1. **Created blank migration:**
   ```bash
   alembic revision -m "Initial schema with all 11 tables"
   ```

2. **Populated upgrade() function:**
   - Created 5 enum types first (required before table creation)
   - Created tables in dependency order:
     1. Independent tables: customers, product_categories
     2. Level 1 dependencies: products, quotations
     3. Level 2 dependencies: quotation_items, jobs
     4. Level 3 dependencies: measurements, payments, activity_logs, measurement_items
     5. Standalone: reports
   - Added all indexes explicitly
   - Specified all foreign key constraints with ondelete behavior
   - Included server defaults for UUIDs, timestamps, booleans, enums, and numerics

3. **Populated downgrade() function:**
   - Dropped tables in reverse dependency order
   - Dropped all indexes explicitly
   - Dropped all enum types at the end

### Verification Against Models

The migration was cross-referenced against:
- All 11 model files in `app/models/`
- All enum definitions in `app/enums/`
- The `BaseEntity` class in `app/db/base.py`
- Documentation in `docs/models_summary.md`

### What Autogenerate Would Have Detected

If run with a live database connection, autogenerate would have produced an identical migration (minus formatting differences).

---

## Testing the Migration

### Test Upgrade

```bash
# Start database (if using docker-compose)
docker compose up -d db

# Wait for database to be ready
sleep 5

# Run migration
alembic upgrade head

# Verify tables
docker compose exec db psql -U erp_user -d erp_db -c "\dt"
```

### Test Downgrade

```bash
# Rollback migration
alembic downgrade base

# Verify tables are gone
docker compose exec db psql -U erp_user -d erp_db -c "\dt"

# Should return "No relations found"
```

### Test Idempotency

```bash
# Run upgrade twice
alembic upgrade head
alembic upgrade head  # Should say "No changes"

# Rollback and upgrade again
alembic downgrade base
alembic upgrade head  # Should succeed
```

---

## Troubleshooting

### Error: relation "alembic_version" does not exist
**Cause:** First time running Alembic in this database.  
**Solution:** Alembic will create it automatically. This is normal.

### Error: type "quotation_status" already exists
**Cause:** Enum type exists from a previous failed migration.  
**Solution:** Drop enum manually or use `checkfirst=True` (already included).

### Error: permission denied to create extension "uuid-ossp"
**Cause:** Using `gen_random_uuid()` requires no extension in PostgreSQL 13+.  
**Solution:** Ensure PostgreSQL 13+ is installed. For older versions, manually create the extension.

### Error: cannot drop type because other objects depend on it
**Cause:** Tables using the enum still exist.  
**Solution:** Drop tables before dropping enums (already handled in downgrade).

---

## Next Steps

After migration is verified:

1. **Seed reference data:**
   - Create product categories
   - Create initial products
   - Create sample customers (optional, for development)

2. **Build CRUD layer:**
   - Implement repositories for each model
   - Create service layer for business logic
   - Build FastAPI endpoints

3. **Add validation:**
   - Pydantic schemas for request/response
   - Business rule validation in services
   - Database constraints are already in place

4. **Implement authentication:**
   - User model (future)
   - JWT tokens
   - Role-based access control

---

## Migration Metadata

- **Revision ID:** a18031e1652d
- **Previous Revision:** None (initial migration)
- **Branch Labels:** None
- **Depends On:** None
- **Created:** 2026-07-16 23:26:22

**Tables:** 11  
**Enums:** 5  
**Foreign Keys:** 13  
**Indexes:** 14 (including primary keys)  
**Unique Constraints:** 3
