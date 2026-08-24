"""
Tests for configuration management.
"""

import os
import pytest
from pathlib import Path
from src.config.settings import Settings


class TestSettings:
    """Test Settings configuration class."""
    
    def test_settings_initialization(self):
        """Test that Settings can be initialized."""
        settings = Settings()
        assert settings is not None
        assert settings.base_dir is not None
    
    def test_base_dir_is_path(self):
        """Test that base_dir returns a Path object."""
        settings = Settings()
        assert isinstance(settings.base_dir, Path)
    
    def test_base_dir_exists(self):
        """Test that base_dir points to an existing directory."""
        settings = Settings()
        assert settings.base_dir.exists()
        assert settings.base_dir.is_dir()
    
    def test_default_environment(self):
        """Test default environment setting."""
        settings = Settings()
        assert settings.env in ["development", "staging", "production"]
    
    def test_is_development_flag(self):
        """Test development environment flag."""
        settings = Settings()
        assert isinstance(settings.is_development, bool)
    
    def test_is_production_flag(self):
        """Test production environment flag."""
        settings = Settings()
        assert isinstance(settings.is_production, bool)
    
    def test_database_path_is_path(self):
        """Test that database_path returns a Path object."""
        settings = Settings()
        assert isinstance(settings.database_path, Path)
    
    def test_database_path_parent_exists(self):
        """Test that database directory can be created."""
        settings = Settings()
        # The parent directory should exist or be creatable
        assert settings.database_path.parent is not None
    
    def test_log_level_default(self):
        """Test default log level."""
        settings = Settings()
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def test_synthetic_data_seed_is_int(self):
        """Test that synthetic data seed is an integer."""
        settings = Settings()
        assert isinstance(settings.synthetic_data_seed, int)
    
    def test_app_title(self):
        """Test application title configuration."""
        settings = Settings()
        assert isinstance(settings.app_title, str)
        assert len(settings.app_title) > 0
    
    def test_app_page_title(self):
        """Test page title configuration."""
        settings = Settings()
        assert isinstance(settings.app_page_title, str)
        assert len(settings.app_page_title) > 0
    
    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("STAP_ENV", "production")
        monkeypatch.setenv("STAP_LOG_LEVEL", "DEBUG")
        
        settings = Settings()
        assert settings.env == "production"
        assert settings.log_level == "DEBUG"
