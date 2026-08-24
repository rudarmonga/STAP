"""
Data models for analytics results.

This module defines the data structures for seller analytics,
marketplace analytics, and trust score results.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

from src.analytics.config import RiskLevel, DateRange


@dataclass
class OrderMetrics:
    """Order-related metrics for a seller."""
    total_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    pending_orders: int = 0
    refunded_orders: int = 0
    total_revenue: float = 0.0
    average_order_value: float = 0.0
    completion_rate: float = 0.0  # completed / total orders
    cancellation_rate: float = 0.0  # cancelled / total orders


@dataclass
class ReturnMetrics:
    """Return-related metrics for a seller."""
    total_returns: int = 0
    approved_returns: int = 0
    rejected_returns: int = 0
    pending_returns: int = 0
    return_rate: float = 0.0  # returns / applicable orders


@dataclass
class RatingMetrics:
    """Rating-related metrics for a seller."""
    total_ratings: int = 0
    average_rating: float = 0.0
    rating_distribution: Dict[int, int] = field(default_factory=dict)  # {1: count, 2: count, ...}
    five_star_percentage: float = 0.0
    one_star_percentage: float = 0.0


@dataclass
class ReviewMetrics:
    """Review-related metrics for a seller."""
    total_reviews: int = 0
    positive_reviews: int = 0
    neutral_reviews: int = 0
    negative_reviews: int = 0
    negative_review_percentage: float = 0.0
    average_sentiment_score: float = 0.0


@dataclass
class OperationalMetrics:
    """Operational performance metrics for a seller."""
    average_delivery_days: float = 0.0
    on_time_delivery_rate: float = 0.0  # Assuming delivery within expected time
    total_delivery_days: int = 0


@dataclass
class TrustScoreComponents:
    """Individual components that make up the Trust Score."""
    rating_component: float = 0.0  # 0-100 scale
    return_component: float = 0.0  # 0-100 scale
    sentiment_component: float = 0.0  # 0-100 scale
    operational_component: float = 0.0  # 0-100 scale
    reliability_component: float = 0.0  # 0-100 scale
    
    def to_dict(self) -> Dict[str, float]:
        """Convert components to dictionary."""
        return {
            "rating": self.rating_component,
            "return": self.return_component,
            "sentiment": self.sentiment_component,
            "operational": self.operational_component,
            "reliability": self.reliability_component
        }


@dataclass
class SellerAnalytics:
    """
    Complete analytics result for a single seller.
    
    This contains all calculated metrics, trust score, and classification
    for a seller over a specified time period.
    """
    # Seller information
    seller_id: str
    seller_name: str
    category: str
    region: str
    join_date: str
    status: str
    
    # Time period
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    date_range: Optional[str] = None
    
    # Performance metrics
    order_metrics: OrderMetrics = field(default_factory=OrderMetrics)
    return_metrics: ReturnMetrics = field(default_factory=ReturnMetrics)
    rating_metrics: RatingMetrics = field(default_factory=RatingMetrics)
    review_metrics: ReviewMetrics = field(default_factory=ReviewMetrics)
    operational_metrics: OperationalMetrics = field(default_factory=OperationalMetrics)
    
    # Trust Score and classification
    trust_score: float = 0.0
    trust_score_components: TrustScoreComponents = field(default_factory=TrustScoreComponents)
    risk_level: RiskLevel = RiskLevel.HIGH_RISK
    
    # Data sufficiency
    has_sufficient_data: bool = False
    data_sufficiency_details: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics result to dictionary."""
        return {
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "category": self.category,
            "region": self.region,
            "join_date": self.join_date,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "date_range": self.date_range,
            "order_metrics": {
                "total_orders": self.order_metrics.total_orders,
                "completed_orders": self.order_metrics.completed_orders,
                "cancelled_orders": self.order_metrics.cancelled_orders,
                "pending_orders": self.order_metrics.pending_orders,
                "refunded_orders": self.order_metrics.refunded_orders,
                "total_revenue": self.order_metrics.total_revenue,
                "average_order_value": self.order_metrics.average_order_value,
                "completion_rate": self.order_metrics.completion_rate,
                "cancellation_rate": self.order_metrics.cancellation_rate
            },
            "return_metrics": {
                "total_returns": self.return_metrics.total_returns,
                "approved_returns": self.return_metrics.approved_returns,
                "rejected_returns": self.return_metrics.rejected_returns,
                "pending_returns": self.return_metrics.pending_returns,
                "return_rate": self.return_metrics.return_rate
            },
            "rating_metrics": {
                "total_ratings": self.rating_metrics.total_ratings,
                "average_rating": self.rating_metrics.average_rating,
                "rating_distribution": self.rating_metrics.rating_distribution,
                "five_star_percentage": self.rating_metrics.five_star_percentage,
                "one_star_percentage": self.rating_metrics.one_star_percentage
            },
            "review_metrics": {
                "total_reviews": self.review_metrics.total_reviews,
                "positive_reviews": self.review_metrics.positive_reviews,
                "neutral_reviews": self.review_metrics.neutral_reviews,
                "negative_reviews": self.review_metrics.negative_reviews,
                "negative_review_percentage": self.review_metrics.negative_review_percentage,
                "average_sentiment_score": self.review_metrics.average_sentiment_score
            },
            "operational_metrics": {
                "average_delivery_days": self.operational_metrics.average_delivery_days,
                "on_time_delivery_rate": self.operational_metrics.on_time_delivery_rate,
                "total_delivery_days": self.operational_metrics.total_delivery_days
            },
            "trust_score": self.trust_score,
            "trust_score_components": self.trust_score_components.to_dict(),
            "risk_level": self.risk_level.value,
            "has_sufficient_data": self.has_sufficient_data,
            "data_sufficiency_details": self.data_sufficiency_details,
            "calculated_at": self.calculated_at
        }


