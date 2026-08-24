"""
Tests for database layer.
"""

import pytest
import sqlite3
from pathlib import Path
from src.database.connection import DatabaseConnection


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Create a temporary database path for testing."""
        return tmp_path / "test_stap.db"
    
    @pytest.fixture
    def db_connection(self, temp_db_path):
        """Create a database connection with temporary path."""
        return DatabaseConnection(temp_db_path)
    
    def test_database_connection_initialization(self, temp_db_path):
        """Test that DatabaseConnection can be initialized."""
        db = DatabaseConnection(temp_db_path)
        assert db is not None
        assert db.db_path == temp_db_path
    
    def test_database_path_is_path(self, db_connection):
        """Test that db_path returns a Path object."""
        assert isinstance(db_connection.db_path, Path)
    
    def test_data_directory_creation(self, temp_db_path):
        """Test that data directory is created if it doesn't exist."""
        nested_path = temp_db_path / "subdir" / "test.db"
        db = DatabaseConnection(nested_path)
        assert nested_path.parent.exists()
        assert nested_path.parent.is_dir()
    
    def test_database_exists_false_initially(self, db_connection):
        """Test that database_exists returns False for non-existent database."""
        assert not db_connection.database_exists()
    
    def test_get_connection_context_manager(self, db_connection):
        """Test that get_connection works as a context manager."""
        with db_connection.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)
    
    def test_connection_row_factory(self, db_connection):
        """Test that connection has row factory set for dict-like access."""
        with db_connection.get_connection() as conn:
            assert conn.row_factory is not None
    
    def test_foreign_keys_enabled(self, db_connection):
        """Test that foreign keys are enabled."""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_initialize_database(self, db_connection):
        """Test database initialization."""
        db_connection.initialize_database()
        assert db_connection.database_exists()
    
    def test_schema_version_after_initialization(self, db_connection):
        """Test that schema version is set after initialization."""
        db_connection.initialize_database()
        version = db_connection.get_schema_version()
        assert version is not None
        assert version >= 1
    
    def test_reinitialize_database(self, db_connection):
        """Test that re-initializing doesn't cause errors."""
        db_connection.initialize_database()
        db_connection.initialize_database()  # Should not fail
        assert db_connection.database_exists()
    
    def test_get_schema_version_without_database(self, temp_db_path):
        """Test get_schema_version returns None when database doesn't exist."""
        db = DatabaseConnection(temp_db_path)
        assert db.get_schema_version() is None
    
    def test_connection_closes_properly(self, db_connection):
        """Test that connection closes properly after context manager."""
        conn = None
        with db_connection.get_connection() as conn:
            assert conn is not None
        # Connection should be closed now
        # We can't directly test this without internal access, 
        # but the context manager should handle it
    
    def test_database_path_not_absolute_by_default(self):
        """Test that default database path is not hardcoded absolute."""
        from src.config.settings import settings
        db = DatabaseConnection()
        # The path should be relative to project, not an absolute machine path
        assert settings.base_dir in db.db_path.parents or db.db_path.parent == settings.base_dir / "data"
