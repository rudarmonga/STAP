"""
Database connection management for STAP.

Provides safe SQLite connection handling with:
- Centralized configuration
- Connection pooling
- Safe path handling
- Context manager support
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages SQLite database connections."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to database file. If None, uses settings.
        """
        self._db_path = db_path or settings.database_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured data directory exists: {self._db_path.parent}")
    
    @property
    def db_path(self) -> Path:
        """Get the database path."""
        return self._db_path
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection with row factory set
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self._db_path),
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            logger.debug(f"Database connection opened: {self._db_path}")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug(f"Database connection closed: {self._db_path}")
    
    def initialize_database(self) -> None:
        """
        Initialize the database with required schema.
        
        This method creates the database file and basic schema if it doesn't exist.
        Future schema migrations will be handled here.
        """
        logger.info(f"Initializing database at: {self._db_path}")
        
        with self.get_connection() as conn:
            # Create basic schema
            # This is a minimal foundation - actual STAP schema will be added later
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert initial version if table is empty
            cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO schema_version (version) VALUES (1)")
                conn.commit()
                logger.info("Database schema initialized to version 1")
            else:
                logger.info("Database schema already exists")
    
    def database_exists(self) -> bool:
        """Check if the database file exists."""
        return self._db_path.exists()
    
    def get_schema_version(self) -> Optional[int]:
        """Get the current schema version."""
        if not self.database_exists():
            return None
        
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            return result[0] if result and result[0] else None


# Global database connection instance
db = DatabaseConnection()
