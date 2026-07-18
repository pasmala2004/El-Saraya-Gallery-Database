# Database Seeding Guide

## Principles

This ERP is a production system. Seeding exists to load **reference (master) data** only.

| Data type | Examples | How it enters the database |
|-----------|----------|----------------------------|
| **Reference / master** | Product categories, products | Seeders (safe for every environment) |
| **Business** | Customers, quotations, jobs, measurements, payments, activity logs, reports | ERP UI / application APIs only |
| **Demo** | Sample business rows for local UI testing | Explicit development command only — never production |

After a normal seed run, the database must contain **no** fake customers, quotations, jobs, payments, measurements, activity logs, or reports.

Production databases must never contain demo business records.

---

## Package layout

```
app/database/seeders/
├── reference/                 # Permanent master data
│   ├── product_category_seeder.py
│   ├── product_seeder.py
│   └── run_reference.py
├── development/               # Opt-in demo data (local only)
│   ├── demo_data.py
│   └── run_demo.py
└── run_all.py                 # Default entry → reference only
```

`run_all` does **not** import the development package.

---

## Reference seeding (default)

Seeds permanent catalog data:

1. Product categories: Windows, Doors, Kitchens, Shower Cabins, Smart Locks
2. Products: only when `PRODUCTS_BY_CATEGORY` in `product_seeder.py` is filled with the real catalog

Until the catalog is finalized, the product seeder inserts nothing (TODO markers in code).

```bash
# Preferred module entrypoints
python -m app.database.seeders.run_all
python -m app.database.seeders.reference.run_reference

# Convenience CLI (same default behaviour)
python seed_database.py
```

Clear reference catalog only:

```bash
python -m app.database.seeders.reference.run_reference --clear
python seed_database.py --clear
```

Clearing products fails if quotation line items still reference them (`ON DELETE RESTRICT`).

---

## Development demo seeding (opt-in)

Use only on local developer databases when you need sample business rows for UI testing.

```bash
python -m app.database.seeders.development.run_demo --yes
python seed_database.py --demo --yes
```

Clear business tables (keeps categories/products):

```bash
python -m app.database.seeders.development.run_demo --clear --yes
python seed_database.py --demo --clear --yes
```

Without `--yes`, the runner asks you to type `demo` to confirm.

Demo seeding:

- Never runs from `run_all`
- Requires at least one real product in the catalog (it does not invent fake products)
- Must not be executed against production

---

## Finalizing the product catalog

Edit `app/database/seeders/reference/product_seeder.py` and populate `PRODUCTS_BY_CATEGORY` with production SKUs only, for example:

```python
PRODUCTS_BY_CATEGORY = {
    "Windows": ["Sliding Window", "Casement Window"],
    "Doors": ["Sliding Door", "French Door"],
    "Kitchens": [],
    "Shower Cabins": [],
    "Smart Locks": [],
}
```

Then re-run reference seeding. Do not add placeholder or randomly generated product names.

---

## Prerequisites

```bash
pip install -r requirements.txt
# Configure DATABASE_URL / DATABASE_URL_SYNC in .env
alembic upgrade head
```

---

## Verification after reference seed

```sql
SELECT count(*) FROM product_categories;  -- expect 5
SELECT count(*) FROM products;            -- 0 until catalog is finalized
SELECT count(*) FROM customers;           -- expect 0
SELECT count(*) FROM quotations;          -- expect 0
SELECT count(*) FROM jobs;                -- expect 0
```

---

## What not to do

- Do not seed customers, quotations, jobs, payments, or measurements in production
- Do not import `app.database.seeders.development` from reference runners
- Do not treat demo data as a substitute for UI workflows
