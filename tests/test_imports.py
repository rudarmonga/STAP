"""
Tests for core module imports and basic initialization.

These tests ensure that the application can be imported without errors
and that basic components are accessible.
"""

import pytest


def test_import_config():
    """Test that config module can be imported."""
    from src.config import settings
    assert settings is not None


def test_import_database():
    """Test that database module can be imported."""
    from src.database import connection
    assert connection is not None


def test_import_data():
    """Test that data module can be imported."""
    from src.data import synthetic
    assert synthetic is not None


def test_import_utils():
    """Test that utils module can be imported."""
    from src.utils import logger
    assert logger is not None


def test_import_ui():
    """Test that ui module can be imported."""
    from src.ui import app, pages
    assert app is not None
    assert pages is not None


def test_import_analytics():
    """Test that analytics module can be imported."""
    from src import analytics
    assert analytics is not None
    
    # Test that major analytics components are available
    from src.analytics import (
        AnalyticsEngine,
        analytics_engine,
        SellerAnalytics,
        MarketplaceAnalytics,
        RiskLevel,
        DateRange,
        TrustScoreWeights,
        DEFAULT_TRUST_SCORE_WEIGHTS
    )
    assert AnalyticsEngine is not None
    assert analytics_engine is not None
    assert SellerAnalytics is not None
    assert MarketplaceAnalytics is not None
    assert RiskLevel is not None
    assert DateRange is not None
    assert TrustScoreWeights is not None
    assert DEFAULT_TRUST_SCORE_WEIGHTS is not None


def test_import_reporting():
    """Test that reporting module can be imported."""
    from src import reporting
    assert reporting is not None


def test_settings_instance():
    """Test that settings instance is available."""
    from src.config.settings import settings
    assert settings is not None
    assert hasattr(settings, 'base_dir')
    assert hasattr(settings, 'database_path')


def test_database_instance():
    """Test that database instance is available."""
    from src.database.connection import db
    assert db is not None
    assert hasattr(db, 'db_path')
    assert hasattr(db, 'initialize_database')


def test_logger_function():
    """Test that logger function is available."""
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    assert logger is not None


def test_synthetic_generator_class():
    """Test that synthetic data generator class is available."""
    from src.data.synthetic import SyntheticDataGenerator
    assert SyntheticDataGenerator is not None
    generator = SyntheticDataGenerator()
    assert generator is not None


def test_marketplace_generator_class():
    """Test that marketplace data generator class is available."""
    from src.data.synthetic import MarketplaceDataGenerator
    assert MarketplaceDataGenerator is not None
    generator = MarketplaceDataGenerator()
    assert generator is not None


def test_page_functions():
    """Test that page rendering functions are available."""
    from src.ui.pages import (
        render_dashboard,
        render_seller_analytics,
        render_reports,
        render_settings
    )
    assert render_dashboard is not None
    assert render_seller_analytics is not None
    assert render_reports is not None
    assert render_settings is not None
