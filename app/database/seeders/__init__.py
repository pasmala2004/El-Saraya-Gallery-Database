"""
Database seeders.

Reference seeders (default / production-safe)
---------------------------------------------
Populate permanent master data only (product categories and products).

    python -m app.database.seeders.run_all
    python -m app.database.seeders.reference.run_reference

Development demo seeders (opt-in only)
--------------------------------------
Optional sample business records for local UI testing.
Never run automatically and never use in production.

    python -m app.database.seeders.development.run_demo --yes
"""

from app.database.seeders.run_all import clear_all, seed_all
from app.database.seeders.reference import (
    clear_categories,
    clear_products,
    clear_reference,
    seed_categories,
    seed_products,
    seed_reference,
)

__all__ = [
    "seed_all",
    "clear_all",
    "seed_reference",
    "clear_reference",
    "seed_categories",
    "seed_products",
    "clear_categories",
    "clear_products",
]
