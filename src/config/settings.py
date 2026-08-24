"""
Configuration management for STAP.

This module handles application configuration with support for:
- Environment variables
- Safe defaults
- Runtime-relative paths
- Environment-specific settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        self._base_dir: Path = self._get_base_dir()
        self._env: str = os.getenv("STAP_ENV", "development")
    
    def _get_base_dir(self) -> Path:
        """Get the base directory of the project."""
        # Start from current file and go up to project root
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent
    
    @property
    def base_dir(self) -> Path:
        """Base directory of the project."""
        return self._base_dir
    
    @property
    def env(self) -> str:
        """Current environment (development, staging, production)."""
        return self._env
    
    @property
    def is_development(self) -> bool:
        """Whether running in development mode."""
        return self._env == "development"
    
    @property
    def is_production(self) -> bool:
        """Whether running in production mode."""
        return self._env == "production"
    
    @property
    def database_path(self) -> Path:
        """Path to the SQLite database file."""
        db_path = os.getenv("STAP_DATABASE_PATH")
        if db_path:
            return Path(db_path).resolve()
        
        # Default: data directory in project root
        data_dir = self._base_dir / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir / "stap.db"
    
    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv("STAP_LOG_LEVEL", "INFO")
    
    @property
    def log_file(self) -> Optional[Path]:
        """Path to log file, if configured."""
        log_path = os.getenv("STAP_LOG_FILE")
        if log_path:
            return Path(log_path).resolve()
        return None
    
    @property
    def synthetic_data_seed(self) -> int:
        """Seed for reproducible synthetic data generation."""
        seed_str = os.getenv("STAP_SYNTHETIC_DATA_SEED", "42")
        return int(seed_str)
    
    @property
    def app_title(self) -> str:
        """Application title for Streamlit."""
        return os.getenv("STAP_APP_TITLE", "STAP - Seller Trust Analytics Platform")
    
    @property
    def app_page_title(self) -> str:
        """Browser page title."""
        return os.getenv("STAP_PAGE_TITLE", "STAP Analytics")


# Global settings instance
settings = Settings()
