#!/usr/bin/env python3
"""
Database initialization script for STAP.

Run this script to create and initialize the SQLite database:
    python scripts/init_db.py
"""

import sys
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
    logger.info("Starting database initialization...")
    
    try:
        db.initialize_database()
        logger.info(f"Database initialized successfully at: {db.db_path}")
        logger.info(f"Schema version: {db.get_schema_version()}")
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
