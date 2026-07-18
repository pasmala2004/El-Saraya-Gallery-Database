"""
Reference (master) data seeders.

These seeders populate permanent catalog data required by the ERP.
They are safe to run in every environment, including production.

Business records (customers, quotations, jobs, payments, etc.) are
created through the application UI — never by reference seeders.
"""

from app.database.seeders.reference.product_category_seeder import (
    clear_categories,
    seed_categories,
)
from app.database.seeders.reference.product_seeder import (
    clear_products,
    seed_products,
)
from app.database.seeders.reference.run_reference import (
    clear_reference,
    seed_reference,
)

__all__ = [
    "seed_categories",
    "seed_products",
    "clear_categories",
    "clear_products",
    "seed_reference",
    "clear_reference",
]
