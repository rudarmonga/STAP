"""
Tests for analytics configuration.
"""

import pytest
from src.analytics.config import (
    RiskLevel,
    DateRange,
    TrustScoreWeights,
    RiskThresholds,
    DataSufficiencyThresholds,
    DEFAULT_TRUST_SCORE_WEIGHTS,
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_DATA_SUFFICIENCY,
    get_trust_score_config
)


class TestRiskLevel:
    """Test RiskLevel enum."""
    
    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.HEALTHY.value == "healthy"
        assert RiskLevel.MONITOR.value == "monitor"
        assert RiskLevel.HIGH_RISK.value == "high_risk"
    
    def test_risk_level_count(self):
        """Test RiskLevel has correct number of values."""
        assert len(RiskLevel) == 3


class TestDateRange:
    """Test DateRange enum."""
    
    def test_date_range_values(self):
        """Test DateRange enum values."""
        assert DateRange.ALL_TIME.value == "all_time"
        assert DateRange.LAST_30_DAYS.value == "last_30_days"
        assert DateRange.LAST_90_DAYS.value == "last_90_days"
        assert DateRange.LAST_6_MONTHS.value == "last_6_months"
        assert DateRange.LAST_1_YEAR.value == "last_1_year"
        assert DateRange.LAST_3_YEARS.value == "last_3_years"
        assert DateRange.LAST_5_YEARS.value == "last_5_years"
        assert DateRange.CUSTOM.value == "custom"
    
    def test_date_range_count(self):
        """Test DateRange has correct number of values."""
        assert len(DateRange) == 8


class TestTrustScoreWeights:
    """Test TrustScoreWeights configuration."""
    
    def test_default_weights_sum_to_one(self):
        """Test that default weights sum to 1.0."""
        total = (
            DEFAULT_TRUST_SCORE_WEIGHTS.rating_weight +
            DEFAULT_TRUST_SCORE_WEIGHTS.return_weight +
            DEFAULT_TRUST_SCORE_WEIGHTS.sentiment_weight +
            DEFAULT_TRUST_SCORE_WEIGHTS.operational_weight +
            DEFAULT_TRUST_SCORE_WEIGHTS.reliability_weight
        )
        assert 0.99 <= total <= 1.01  # Allow small floating point tolerance
    
    def test_weights_are_positive(self):
        """Test that all weights are positive."""
        assert DEFAULT_TRUST_SCORE_WEIGHTS.rating_weight > 0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.return_weight > 0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.sentiment_weight > 0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.operational_weight > 0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.reliability_weight > 0
    
    def test_weights_are_less_than_one(self):
        """Test that individual weights are less than 1."""
        assert DEFAULT_TRUST_SCORE_WEIGHTS.rating_weight < 1.0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.return_weight < 1.0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.sentiment_weight < 1.0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.operational_weight < 1.0
        assert DEFAULT_TRUST_SCORE_WEIGHTS.reliability_weight < 1.0
    
    def test_custom_weights_validation(self):
        """Test that custom weights are validated."""
        # Valid weights
        weights = TrustScoreWeights(
            rating_weight=0.2,
            return_weight=0.2,
            sentiment_weight=0.2,
            operational_weight=0.2,
            reliability_weight=0.2
        )
        assert weights is not None
        
        # Invalid weights (sum != 1.0)
        with pytest.raises(ValueError):
            TrustScoreWeights(
                rating_weight=0.6,
                return_weight=0.5,
                sentiment_weight=0.0,
                operational_weight=0.0,
                reliability_weight=0.0
            )
    
    def test_weights_to_dict(self):
        """Test converting weights to dictionary."""
        weights_dict = DEFAULT_TRUST_SCORE_WEIGHTS.to_dict()
        assert isinstance(weights_dict, dict)
        assert "rating" in weights_dict
        assert "return" in weights_dict
        assert "sentiment" in weights_dict
        assert "operational" in weights_dict
        assert "reliability" in weights_dict
        assert weights_dict["rating"] == DEFAULT_TRUST_SCORE_WEIGHTS.rating_weight


