#!/usr/bin/env python3
"""
Database initialization script for STAP.

Run this script to create and initialize the SQLite database:
    python scripts/init_db.py [--reset]

Options:
    --reset: Reset the database by dropping all tables and reinitializing
"""

import sys
import argparse
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.utils.logger import setup_logging, get_logger

# Ensure logging is set up
setup_logging()
logger = get_logger(__name__)


def main():
    """Initialize the database."""
    parser = argparse.ArgumentParser(description="Initialize STAP database")
    parser.add_argument("--reset", action="store_true", help="Reset database before initialization")
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            logger.warning("Resetting database...")
            db.reset_database()
        else:
            logger.info("Starting database initialization...")
            db.initialize_database()
        
        logger.info(f"Database initialized successfully at: {db.db_path}")
        logger.info(f"Schema version: {db.get_schema_version()}")
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
