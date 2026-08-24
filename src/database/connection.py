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
        
        This method creates the database file and complete STAP schema if it doesn't exist.
        """
        logger.info(f"Initializing database at: {self._db_path}")
        
        with self.get_connection() as conn:
            # Create schema version table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check current schema version
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            current_version = cursor.fetchone()[0]
            
            if current_version is None or current_version < 2:
                self._create_stap_schema(conn)
                conn.execute("INSERT INTO schema_version (version) VALUES (2)")
                conn.commit()
                logger.info("Database schema initialized to version 2")
            else:
                logger.info(f"Database schema already exists at version {current_version}")
    
    def _create_stap_schema(self, conn) -> None:
        """Create the complete STAP database schema."""
        logger.info("Creating STAP database schema")
        
        # Sellers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                seller_id TEXT PRIMARY KEY,
                seller_name TEXT NOT NULL,
                category TEXT NOT NULL,
                region TEXT NOT NULL,
                join_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('active', 'inactive', 'suspended'))
            )
        """)
        
        # Orders table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                order_date TEXT NOT NULL,
                category TEXT NOT NULL,
                region TEXT NOT NULL,
                order_value REAL NOT NULL CHECK(order_value >= 0),
                delivery_days INTEGER CHECK(delivery_days >= 0),
                status TEXT NOT NULL CHECK(status IN ('completed', 'cancelled', 'pending', 'refunded')),
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        # Returns table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                return_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                return_date TEXT NOT NULL,
                return_reason TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('approved', 'rejected', 'pending')),
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        # Ratings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                order_id TEXT,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                rating_date TEXT NOT NULL,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)
        
        # Reviews table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                order_id TEXT,
                review_date TEXT NOT NULL,
                review_text TEXT NOT NULL,
                sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')),
                sentiment_score REAL CHECK(sentiment_score BETWEEN -1 AND 1),
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_seller_id ON orders(seller_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_category ON orders(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_returns_seller_id ON returns(seller_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_returns_order_id ON returns(order_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_seller_id ON ratings(seller_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_rating_date ON ratings(rating_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_seller_id ON reviews(seller_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment)")
        
        logger.info("STAP schema created successfully")
    
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
    
    def reset_database(self) -> None:
        """
        Reset the database by dropping all tables and reinitializing schema.
        
        This is useful for development and testing when you want a fresh start.
        """
        logger.warning(f"Resetting database at: {self._db_path}")
        
        with self.get_connection() as conn:
            # Drop all tables in correct order (respecting foreign keys)
            conn.execute("DROP TABLE IF EXISTS reviews")
            conn.execute("DROP TABLE IF EXISTS ratings")
            conn.execute("DROP TABLE IF EXISTS returns")
            conn.execute("DROP TABLE IF EXISTS orders")
            conn.execute("DROP TABLE IF EXISTS sellers")
            conn.execute("DROP TABLE IF EXISTS schema_version")
            conn.commit()
        
        # Reinitialize schema
        self.initialize_database()
        logger.info("Database reset successfully")


# Global database connection instance
db = DatabaseConnection()
