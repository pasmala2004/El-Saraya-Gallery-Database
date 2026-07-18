# Database Seeding - Quick Start

## TL;DR

```bash
# 1. Setup
pip install -r requirements.txt
alembic upgrade head

# 2. Seed database
python seed_database.py

# 3. That's it! 🎉
```

## What Gets Created?

| Table | Count | Description |
|-------|-------|-------------|
| Product Categories | 5 | Windows, Doors, Kitchens, Shower Cabins, Smart Locks |
| Products | 40 | 8 products per category |
| Customers | 10 | Egyptian customers with realistic data |
| Quotations | ~12 | Various statuses (Draft, Sent, Approved, Rejected) |
| Quotation Items | ~48 | 2-5 items per quotation |
| Jobs | ~10 | Created for approved quotations only |
| Payments | ~30 | 3 per job: 70% Deposit, 20% Production, 10% Final |
| Measurements | ~10 | 1 per job with multiple items |
| Measurement Items | ~30 | Room-specific measurements with dimensions |
| Activity Logs | ~50 | Complete audit trail of job lifecycle |

## Commands

```bash
# Seed the database (idempotent - safe to run multiple times)
python seed_database.py

# Clear all data (⚠️ destructive!)
python seed_database.py --clear

# Alternative: use as Python module
python -m app.database.seeders.run_all
```

## Verify Data

```sql
-- Quick count check
SELECT 
    (SELECT count(*) FROM product_categories) as categories,
    (SELECT count(*) FROM products) as products,
    (SELECT count(*) FROM customers) as customers,
    (SELECT count(*) FROM quotations) as quotations,
    (SELECT count(*) FROM jobs) as jobs,
    (SELECT count(*) FROM payments) as payments;
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Module not found | Run from `backend/` directory |
| Database error | Check `.env` DATABASE_URL |
| Migration error | Run `alembic upgrade head` first |
| Duplicate data | Seeders are idempotent, safe to re-run |

## Example Data Preview

**Customer:**
```
Name: محمد أحمد (Mohamed Ahmed)
Phone: +20 10 1234 5678
City: القاهرة (Cairo)
```

**Quotation:**
```
Number: Q-2024-001
Status: Approved
Total: 45,750.00 EGP
Discount: 10%
Final: 41,175.00 EGP
```

**Payment Breakdown:**
```
Deposit:     70% = 28,822.50 EGP (Paid)
Production:  20% =  8,235.00 EGP (Paid)
Final:       10% =  4,117.50 EGP (Pending)
```

## Full Documentation

See [SEEDING_GUIDE.md](SEEDING_GUIDE.md) for:
- Advanced usage
- Architecture details
- Customization guide
- Troubleshooting
- Integration with workflows

---

⚡ **Pro Tip**: Run `python seed_database.py` after every migration to keep your dev database populated!