class TestRiskThresholds:
    """Test RiskThresholds configuration."""
    
    def test_default_thresholds(self):
        """Test default risk thresholds."""
        assert DEFAULT_RISK_THRESHOLDS.healthy_min == 80.0
        assert DEFAULT_RISK_THRESHOLDS.monitor_min == 60.0
        assert DEFAULT_RISK_THRESHOLDS.high_risk_max == 59.9
    
    def test_get_risk_level_healthy(self):
        """Test risk classification for healthy seller."""
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(90.0) == RiskLevel.HEALTHY
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(80.0) == RiskLevel.HEALTHY
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(85.0) == RiskLevel.HEALTHY
    
    def test_get_risk_level_monitor(self):
        """Test risk classification for monitor seller."""
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(70.0) == RiskLevel.MONITOR
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(60.0) == RiskLevel.MONITOR
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(65.0) == RiskLevel.MONITOR
    
    def test_get_risk_level_high_risk(self):
        """Test risk classification for high-risk seller."""
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(50.0) == RiskLevel.HIGH_RISK
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(0.0) == RiskLevel.HIGH_RISK
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(30.0) == RiskLevel.HIGH_RISK
    
    def test_get_risk_level_boundary(self):
        """Test risk classification at boundaries."""
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(79.9) == RiskLevel.MONITOR
        assert DEFAULT_RISK_THRESHOLDS.get_risk_level(59.9) == RiskLevel.HIGH_RISK
    
    def test_custom_thresholds(self):
        """Test custom risk thresholds."""
        thresholds = RiskThresholds(healthy_min=90.0, monitor_min=70.0, high_risk_max=69.9)
        assert thresholds.get_risk_level(95.0) == RiskLevel.HEALTHY
        assert thresholds.get_risk_level(80.0) == RiskLevel.MONITOR
        assert thresholds.get_risk_level(50.0) == RiskLevel.HIGH_RISK


class TestDataSufficiencyThresholds:
    """TestDataSufficiencyThresholds configuration."""
    
    def test_default_thresholds(self):
        """Test default data sufficiency thresholds."""
        assert DEFAULT_DATA_SUFFICIENCY.min_orders == 5
        assert DEFAULT_DATA_SUFFICIENCY.min_ratings == 3
        assert DEFAULT_DATA_SUFFICIENCY.min_reviews == 2
    
    def test_has_sufficient_data_orders(self):
        """Test data sufficiency based on orders."""
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(10, 0, 0) == True
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(5, 0, 0) == True
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(4, 0, 0) == False
    
    def test_has_sufficient_data_with_ratings(self):
        """Test data sufficiency with ratings."""
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(10, 5, 0) == True
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(10, 2, 0) == True  # Still sufficient due to orders
    
    def test_has_sufficient_data_with_reviews(self):
        """Test data sufficiency with reviews."""
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(10, 0, 5) == True
        assert DEFAULT_DATA_SUFFICIENCY.has_sufficient_data(10, 0, 1) == True  # Still sufficient due to orders
    
    def test_custom_thresholds(self):
        """Test custom data sufficiency thresholds."""
        thresholds = DataSufficiencyThresholds(min_orders=10, min_ratings=5, min_reviews=3)
        assert thresholds.has_sufficient_data(15, 0, 0) == True
        assert thresholds.has_sufficient_data(9, 0, 0) == False


class TestGetTrustScoreConfig:
    """Test get_trust_score_config function."""
    
    def test_config_structure(self):
        """Test that config returns proper structure."""
        config = get_trust_score_config()
        assert isinstance(config, dict)
        assert "weights" in config
        assert "risk_thresholds" in config
        assert "data_sufficiency" in config
    
    def test_config_weights(self):
        """Test config weights section."""
        config = get_trust_score_config()
        weights = config["weights"]
        assert isinstance(weights, dict)
        assert "rating" in weights
        assert "return" in weights
        assert "sentiment" in weights
        assert "operational" in weights
        assert "reliability" in weights
    
    def test_config_risk_thresholds(self):
        """Test config risk thresholds section."""
        config = get_trust_score_config()
        thresholds = config["risk_thresholds"]
        assert isinstance(thresholds, dict)
        assert "healthy_min" in thresholds
        assert "monitor_min" in thresholds
        assert "high_risk_max" in thresholds
    
    def test_config_data_sufficiency(self):
        """Test config data sufficiency section."""
        config = get_trust_score_config()
        sufficiency = config["data_sufficiency"]
        assert isinstance(sufficiency, dict)
        assert "min_orders" in sufficiency
        assert "min_ratings" in sufficiency
        assert "min_reviews" in sufficiency
    
    def test_config_values_match_defaults(self):
        """Test that config values match default constants."""
        config = get_trust_score_config()
        
        assert config["weights"]["rating"] == DEFAULT_TRUST_SCORE_WEIGHTS.rating_weight
        assert config["risk_thresholds"]["healthy_min"] == DEFAULT_RISK_THRESHOLDS.healthy_min
        assert config["data_sufficiency"]["min_orders"] == DEFAULT_DATA_SUFFICIENCY.min_orders