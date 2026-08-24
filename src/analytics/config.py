"""
Analytics configuration and constants for STAP.

This module contains configuration for the Trust Score calculation,
risk classification thresholds, and weighting schemes.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class RiskLevel(Enum):
    """Seller risk classification levels."""
    HEALTHY = "healthy"
    MONITOR = "monitor"
    HIGH_RISK = "high_risk"


class DateRange(Enum):
    """Standard date ranges for analytics."""
    ALL_TIME = "all_time"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_6_MONTHS = "last_6_months"
    LAST_1_YEAR = "last_1_year"
    LAST_3_YEARS = "last_3_years"
    LAST_5_YEARS = "last_5_years"
    CUSTOM = "custom"


@dataclass
class TrustScoreWeights:
    """
    Weights for the Trust Score calculation.
    
    All weights must sum to 1.0 (100%).
    """
    # Customer satisfaction component (ratings)
    rating_weight: float = 0.30
    
    # Return behavior component
    return_weight: float = 0.25
    
    # Review sentiment component
    sentiment_weight: float = 0.20
    
    # Operational performance component (delivery)
    operational_weight: float = 0.15
    
    # Order reliability component (completion rate)
    reliability_weight: float = 0.10
    
    def __post_init__(self):
        """Validate that weights sum to 1.0."""
        total = (
            self.rating_weight + 
            self.return_weight + 
            self.sentiment_weight + 
            self.operational_weight + 
            self.reliability_weight
        )
        if not (0.99 <= total <= 1.01):  # Allow small floating point tolerance
            raise ValueError(f"Trust score weights must sum to 1.0, got {total}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert weights to dictionary."""
        return {
            "rating": self.rating_weight,
            "return": self.return_weight,
            "sentiment": self.sentiment_weight,
            "operational": self.operational_weight,
            "reliability": self.reliability_weight
        }


@dataclass
class RiskThresholds:
    """
    Thresholds for risk classification based on Trust Score.
    
    Trust Score range: 0-100
    """
    healthy_min: float = 80.0
    monitor_min: float = 60.0
    high_risk_max: float = 59.9
    
    def get_risk_level(self, trust_score: float) -> RiskLevel:
        """
        Get risk level based on trust score.
        
        Args:
            trust_score: Trust score (0-100)
        
        Returns:
            RiskLevel classification
        """
        if trust_score >= self.healthy_min:
            return RiskLevel.HEALTHY
        elif trust_score >= self.monitor_min:
            return RiskLevel.MONITOR
        else:
            return RiskLevel.HIGH_RISK


@dataclass
class DataSufficiencyThresholds:
    """
    Minimum data requirements for reliable Trust Score calculation.
    """
    min_orders: int = 5  # Minimum orders for reliable assessment
    min_ratings: int = 3  # Minimum ratings for rating component
    min_reviews: int = 2  # Minimum reviews for sentiment component
    
    def has_sufficient_data(self, order_count: int, rating_count: int = 0, review_count: int = 0) -> bool:
        """
        Check if seller has sufficient data for reliable assessment.
        
        Args:
            order_count: Number of orders
            rating_count: Number of ratings
            review_count: Number of reviews
        
        Returns:
            True if sufficient data for reliable assessment
        """
        return order_count >= self.min_orders


# Default configuration instances
DEFAULT_TRUST_SCORE_WEIGHTS = TrustScoreWeights()
DEFAULT_RISK_THRESHOLDS = RiskThresholds()
DEFAULT_DATA_SUFFICIENCY = DataSufficiencyThresholds()


def get_trust_score_config() -> Dict[str, Any]:
    """
    Get complete Trust Score configuration.
    
    Returns:
        Dictionary with all Trust Score configuration
    """
    return {
        "weights": DEFAULT_TRUST_SCORE_WEIGHTS.to_dict(),
        "risk_thresholds": {
            "healthy_min": DEFAULT_RISK_THRESHOLDS.healthy_min,
            "monitor_min": DEFAULT_RISK_THRESHOLDS.monitor_min,
            "high_risk_max": DEFAULT_RISK_THRESHOLDS.high_risk_max
        },
        "data_sufficiency": {
            "min_orders": DEFAULT_DATA_SUFFICIENCY.min_orders,
            "min_ratings": DEFAULT_DATA_SUFFICIENCY.min_ratings,
            "min_reviews": DEFAULT_DATA_SUFFICIENCY.min_reviews
        }
    }