"""
Main Seeder Orchestrator.

Executes all seeders in the correct order to populate the database
with realistic ERP data.

Usage:
    python -m app.database.seeders.run_all
"""
import asyncio
import time

from app.core.logging import configure_logging, get_logger
from app.database.seeders.activity_log_seeder import seed_activity_logs
from app.database.seeders.category_seeder import seed_categories
from app.database.seeders.customer_seeder import seed_customers
from app.database.seeders.job_seeder import seed_jobs
from app.database.seeders.measurement_seeder import seed_measurements
from app.database.seeders.payment_seeder import seed_payments
from app.database.seeders.product_seeder import seed_products
from app.database.seeders.quotation_seeder import seed_quotations
from app.db.session import AsyncSessionLocal

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def seed_all() -> None:
    """
    Run all seeders in the correct dependency order.
    
    Seeding order:
    1. Product Categories (no dependencies)
    2. Products (depends on categories)
    3. Customers (no dependencies)
    4. Quotations & Quotation Items (depends on customers and products)
    5. Jobs (depends on approved quotations)
    6. Payments (depends on jobs)
    7. Measurements & Measurement Items (depends on jobs)
    8. Activity Logs (depends on jobs)
    
    This operation is idempotent - running multiple times will not duplicate data.
    """
    start_time = time.time()
    
    logger.info("=" * 70)
    logger.info("STARTING DATABASE SEEDING")
    logger.info("=" * 70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Step 1: Seed Product Categories
            logger.info("\n[1/8] Seeding Product Categories...")
            categories_map = await seed_categories(session)
            logger.info(f"✓ Categories: {len(categories_map)} total")
            
            # Step 2: Seed Products
            logger.info("\n[2/8] Seeding Products...")
            products = await seed_products(session, categories_map)
            logger.info(f"✓ Products: {len(products)} total")
            
            # Step 3: Seed Customers
            logger.info("\n[3/8] Seeding Customers...")
            customers = await seed_customers(session)
            logger.info(f"✓ Customers: {len(customers)} total")
            
            # Step 4: Seed Quotations and Quotation Items
            logger.info("\n[4/8] Seeding Quotations and Items...")
            quotations = await seed_quotations(session, customers, products)
            logger.info(f"✓ Quotations: {len(quotations)} total")
            
            # Step 5: Seed Jobs (only for approved quotations)
            logger.info("\n[5/8] Seeding Jobs...")
            jobs = await seed_jobs(session, quotations)
            logger.info(f"✓ Jobs: {len(jobs)} total")
            
            # Step 6: Seed Payments (3 per job: 70% Deposit, 20% Production, 10% Final)
            logger.info("\n[6/8] Seeding Payments...")
            payments = await seed_payments(session, jobs)
            logger.info(f"✓ Payments: {len(payments)} total")
            
            # Step 7: Seed Measurements and Measurement Items
            logger.info("\n[7/8] Seeding Measurements and Items...")
            measurements = await seed_measurements(session, jobs)
            logger.info(f"✓ Measurements: {len(measurements)} total")
            
            # Step 8: Seed Activity Logs
            logger.info("\n[8/8] Seeding Activity Logs...")
            activity_logs = await seed_activity_logs(session, jobs)
            logger.info(f"✓ Activity Logs: {len(activity_logs)} total")
            
            # Summary
            elapsed_time = time.time() - start_time
            logger.info("\n" + "=" * 70)
            logger.info("DATABASE SEEDING COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            logger.info("\nSummary:")
            logger.info(f"  • Product Categories: {len(categories_map)}")
            logger.info(f"  • Products: {len(products)}")
            logger.info(f"  • Customers: {len(customers)}")
            logger.info(f"  • Quotations: {len(quotations)}")
            logger.info(f"  • Jobs: {len(jobs)}")
            logger.info(f"  • Payments: {len(payments)}")
            logger.info(f"  • Measurements: {len(measurements)}")
            logger.info(f"  • Activity Logs: {len(activity_logs)}")
            logger.info(f"\nTime elapsed: {elapsed_time:.2f} seconds")
            logger.info("\n✅ Database is now populated with realistic ERP data!")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"\n❌ Seeding failed with error: {e}", exc_info=True)
            raise


async def clear_all() -> None:
    """
    Clear all seeded data (for testing purposes).
    
    ⚠️ WARNING: This will delete ALL data from the database!
    Use only in development/testing environments.
    """
    logger.warning("=" * 70)
    logger.warning("⚠️  CLEARING ALL DATA FROM DATABASE")
    logger.warning("=" * 70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Import clear functions
            from app.database.seeders.activity_log_seeder import clear_activity_logs
            from app.database.seeders.category_seeder import clear_categories
            from app.database.seeders.customer_seeder import clear_customers
            from app.database.seeders.job_seeder import clear_jobs
            from app.database.seeders.measurement_seeder import clear_measurements
            from app.database.seeders.payment_seeder import clear_payments
            from app.database.seeders.product_seeder import clear_products
            from app.database.seeders.quotation_seeder import clear_quotations
            
            # Clear in reverse order (respecting foreign key constraints)
            await clear_activity_logs(session)
            await clear_measurements(session)
            await clear_payments(session)
            await clear_jobs(session)
            await clear_quotations(session)
            await clear_customers(session)
            await clear_products(session)
            await clear_categories(session)
            
            logger.warning("✓ All data cleared successfully")
            logger.warning("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Clearing failed with error: {e}", exc_info=True)
            raise


def main() -> None:
    """Main entry point for the seeder."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        # Clear mode
        asyncio.run(clear_all())
    else:
        # Seed mode (default)
        asyncio.run(seed_all())


if __name__ == "__main__":
    main()
