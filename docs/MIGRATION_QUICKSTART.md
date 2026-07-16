# Migration Quick Start

One-page reference for applying and verifying the database migration.

---

## Prerequisites

```bash
# 1. Database running
docker compose up -d db

# 2. Wait for it to be ready (5-10 seconds)
docker compose logs db | grep "ready to accept connections"
```

---

## Apply Migration

```bash
# Check current state (should show no migration applied)
alembic current

# Apply migration
alembic upgrade head

# Should output:
# INFO [alembic.runtime.migration] Running upgrade  -> a18031e1652d
```

---

## Verify Migration

### Quick Check (30 seconds)

```bash
# Connect to database
docker compose exec db psql -U erp_user -d erp_db

# Run these queries
\dt                          # List tables (expect 12: 11 + alembic_version)
\dT                          # List types (expect 5 enums)
\d customers                 # Describe customers table
\q                           # Quit
```

### Full Verification (2 minutes)

```bash
# Run comprehensive SQL verification
docker compose exec -T db psql -U erp_user -d erp_db < docs/verify_migration.sql
```

---

## Test Rollback

```bash
# Rollback to empty database
alembic downgrade base

# Verify tables are gone
docker compose exec db psql -U erp_user -d erp_db -c "\dt"
# Should show only alembic_version

# Re-apply migration
alembic upgrade head

# Verify tables are back
docker compose exec db psql -U erp_user -d erp_db -c "\dt"
# Should show 12 tables
```

---

## Migration Contents

**Tables:** 11  
- customers, product_categories, products
- quotations, quotation_items
- jobs, measurements, measurement_items
- payments, activity_logs, reports

**Enums:** 5  
- quotation_status, job_status
- payment_type, payment_method, payment_status

**Foreign Keys:** 13 (8 CASCADE + 5 RESTRICT)  
**Indexes:** 14 (excluding primary keys)  
**Unique Constraints:** 3

---

## Common Commands

```bash
# View migration history
alembic history

# Check current version
alembic current

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one step
alembic downgrade -1

# Generate SQL without applying
alembic upgrade head --sql > migration.sql
```

---

## Troubleshooting

### "No module named 'app'"
```bash
# Make sure you're in backend/ directory
cd backend
```

### "Cannot connect to database"
```bash
# Start database
docker compose up -d db

# Check it's running
docker compose ps db
```

### "Type already exists"
```bash
# Drop enum types manually
docker compose exec db psql -U erp_user -d erp_db -c "DROP TYPE IF EXISTS quotation_status CASCADE;"
# Then retry migration
```

### "Permission denied"
```bash
# Ensure user has privileges
docker compose exec db psql -U erp_user -d erp_db -c "GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;"
```

---

## Next Steps After Migration

1. **Test with Python**
   ```python
   from app.models import Customer
   from app.db.session import AsyncSessionLocal
   
   async def test():
       async with AsyncSessionLocal() as session:
           customer = Customer(full_name="Test", phone_number="123")
           session.add(customer)
           await session.commit()
           print(f"Created customer with ID: {customer.id}")
   ```

2. **Create seed data** → `app/database/seeders/`

3. **Build CRUD endpoints** → `app/api/v1/`

---

## Documentation Files

- `MIGRATION_GUIDE.md` — Complete documentation (3,400+ words)
- `MIGRATION_VERIFICATION.md` — Detailed checklist (900+ items)
- `MIGRATION_SUMMARY.md` — Overview and statistics
- `verify_migration.sql` — PostgreSQL verification script
- `MIGRATION_QUICKSTART.md` — This document

---

## Status: ✅ Ready for Deployment

The migration is production-ready and can be applied to any PostgreSQL 13+ database.