@dataclass
class MarketplaceAnalytics:
    """
    Aggregated analytics for the entire marketplace.
    
    This contains marketplace-level metrics and distributions.
    """
    # Seller counts
    total_sellers: int = 0
    active_sellers: int = 0
    healthy_sellers: int = 0
    monitor_sellers: int = 0
    high_risk_sellers: int = 0
    
    # Order metrics
    total_orders: int = 0
    total_revenue: float = 0.0
    overall_completion_rate: float = 0.0
    
    # Return metrics
    total_returns: int = 0
    overall_return_rate: float = 0.0
    
    # Rating metrics
    total_ratings: int = 0
    overall_average_rating: float = 0.0
    
    # Review metrics
    total_reviews: int = 0
    overall_negative_review_percentage: float = 0.0
    overall_average_sentiment: float = 0.0
    
    # Trust Score metrics
    average_trust_score: float = 0.0
    trust_score_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Time period
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    date_range: Optional[str] = None
    
    # Metadata
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert marketplace analytics to dictionary."""
        return {
            "total_sellers": self.total_sellers,
            "active_sellers": self.active_sellers,
            "healthy_sellers": self.healthy_sellers,
            "monitor_sellers": self.monitor_sellers,
            "high_risk_sellers": self.high_risk_sellers,
            "total_orders": self.total_orders,
            "total_revenue": self.total_revenue,
            "overall_completion_rate": self.overall_completion_rate,
            "total_returns": self.total_returns,
            "overall_return_rate": self.overall_return_rate,
            "total_ratings": self.total_ratings,
            "overall_average_rating": self.overall_average_rating,
            "total_reviews": self.total_reviews,
            "overall_negative_review_percentage": self.overall_negative_review_percentage,
            "overall_average_sentiment": self.overall_average_sentiment,
            "average_trust_score": self.average_trust_score,
            "trust_score_distribution": self.trust_score_distribution,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "date_range": self.date_range,
            "calculated_at": self.calculated_at
        }


@dataclass
class HistoricalDataPoint:
    """A single data point in a time series."""
    date: str
    value: float
    count: int = 0  # Number of records contributing to this value


@dataclass
class HistoricalAnalytics:
    """
    Historical time-series analytics for a seller or marketplace.
    
    This contains metrics over time for trend analysis.
    """
    entity_id: str  # seller_id or "marketplace"
    entity_type: str  # "seller" or "marketplace"
    metric_name: str  # e.g., "trust_score", "return_rate", "average_rating"
    aggregation_period: str  # "day", "week", "month"
    data_points: List[HistoricalDataPoint] = field(default_factory=list)
    
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert historical analytics to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "metric_name": self.metric_name,
            "aggregation_period": self.aggregation_period,
            "data_points": [
                {"date": dp.date, "value": dp.value, "count": dp.count}
                for dp in self.data_points
            ],
            "start_date": self.start_date,
            "end_date": self.end_date,
            "calculated_at": self.calculated_at
        }