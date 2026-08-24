"""
Tests for analytics engine.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from src.analytics.engine import AnalyticsEngine
from src.analytics.config import RiskLevel, DateRange
from src.analytics.models import SellerAnalytics, MarketplaceAnalytics
from src.database.connection import DatabaseConnection


class TestAnalyticsEngine:
    """Test AnalyticsEngine class."""
    
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Create a temporary database path for testing."""
        return tmp_path / "test_analytics.db"
    
    @pytest.fixture
    def test_db(self, temp_db_path):
        """Create and initialize a test database."""
        db = DatabaseConnection(temp_db_path)
        db.initialize_database()
        
        # Insert test data
        with db.get_connection() as conn:
            # Insert test seller
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('TEST-001', 'Test Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            
            # Insert test orders
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES 
                ('ORD-001', 'TEST-001', '2024-01-01', 'Electronics', 'North America', 100.0, 3, 'completed'),
                ('ORD-002', 'TEST-001', '2024-01-15', 'Electronics', 'North America', 150.0, 5, 'completed'),
                ('ORD-003', 'TEST-001', '2024-02-01', 'Electronics', 'North America', 200.0, 7, 'cancelled')
            """)
            
            # Insert test ratings
            conn.execute("""
                INSERT INTO ratings (rating_id, seller_id, order_id, rating, rating_date)
                VALUES 
                ('RAT-001', 'TEST-001', 'ORD-001', 5, '2024-01-05'),
                ('RAT-002', 'TEST-001', 'ORD-002', 4, '2024-01-20')
            """)
            
            # Insert test reviews
            conn.execute("""
                INSERT INTO reviews (review_id, seller_id, order_id, review_date, review_text, sentiment, sentiment_score)
                VALUES 
                ('REV-001', 'TEST-001', 'ORD-001', '2024-01-05', 'Great product!', 'positive', 0.8),
                ('REV-002', 'TEST-001', 'ORD-002', '2024-01-20', 'Good value', 'positive', 0.6)
            """)
            
            conn.commit()
        
        return db
    
    @pytest.fixture
    def analytics_engine(self, test_db):
        """Create analytics engine with test database."""
        return AnalyticsEngine(test_db)
    
    def test_analytics_engine_initialization(self, analytics_engine):
        """Test analytics engine initialization."""
        assert analytics_engine is not None
        assert analytics_engine.db is not None
    
    def test_get_date_range_filters_all_time(self, analytics_engine):
        """Test date range filter for all time."""
        start, end = analytics_engine.get_date_range_filters("all_time")
        assert start is None
        assert end is None
    
    def test_get_date_range_filters_last_30_days(self, analytics_engine):
        """Test date range filter for last 30 days."""
        start, end = analytics_engine.get_date_range_filters("last_30_days")
        assert start is not None
        assert end is not None
        
        # Verify date difference is approximately 30 days
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        diff = (end_dt - start_dt).days
        assert 28 <= diff <= 32  # Allow some tolerance
    
    def test_get_date_range_filters_last_90_days(self, analytics_engine):
        """Test date range filter for last 90 days."""
        start, end = analytics_engine.get_date_range_filters("last_90_days")
        assert start is not None
        assert end is not None
        
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        diff = (end_dt - start_dt).days
        assert 88 <= diff <= 92
    
    def test_get_date_range_filters_custom(self, analytics_engine):
        """Test custom date range filter."""
        start, end = analytics_engine.get_date_range_filters("custom", "2024-01-01", "2024-01-31")
        assert start == "2024-01-01"
        assert end == "2024-01-31"
    
    def test_get_date_range_filters_custom_invalid(self, analytics_engine):
        """Test custom date range with invalid format."""
        start, end = analytics_engine.get_date_range_filters("custom", "invalid", "2024-01-31")
        assert start is None
        assert end is None
    
    def test_get_date_range_filters_custom_missing(self, analytics_engine):
        """Test custom date range with missing dates."""
        start, end = analytics_engine.get_date_range_filters("custom", None, "2024-01-31")
        assert start is None
        assert end is None
    
    def test_calculate_seller_analytics(self, analytics_engine):
        """Test calculating seller analytics."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert isinstance(analytics, SellerAnalytics)
        assert analytics.seller_id == "TEST-001"
        assert analytics.seller_name == "Test Store"
        assert analytics.category == "Electronics"
        assert analytics.region == "North America"
        assert analytics.status == "active"
    
    def test_seller_analytics_order_metrics(self, analytics_engine):
        """Test order metrics calculation."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert analytics.order_metrics.total_orders == 3
        assert analytics.order_metrics.completed_orders == 2
        assert analytics.order_metrics.cancelled_orders == 1
        assert analytics.order_metrics.total_revenue == 450.0
        assert analytics.order_metrics.average_order_value == 150.0
        assert analytics.order_metrics.completion_rate == pytest.approx(66.67, rel=0.1)
    
    def test_seller_analytics_rating_metrics(self, analytics_engine):
        """Test rating metrics calculation."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert analytics.rating_metrics.total_ratings == 2
        assert analytics.rating_metrics.average_rating == 4.5
        assert analytics.rating_metrics.rating_distribution[5] == 1
        assert analytics.rating_metrics.rating_distribution[4] == 1
    
    def test_seller_analytics_review_metrics(self, analytics_engine):
        """Test review metrics calculation."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert analytics.review_metrics.total_reviews == 2
        assert analytics.review_metrics.positive_reviews == 2
        assert analytics.review_metrics.negative_reviews == 0
        assert analytics.review_metrics.average_sentiment_score == 0.7
    
    def test_seller_analytics_trust_score(self, analytics_engine):
        """Test Trust Score calculation."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert 0 <= analytics.trust_score <= 100
        assert analytics.trust_score_components is not None
        assert analytics.risk_level in [RiskLevel.HEALTHY, RiskLevel.MONITOR, RiskLevel.HIGH_RISK]
    
    def test_seller_analytics_data_sufficiency(self, analytics_engine):
        """Test data sufficiency check."""
        analytics = analytics_engine.calculate_seller_analytics("TEST-001")
        
        assert isinstance(analytics.has_sufficient_data, bool)
        assert isinstance(analytics.data_sufficiency_details, dict)
    
    def test_calculate_seller_analytics_not_found(self, analytics_engine):
        """Test calculating analytics for non-existent seller."""
        with pytest.raises(ValueError):
            analytics_engine.calculate_seller_analytics("NONEXISTENT")
    
    def test_calculate_marketplace_analytics(self, analytics_engine):
        """Test calculating marketplace analytics."""
        analytics = analytics_engine.calculate_marketplace_analytics()
        
        assert isinstance(analytics, MarketplaceAnalytics)
        assert analytics.total_sellers == 1
        assert analytics.active_sellers == 1
        assert analytics.total_orders == 3
    
    def test_marketplace_analytics_with_date_filter(self, analytics_engine):
        """Test marketplace analytics with date filter."""
        analytics = analytics_engine.calculate_marketplace_analytics("last_30_days")
        
        assert isinstance(analytics, MarketplaceAnalytics)
        # With last 30 days filter, should have no orders since test data is from 2024
        assert analytics.total_orders == 0
    
    def test_rank_sellers_by_trust_score(self, analytics_engine):
        """Test ranking sellers by Trust Score."""
        ranked = analytics_engine.rank_sellers_by_trust_score()
        
        assert isinstance(ranked, list)
        assert len(ranked) == 1
        assert ranked[0].seller_id == "TEST-001"
    
    def test_rank_sellers_with_limit(self, analytics_engine):
        """Test ranking sellers with limit."""
        ranked = analytics_engine.rank_sellers_by_trust_score(limit=1)
        
        assert len(ranked) <= 1
    
    def test_rank_sellers_sorting(self, analytics_engine):
        """Test that sellers are sorted by Trust Score."""
        # Add another seller with different performance
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('TEST-002', 'Another Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES ('ORD-004', 'TEST-002', '2024-01-01', 'Electronics', 'North America', 50.0, 10, 'cancelled')
            """)
            conn.execute("""
                INSERT INTO ratings (rating_id, seller_id, order_id, rating, rating_date)
                VALUES ('RAT-003', 'TEST-002', 'ORD-004', 1, '2024-01-05')
            """)
            conn.commit()
        
        ranked = analytics_engine.rank_sellers_by_trust_score()
        
        assert len(ranked) == 2
        # First seller should have higher trust score (better performance)
        assert ranked[0].trust_score >= ranked[1].trust_score
    
    def test_calculate_historical_analytics(self, analytics_engine):
        """Test historical analytics calculation."""
        historical = analytics_engine.calculate_historical_analytics(
            entity_id="TEST-001",
            entity_type="seller",
            metric_name="trust_score",
            aggregation_period="month"
        )
        
        assert historical.entity_id == "TEST-001"
        assert historical.entity_type == "seller"
        assert historical.metric_name == "trust_score"
        assert historical.aggregation_period == "month"


class TestAnalyticsEngineEdgeCases:
    """Test analytics engine edge cases."""
    
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Create a temporary database path for testing."""
        return tmp_path / "test_edge_cases.db"
    
    @pytest.fixture
    def empty_db(self, temp_db_path):
        """Create an empty test database."""
        db = DatabaseConnection(temp_db_path)
        db.initialize_database()
        return db
    
    @pytest.fixture
    def analytics_engine(self, empty_db):
        """Create analytics engine with empty database."""
        return AnalyticsEngine(empty_db)
    
    def test_empty_marketplace_analytics(self, analytics_engine):
        """Test marketplace analytics with no data."""
        analytics = analytics_engine.calculate_marketplace_analytics()
        
        assert analytics.total_sellers == 0
        assert analytics.total_orders == 0
        assert analytics.total_ratings == 0
        assert analytics.total_reviews == 0
    
    def test_rank_sellers_empty(self, analytics_engine):
        """Test ranking sellers with no sellers."""
        ranked = analytics_engine.rank_sellers_by_trust_score()
        
        assert isinstance(ranked, list)
        assert len(ranked) == 0
    
    def test_seller_with_no_orders(self, analytics_engine):
        """Test analytics for seller with no orders."""
        # Add seller with no orders
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('EMPTY-001', 'Empty Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.commit()
        
        analytics = analytics_engine.calculate_seller_analytics("EMPTY-001")
        
        assert analytics.order_metrics.total_orders == 0
        assert analytics.order_metrics.completion_rate == 0.0
        assert analytics.return_metrics.return_rate == 0.0
    
    def test_seller_with_no_ratings(self, analytics_engine):
        """Test analytics for seller with no ratings."""
        # Add seller with orders but no ratings
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('NO-RAT-001', 'No Ratings Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES ('ORD-NO-RAT', 'NO-RAT-001', '2024-01-01', 'Electronics', 'North America', 100.0, 3, 'completed')
            """)
            conn.commit()
        
        analytics = analytics_engine.calculate_seller_analytics("NO-RAT-001")
        
        assert analytics.rating_metrics.total_ratings == 0
        assert analytics.rating_metrics.average_rating == 0.0
        # Trust score should handle missing ratings gracefully
        assert 0 <= analytics.trust_score <= 100
    
    def test_seller_with_no_reviews(self, analytics_engine):
        """Test analytics for seller with no reviews."""
        # Add seller with orders but no reviews
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('NO-REV-001', 'No Reviews Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES ('ORD-NO-REV', 'NO-REV-001', '2024-01-01', 'Electronics', 'North America', 100.0, 3, 'completed')
            """)
            conn.commit()
        
        analytics = analytics_engine.calculate_seller_analytics("NO-REV-001")
        
        assert analytics.review_metrics.total_reviews == 0
        assert analytics.review_metrics.average_sentiment_score == 0.0
    
    def test_trust_score_boundary_values(self, analytics_engine):
        """Test Trust Score at boundary values."""
        # Create a seller with perfect metrics
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('PERFECT-001', 'Perfect Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES ('ORD-PERFECT', 'PERFECT-001', '2024-01-01', 'Electronics', 'North America', 100.0, 1, 'completed')
            """)
            conn.execute("""
                INSERT INTO ratings (rating_id, seller_id, order_id, rating, rating_date)
                VALUES ('RAT-PERFECT', 'PERFECT-001', 'ORD-PERFECT', 5, '2024-01-05')
            """)
            conn.execute("""
                INSERT INTO reviews (review_id, seller_id, order_id, review_date, review_text, sentiment, sentiment_score)
                VALUES ('REV-PERFECT', 'PERFECT-001', 'ORD-PERFECT', '2024-01-05', 'Perfect!', 'positive', 1.0)
            """)
            conn.commit()
        
        analytics = analytics_engine.calculate_seller_analytics("PERFECT-001")
        
        # Perfect seller should have high trust score
        assert analytics.trust_score >= 80.0
        assert analytics.risk_level == RiskLevel.HEALTHY
    
    def test_trust_score_poor_performance(self, analytics_engine):
        """Test Trust Score for poor performing seller."""
        # Create a seller with poor metrics
        with analytics_engine.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO sellers (seller_id, seller_name, category, region, join_date, status)
                VALUES ('POOR-001', 'Poor Store', 'Electronics', 'North America', '2023-01-01', 'active')
            """)
            conn.execute("""
                INSERT INTO orders (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
                VALUES ('ORD-POOR', 'POOR-001', '2024-01-01', 'Electronics', 'North America', 100.0, 15, 'cancelled')
            """)
            conn.execute("""
                INSERT INTO ratings (rating_id, seller_id, order_id, rating, rating_date)
                VALUES ('RAT-POOR', 'POOR-001', 'ORD-POOR', 1, '2024-01-05')
            """)
            conn.execute("""
                INSERT INTO reviews (review_id, seller_id, order_id, review_date, review_text, sentiment, sentiment_score)
                VALUES ('REV-POOR', 'POOR-001', 'ORD-POOR', '2024-01-05', 'Terrible!', 'negative', -1.0)
            """)
            conn.commit()
        
        analytics = analytics_engine.calculate_seller_analytics("POOR-001")
        
        # Poor seller should have low trust score
        assert analytics.trust_score <= 60.0
        assert analytics.risk_level in [RiskLevel.MONITOR, RiskLevel.HIGH_RISK]