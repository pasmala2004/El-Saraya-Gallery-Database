# Database Seeding - Testing Checklist

## Pre-Testing Setup

Before testing the seeding system, ensure:

- [ ] Docker Desktop is running
- [ ] `.env` file exists (copy from `.env.example`)
- [ ] Database is running: `docker compose up -d db`
- [ ] Migrations applied: `alembic upgrade head`

## Quick Setup

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start database
docker compose up -d db

# 3. Wait for database (check logs)
docker compose logs -f db
# Wait for: "database system is ready to accept connections"

# 4. Run migrations
alembic upgrade head

# 5. Verify schema
docker compose exec db psql -U erp_user -d erp_db -c "\dt"
# Should show 11 tables
```

## Test Plan

### Test 1: Basic Seeding
**Objective**: Verify seeding works end-to-end

```bash
# Run seeder
python seed_database.py

# Expected output:
# ======================================================================
# STARTING DATABASE SEEDING
# ======================================================================
# [1/8] Seeding Product Categories...
# ✓ Categories: 5 total
# [2/8] Seeding Products...
# ✓ Products: 40 total
# ...
# ✅ Database is now populated with realistic ERP data!
```

**Success Criteria:**
- No errors during execution
- All 8 steps complete
- Summary shows expected counts

### Test 2: Verify Data
**Objective**: Confirm data was actually inserted

```sql
-- Run in psql:
docker compose exec db psql -U erp_user -d erp_db

-- Check counts
SELECT 'product_categories' as table_name, count(*) FROM product_categories
UNION ALL SELECT 'products', count(*) FROM products
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'quotations', count(*) FROM quotations
UNION ALL SELECT 'quotation_items', count(*) FROM quotation_items
UNION ALL SELECT 'jobs', count(*) FROM jobs
UNION ALL SELECT 'payments', count(*) FROM payments
UNION ALL SELECT 'measurements', count(*) FROM measurements
UNION ALL SELECT 'measurement_items', count(*) FROM measurement_items
UNION ALL SELECT 'activity_logs', count(*) FROM activity_logs;
```

**Expected Counts:**
| Table | Expected Count |
|-------|----------------|
| product_categories | 5 |
| products | 40 |
| customers | 10 |
| quotations | ~10-15 |
| quotation_items | ~40-60 |
| jobs | ~8-12 |
| payments | ~24-36 |
| measurements | ~8-12 |
| measurement_items | ~16-48 |
| activity_logs | ~32-60 |

### Test 3: Idempotency
**Objective**: Verify running multiple times doesn't duplicate data

```bash
# Run seeder again
python seed_database.py

# Check logs - should show many "already exists" messages
# Verify counts are the same as Test 2
```

**Success Criteria:**
- No errors
- Counts unchanged from Test 2
- Logs show existing records detected

### Test 4: Data Quality
**Objective**: Verify data is realistic and correct

```sql
-- Check Egyptian phone numbers
SELECT full_name, phone_number FROM customers LIMIT 5;
-- Should show +20 format

-- Check payment split (70/20/10)
SELECT j.id, 
       (SELECT amount FROM payments WHERE job_id = j.id AND payment_type = 'deposit') as deposit,
       (SELECT amount FROM payments WHERE job_id = j.id AND payment_type = 'production') as production,
       (SELECT amount FROM payments WHERE job_id = j.id AND payment_type = 'final') as final
FROM jobs j LIMIT 3;
-- Verify: deposit ~70%, production ~20%, final ~10%

-- Check foreign key relationships
SELECT q.quotation_number, q.status, j.id as job_id
FROM quotations q
LEFT JOIN jobs j ON j.quotation_id = q.id
WHERE q.status = 'approved';
-- All approved quotations should have jobs

-- Check measurement items have piece numbers
SELECT measurement_id, piece_number, room_name, width, height
FROM measurement_items
LIMIT 10;
-- All should have piece_number (e.g., "Window 1", "Door 2")
```

**Success Criteria:**
- Phone numbers use +20 format
- Payment splits are approximately 70/20/10
- All approved quotations have jobs
- All measurement items have piece numbers
- Dates are realistic and sequential

### Test 5: Clear Functionality
**Objective**: Verify data can be cleared safely

```bash
# Clear all data (with confirmation)
python seed_database.py --clear

