#!/usr/bin/env python3
"""
Database seeding CLI (reference data by default).

Usage:
    python seed_database.py
    python seed_database.py --clear
    python seed_database.py --demo --yes
    python seed_database.py --demo --clear --yes
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.seeders import clear_all, seed_all


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Seed permanent reference (master) data by default. "
            "Demo business data is opt-in for local development only."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed_database.py                 Seed reference data only
  python seed_database.py --clear         Clear reference data
  python seed_database.py --demo --yes    Seed local demo business data
  python seed_database.py --demo --clear --yes

Notes:
  • Default seeding never creates customers, quotations, jobs, or payments.
  • Business data should be entered through the ERP UI.
  • Demo seeding must never be used against production databases.
        """,
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear data (reference by default, or business tables with --demo).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Operate on development demo business data (opt-in; not for production).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (required for non-interactive demo runs).",
    )
    args = parser.parse_args()

    if args.demo:
        from app.database.seeders.development.run_demo import run_demo

        if not args.yes:
            action = "CLEAR business tables" if args.clear else "SEED demo business data"
            print(
                f"\nWARNING: About to {action}.\n"
                "Development only — never run against production.\n"
            )
            answer = input("Type 'demo' to continue: ").strip()
            if answer != "demo":
                print("Aborted.")
                sys.exit(0)

        asyncio.run(run_demo(clear=args.clear))
        return

    if args.clear:
        print("\nWARNING: This will delete reference catalog data (products/categories).")
        response = input("Continue? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)
        asyncio.run(clear_all())
        return

    asyncio.run(seed_all())


if __name__ == "__main__":
    main()
