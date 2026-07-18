"""
Default seeder entrypoint.

Runs reference (master) data only. Does not import or execute demo seeders.

Usage:
    python -m app.database.seeders.run_all
    python -m app.database.seeders.run_all --clear
"""
import asyncio

from app.core.logging import configure_logging, get_logger
from app.database.seeders.reference.run_reference import (
    clear_reference,
    seed_reference,
)

configure_logging()
logger = get_logger(__name__)


async def seed_all() -> None:
    """Seed reference data only (production-safe default)."""
    logger.info("run_all: seeding reference data only (demo data is not included)")
    await seed_reference()


async def clear_all() -> None:
    """Clear reference data only."""
    logger.warning("run_all: clearing reference data only")
    await clear_reference()


def main() -> None:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_all())
    else:
        asyncio.run(seed_all())


if __name__ == "__main__":
    main()