# Verify empty
docker compose exec db psql -U erp_user -d erp_db -c "SELECT count(*) FROM customers;"
# Should return: 0
```

**Success Criteria:**
- Confirmation prompt appears
- All tables empty after clearing
- No foreign key errors during deletion

### Test 6: Re-seed After Clear
**Objective**: Verify can seed again after clearing

```bash
# Seed again
python seed_database.py

# Verify counts match Test 2
```

**Success Criteria:**
- Seeding completes successfully
- Counts match original seed

### Test 7: Module Import
**Objective**: Verify seeders can be used programmatically

```python
# Create test_seeder_import.py
import asyncio
from app.db.session import AsyncSessionLocal
from app.database.seeders import seed_categories, seed_products

async def test():
    async with AsyncSessionLocal() as session:
        categories = await seed_categories(session)
        products = await seed_products(session, categories)
        print(f"✓ Created {len(categories)} categories")
        print(f"✓ Created {len(products)} products")

asyncio.run(test())
```

```bash
# Run test
python test_seeder_import.py
```

**Success Criteria:**
- Script runs without errors
- Categories and products created

### Test 8: Error Handling
**Objective**: Verify graceful error handling

```bash
# Test with database down
docker compose stop db
python seed_database.py
# Should show clear error message, not crash

# Restart database
docker compose start db
```

**Success Criteria:**
- Clear error message
- No cryptic tracebacks
- Graceful exit

## Performance Testing

### Timing Benchmark

```bash
# Time the seeding operation
time python seed_database.py

# Expected: < 10 seconds for full seed
```

**Performance Targets:**
- Total time: < 10 seconds
- No timeout errors
- No memory issues

## Edge Cases

### Test: Large Database
**Scenario**: Seed into database with existing unrelated data

```sql
-- Add some unrelated data first
INSERT INTO product_categories (name) VALUES ('Test Category');
INSERT INTO products (category_id, name, active) 
VALUES ((SELECT id FROM product_categories WHERE name = 'Test Category'), 'Test Product', true);
```

```bash
# Seed should not affect existing data
python seed_database.py
```

**Success Criteria:**
- Existing data unchanged
- Seeded data added alongside

### Test: Partial Failure Recovery
**Scenario**: If one seeder fails mid-execution

*Note: This requires code modification to simulate failure*

## Test Results Template

```markdown
## Test Run: [Date/Time]
**Tester**: [Name]
**Environment**: [Dev/Docker/Local]
**Database**: PostgreSQL [version]

| Test | Status | Notes |
|------|--------|-------|
| Basic Seeding | ✅/❌ | |
| Verify Data | ✅/❌ | |
| Idempotency | ✅/❌ | |
| Data Quality | ✅/❌ | |
| Clear Functionality | ✅/❌ | |
| Re-seed After Clear | ✅/❌ | |
| Module Import | ✅/❌ | |
| Error Handling | ✅/❌ | |
| Performance | ✅/❌ | Time: ____ seconds |

**Issues Found:**
- [Issue 1]
- [Issue 2]

**Overall Result**: PASS/FAIL
```

## Continuous Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/test-seeding.yml
name: Test Database Seeding

on: [push, pull_request]

jobs:
  test-seeding:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: erp_user
          POSTGRES_PASSWORD: erp_password
          POSTGRES_DB: erp_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run migrations
        run: alembic upgrade head
      
      - name: Test seeding
        run: python seed_database.py
      
      - name: Verify data
        run: |
          psql postgresql://erp_user:erp_password@localhost:5432/erp_db \
            -c "SELECT count(*) FROM customers;" | grep -q "10"
      
      - name: Test idempotency
        run: python seed_database.py
      
      - name: Test clear
        run: python seed_database.py --clear <<< "y"
```

## Troubleshooting During Testing

| Problem | Solution |
|---------|----------|
| "Module not found" | Run from backend/ directory |
| "Database error" | Check DATABASE_URL in .env |
| "Foreign key violation" | Run migrations first: `alembic upgrade head` |
| "Timeout" | Check database is running: `docker compose ps` |
| "Permission denied" | Make script executable: `chmod +x seed_database.py` |

---

**Last Updated**: July 18, 2026  
**Status**: Ready for testing
