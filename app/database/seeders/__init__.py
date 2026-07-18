"""
Database seeders.

Each seeder module populates a specific table with reference or
development data. Seeders are run in dependency order from the
top-level seed runner.

Usage:
    # Seed the entire database
    python -m app.database.seeders.run_all
    
    # Clear all seeded data
    python -m app.database.seeders.run_all --clear
    
    # Use individual seeders programmatically
    from app.database.seeders import seed_categories, seed_products
"""

# Main orchestrator
from app.database.seeders.run_all import clear_all, seed_all

# Individual seeders
from app.database.seeders.activity_log_seeder import (
    clear_activity_logs,
    seed_activity_logs,
)
from app.database.seeders.category_seeder import clear_categories, seed_categories
from app.database.seeders.customer_seeder import clear_customers, seed_customers
from app.database.seeders.job_seeder import clear_jobs, seed_jobs
from app.database.seeders.measurement_seeder import (
    clear_measurements,
    seed_measurements,
)
from app.database.seeders.payment_seeder import clear_payments, seed_payments
from app.database.seeders.product_seeder import clear_products, seed_products
from app.database.seeders.quotation_seeder import clear_quotations, seed_quotations

__all__ = [
    # Main orchestrator
    "seed_all",
    "clear_all",
    # Individual seeders
    "seed_categories",
    "seed_products",
    "seed_customers",
    "seed_quotations",
    "seed_jobs",
    "seed_payments",
    "seed_measurements",
    "seed_activity_logs",
    # Clear functions
    "clear_categories",
    "clear_products",
    "clear_customers",
    "clear_quotations",
    "clear_jobs",
    "clear_payments",
    "clear_measurements",
    "clear_activity_logs",
]
