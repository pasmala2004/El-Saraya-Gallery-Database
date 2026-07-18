#!/usr/bin/env python3
"""
Database Seeding CLI.

A convenience script to seed the database with realistic ERP data.

Usage:
    # Seed the database
    python seed_database.py
    
    # Clear all data (⚠️ dangerous in production!)
    python seed_database.py --clear
    
    # Show help
    python seed_database.py --help
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.seeders import clear_all, seed_all


def main() -> None:
    """Parse arguments and execute seeding operations."""
    parser = argparse.ArgumentParser(
        description="Seed the database with realistic ERP data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed_database.py              Seed the database with sample data
  python seed_database.py --clear      Clear all seeded data (⚠️ dangerous!)
  
Notes:
  • Seeding is idempotent - running multiple times will not duplicate data
  • The --clear operation is destructive and should only be used in development
  • Ensure database connection is configured in .env before running
        """,
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all seeded data from the database (⚠️ WARNING: destructive operation!)",
    )
    
    args = parser.parse_args()
    
    if args.clear:
        # Confirm before clearing
        print("\n⚠️  WARNING: This will DELETE ALL DATA from the database!")
        response = input("Are you sure you want to continue? [y/N]: ")
        
        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)
        
        asyncio.run(clear_all())
    else:
        # Default: seed the database
        asyncio.run(seed_all())


if __name__ == "__main__":
    main()
