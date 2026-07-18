# Database Seeding Guide

## Overview

The database seeding system populates the ERP database with realistic sample data for development, testing, and demonstration purposes.

## Features

✅ **Idempotent** - Running multiple times does not duplicate data  
✅ **Modular** - Each seeder handles one table/domain  
✅ **Realistic** - Egyptian names, phone numbers, cities, and business data  
✅ **Complete** - Seeds all 11 tables with proper relationships  
✅ **Production-Ready** - Proper error handling and logging  

## Quick Start

### 1. Prerequisites

Ensure your environment is set up:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure database connection in .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/erp_db

# Run migrations to create schema
alembic upgrade head
```

### 2. Seed the Database

**Option A: Using the CLI script (recommended)**

```bash
python seed_database.py
```

**Option B: Using Python module**

```bash
python -m app.database.seeders.run_all
```

### 3. Verify the Data

Connect to your database and verify:

```sql
SELECT 'product_categories' as table_name, count(*) FROM product_categories
UNION ALL
SELECT 'products', count(*) FROM products
UNION ALL
SELECT 'customers', count(*) FROM customers
UNION ALL
SELECT 'quotations', count(*) FROM quotations
UNION ALL
SELECT 'quotation_items', count(*) FROM quotation_items
UNION ALL
SELECT 'jobs', count(*) FROM jobs
UNION ALL
SELECT 'payments', count(*) FROM payments
UNION ALL
SELECT 'measurements', count(*) FROM measurements
UNION ALL
SELECT 'measurement_items', count(*) FROM measurement_items
UNION ALL
SELECT 'activity_logs', count(*) FROM activity_logs;
```

Expected counts (approximate):
- Product Categories: 5
- Products: 40 (8 per category)
- Customers: 10
- Quotations: ~10-15
- Quotation Items: ~40-60 (2-5 per quotation)
- Jobs: ~8-12 (only approved quotations)
- Payments: ~24-36 (3 per job)
- Measurements: ~8-12 (1 per job)
- Measurement Items: ~16-48 (2-4 per measurement)
- Activity Logs: ~32-60 (4-5 per job)

## Data Generated

### Product Categories
5 main business categories:
- Windows
- Doors
- Kitchens
- Shower Cabins
- Smart Locks

### Products
40 realistic products (8 per category):
- Sliding Window, Casement Window, Fixed Window, etc.
- Sliding Door, French Door, Pivot Door, etc.
- Modern Kitchen, Classic Kitchen, L-Shape Kitchen, etc.
- Frameless Shower Cabin, Corner Shower Cabin, etc.
- Smart Lock X100, Biometric Lock, Keypad Lock, etc.

### Customers
10 Egyptian customers with:
- Arabic names (Mohamed Ahmed, Fatma Hassan, etc.)
- Egyptian phone numbers (+20 format)
- Egyptian cities (Cairo, Alexandria, Giza, etc.)
- Google Maps location URLs
- Alternative phone numbers

### Quotations
Multiple quotations per customer with:
- Various statuses (Draft, Sent, Approved, Rejected, Expired)
- 2-5 items per quotation
- Realistic pricing (1,000 - 50,000 EGP)
- 0-15% discounts
- Notes and descriptions

### Jobs
Jobs created for approved quotations with:
- Realistic lifecycle: measurement → production → installation → completion
- Status progression (Pending Measurement, In Production, Ready for Installation, Completed, etc.)
- Proper date sequences
- Notes tracking progress

### Payments
3 payments per job following the business rule:
- **Deposit**: 70% of job total
- **Production**: 20% of job total
- **Final**: 10% of job total

Payment statuses vary (Pending, Paid, Overdue) with realistic dates.

### Measurements
Measurements for each job including:
- Measurement number (M-001, M-002, etc.)
- Egyptian measurer names (Ahmed Mostafa, Mohamed Hassan, etc.)
- Visit dates
- Multiple measurement items per measurement

### Measurement Items
Detailed measurements with:
- Room names (Living Room, Bedroom, Kitchen, etc.)
- Piece numbers (Window 1, Door 2, Kitchen Island, etc.)
- Width and height dimensions (realistic ranges)
- Quantities
- Notes

### Activity Logs
Complete audit trail of job lifecycle:
- Job Created
- Measurement Scheduled
- Production Started
- Installation Completed
- Job Completed

## Advanced Usage

### Clear All Data

⚠️ **WARNING**: This deletes ALL data from the database. Use only in development!

**Using CLI:**
```bash
python seed_database.py --clear
```

**Using Python module:**
```bash
python -m app.database.seeders.run_all --clear
```

### Use Individual Seeders

For testing or custom workflows:

```python
import asyncio
from app.db.session import AsyncSessionLocal
from app.database.seeders import seed_categories, seed_products

async def seed_products_only():
    async with AsyncSessionLocal() as session:
        # Seed categories first (dependency)
        categories_map = await seed_categories(session)
        
        # Seed products
        products = await seed_products(session, categories_map)
        
        print(f"Seeded {len(products)} products")

