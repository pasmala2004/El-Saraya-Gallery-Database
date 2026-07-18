"""
Development demo data runner.

Seeds optional business demo records for local UI testing only.
Never run against production databases.

Usage:
    python -m app.database.seeders.development.run_demo --yes
    python -m app.database.seeders.development.run_demo --clear --yes
"""
import argparse
import asyncio
import sys

from app.core.logging import configure_logging, get_logger
from app.database.seeders.development.demo_data import (
    clear_demo_business_data,
    seed_demo_data,
)
from app.db.session import AsyncSessionLocal

configure_logging()
logger = get_logger(__name__)


async def run_demo(*, clear: bool = False) -> None:
    """Execute demo seed or clear inside a single session."""
    async with AsyncSessionLocal() as session:
        if clear:
            await clear_demo_business_data(session)
        else:
            await seed_demo_data(session)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Seed or clear DEVELOPMENT demo business data. "
            "Do not use in production."
        ),
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear business tables (customers, quotations, jobs, etc.). "
        "Leaves reference catalog intact.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation (required for non-interactive use).",
    )
    args = parser.parse_args()

    if not args.yes:
        action = "CLEAR business tables" if args.clear else "SEED demo business data"
        print(
            f"\nWARNING: About to {action}.\n"
            "This is for local development only. Production must never run this.\n"
        )
        answer = input("Type 'demo' to continue: ").strip()
        if answer != "demo":
            print("Aborted.")
            sys.exit(1)

    asyncio.run(run_demo(clear=args.clear))


if __name__ == "__main__":
    main()