asyncio.run(seed_products_only())
```

### Customize Seeded Data

To modify the data generated, edit the individual seeder files:

- `app/database/seeders/category_seeder.py` - Product categories
- `app/database/seeders/product_seeder.py` - Products
- `app/database/seeders/customer_seeder.py` - Customers
- `app/database/seeders/quotation_seeder.py` - Quotations
- `app/database/seeders/job_seeder.py` - Jobs
- `app/database/seeders/payment_seeder.py` - Payments
- `app/database/seeders/measurement_seeder.py` - Measurements
- `app/database/seeders/activity_log_seeder.py` - Activity logs

## Seeding Order

Seeders run in dependency order to respect foreign key constraints:

1. **Product Categories** (no dependencies)
2. **Products** (depends on categories)
3. **Customers** (no dependencies)
4. **Quotations & Items** (depends on customers and products)
5. **Jobs** (depends on approved quotations)
6. **Payments** (depends on jobs)
7. **Measurements & Items** (depends on jobs)
8. **Activity Logs** (depends on jobs)

## Architecture

### Idempotency

Each seeder checks for existing data before creating new records:

```python
# Check if record exists
result = await session.execute(
    select(Model).where(Model.unique_field == value)
)
existing = result.scalar_one_or_none()

if existing:
    # Use existing record
    return existing
else:
    # Create new record
    record = Model(...)
    session.add(record)
    return record
```

### Error Handling

The main orchestrator (`run_all.py`) wraps all seeding in a try-catch block with detailed logging:

```python
try:
    categories_map = await seed_categories(session)
    products = await seed_products(session, categories_map)
    # ... more seeders
except Exception as e:
    logger.error(f"Seeding failed: {e}", exc_info=True)
    raise
```

### Logging

All seeders use the centralized logging system:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Starting seeding...")
logger.debug(f"Created record: {record.id}")
```

## Troubleshooting

### Issue: "No module named 'app'"

**Solution**: Run from the backend directory:
```bash
cd backend
python seed_database.py
```

### Issue: "Database connection failed"

**Solution**: Check your `.env` file:
```bash
# Ensure DATABASE_URL is correct
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/erp_db
```

### Issue: "Foreign key constraint violation"

**Solution**: Ensure migrations are up to date:
```bash
alembic upgrade head
```

### Issue: "Duplicate key value"

This should not happen due to idempotency checks. If it does:
1. Check the seeder code for the affected table
2. Ensure the uniqueness check is correct
3. Clear data and re-seed: `python seed_database.py --clear && python seed_database.py`

### Issue: "Seeding is too slow"

**Optimization tips**:
1. Use batch inserts where possible
2. Reduce the number of generated records in seeder files
3. Ensure database indexes exist (run migrations)
4. Use a local database instead of remote

## Testing

To verify seeders work correctly:

```bash
# 1. Clear database
python seed_database.py --clear

# 2. Seed database
python seed_database.py

# 3. Verify counts
psql -d erp_db -c "SELECT count(*) FROM customers;"

# 4. Clear again (test cleanup)
python seed_database.py --clear

# 5. Verify empty
psql -d erp_db -c "SELECT count(*) FROM customers;"
```

## Integration with Development Workflow

### Fresh Database Setup

```bash
# Drop and recreate database
dropdb erp_db
createdb erp_db

# Run migrations
alembic upgrade head

# Seed data
python seed_database.py
```

### Reset Database

```bash
# Clear and re-seed
python seed_database.py --clear
python seed_database.py
```

### Docker Integration

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    # ... existing config
    command: >
      sh -c "alembic upgrade head && 
             python seed_database.py && 
             uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

## Best Practices

1. **Never run `--clear` in production** - It deletes all data!
2. **Customize for your needs** - Edit seeder files to match your business
3. **Keep it realistic** - Use data that resembles production data
4. **Version control seeders** - Track changes to sample data
5. **Document custom data** - Add comments for non-obvious data patterns
6. **Test idempotency** - Run seeders multiple times to ensure no duplicates
7. **Use in CI/CD** - Seed test databases automatically in pipelines

## Future Enhancements

Potential improvements for the seeding system:

- [ ] Add faker library for more varied data generation
- [ ] Support multiple locales (not just Egyptian data)
- [ ] Add configuration file for controlling seeded quantities
- [ ] Generate data from templates or YAML files
- [ ] Add progress bars for long-running seeds
- [ ] Support partial seeding (seed only specific tables)
- [ ] Add data validation after seeding
- [ ] Generate seeding reports (CSV/JSON summaries)
- [ ] Add performance benchmarks

## Related Documentation

- [Migration Guide](MIGRATION_GUIDE.md) - Database schema migrations
- [Models Summary](models_summary.md) - SQLAlchemy models reference
- [README](../README.md) - Project overview

## Support

For issues or questions about database seeding:
1. Check this guide first
2. Review the seeder source code in `app/database/seeders/`
3. Check application logs for detailed error messages
4. Open a GitHub issue with logs and steps to reproduce

---

**Last Updated**: July 18, 2026  
**Maintainer**: ERP Backend Team
