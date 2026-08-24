"""
Core analytics engine for STAP.

This module provides the main business logic for calculating seller performance
metrics, Trust Scores, and marketplace analytics.
"""

from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import sqlite3

from src.database.connection import DatabaseConnection
from src.analytics.config import (
    DEFAULT_TRUST_SCORE_WEIGHTS,
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_DATA_SUFFICIENCY,
    RiskLevel
)
from src.analytics.models import (
    SellerAnalytics,
    MarketplaceAnalytics,
    OrderMetrics,
    ReturnMetrics,
    RatingMetrics,
    ReviewMetrics,
    OperationalMetrics,
    TrustScoreComponents,
    HistoricalAnalytics,
    HistoricalDataPoint,
    DateRange
)
from src.analytics.normalization import (
    normalize_rating,
    normalize_return_rate,
    normalize_sentiment,
    normalize_completion_rate,
    normalize_average_delivery_days,
    safe_divide,
    safe_average
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsEngine:
    """
    Core analytics engine for STAP.
    
    This class provides methods for calculating seller performance metrics,
    Trust Scores, risk classifications, and marketplace-level analytics.
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Initialize the analytics engine.
        
        Args:
            db_connection: Database connection instance. If None, uses default.
        """
        self.db = db_connection or DatabaseConnection()
        logger.info("AnalyticsEngine initialized")
    
    def get_date_range_filters(
        self, 
        date_range: str = "all_time",
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get start and end date filters for a given date range.
        
        Args:
            date_range: Date range enum value
            custom_start: Custom start date (YYYY-MM-DD) for custom range
            custom_end: Custom end date (YYYY-MM-DD) for custom range
        
        Returns:
            Tuple of (start_date, end_date) as strings or None
        """
        end_date = datetime.now()
        
        if date_range == "all_time" or date_range is None:
            return None, None
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "last_90_days":
            start_date = end_date - timedelta(days=90)
        elif date_range == "last_6_months":
            start_date = end_date - timedelta(days=180)
        elif date_range == "last_1_year":
            start_date = end_date - timedelta(days=365)
        elif date_range == "last_3_years":
            start_date = end_date - timedelta(days=365 * 3)
        elif date_range == "last_5_years":
            start_date = end_date - timedelta(days=365 * 5)
        elif date_range == "custom":
            if custom_start and custom_end:
                try:
                    start_date = datetime.strptime(custom_start, "%Y-%m-%d")
                    end_date = datetime.strptime(custom_end, "%Y-%m-%d")
                except ValueError:
                    logger.error(f"Invalid custom date format: {custom_start}, {custom_end}")
                    return None, None
            else:
                logger.error("Custom date range requires both start and end dates")
                return None, None
        else:
            logger.warning(f"Unknown date range: {date_range}, using all time")
            return None, None
        
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
    def calculate_seller_analytics(
        self,
        seller_id: str,
        date_range: str = "all_time",
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> SellerAnalytics:
        """
        Calculate complete analytics for a single seller.
        
        Args:
            seller_id: Seller ID to analyze
            date_range: Time period for analysis
            custom_start: Custom start date for custom range
            custom_end: Custom end date for custom range
        
        Returns:
            SellerAnalytics object with all calculated metrics
        """
        logger.info(f"Calculating analytics for seller {seller_id}")
        
        # Get date filters
        start_date, end_date = self.get_date_range_filters(date_range, custom_start, custom_end)
        
        # Get seller information
        seller_info = self._get_seller_info(seller_id)
        if not seller_info:
            logger.error(f"Seller {seller_id} not found")
            raise ValueError(f"Seller {seller_id} not found")
        
        # Calculate individual metrics
        order_metrics = self._calculate_order_metrics(seller_id, start_date, end_date)
        return_metrics = self._calculate_return_metrics(seller_id, start_date, end_date, order_metrics.total_orders)
        rating_metrics = self._calculate_rating_metrics(seller_id, start_date, end_date)
        review_metrics = self._calculate_review_metrics(seller_id, start_date, end_date)
        operational_metrics = self._calculate_operational_metrics(seller_id, start_date, end_date)
        
        # Calculate Trust Score
        trust_score, components = self._calculate_trust_score(
            order_metrics, return_metrics, rating_metrics, review_metrics, operational_metrics
        )
        
        # Determine risk level
        risk_level = DEFAULT_RISK_THRESHOLDS.get_risk_level(trust_score)
        
        # Check data sufficiency
        has_sufficient_data, sufficiency_details = self._check_data_sufficiency(
            order_metrics.total_orders, rating_metrics.total_ratings, review_metrics.total_reviews
        )
        
        # Build analytics result
        analytics = SellerAnalytics(
            seller_id=seller_id,
            seller_name=seller_info['seller_name'],
            category=seller_info['category'],
            region=seller_info['region'],
            join_date=seller_info['join_date'],
            status=seller_info['status'],
            start_date=start_date,
            end_date=end_date,
            date_range=date_range,
            order_metrics=order_metrics,
            return_metrics=return_metrics,
            rating_metrics=rating_metrics,
            review_metrics=review_metrics,
            operational_metrics=operational_metrics,
            trust_score=trust_score,
            trust_score_components=components,
            risk_level=risk_level,
            has_sufficient_data=has_sufficient_data,
            data_sufficiency_details=sufficiency_details
        )
        
        logger.info(f"Analytics calculated for seller {seller_id}: Trust Score {trust_score:.1f}, Risk Level {risk_level.value}")
        return analytics
    
    def _get_seller_info(self, seller_id: str) -> Optional[Dict]:
        """Get seller information from database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT seller_id, seller_name, category, region, join_date, status FROM sellers WHERE seller_id = ?",
                (seller_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def _calculate_order_metrics(
        self, 
        seller_id: str, 
        start_date: Optional[str], 
        end_date: Optional[str]
    ) -> OrderMetrics:
        """Calculate order-related metrics for a seller."""
        with self.db.get_connection() as conn:
            # Build query with date filters
            query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
                    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                    SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) as refunded_orders,
                    SUM(order_value) as total_revenue,
                    AVG(order_value) as average_order_value
                FROM orders
                WHERE seller_id = ?
            """
            params = [seller_id]
            
            if start_date:
                query += " AND order_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND order_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            total_orders = row['total_orders'] or 0
            completed_orders = row['completed_orders'] or 0
            cancelled_orders = row['cancelled_orders'] or 0
            pending_orders = row['pending_orders'] or 0
            refunded_orders = row['refunded_orders'] or 0
            total_revenue = row['total_revenue'] or 0.0
            average_order_value = row['average_order_value'] or 0.0
            
            # Calculate rates
            completion_rate = safe_divide(completed_orders * 100, total_orders, 0.0)
            cancellation_rate = safe_divide(cancelled_orders * 100, total_orders, 0.0)
            
            return OrderMetrics(
                total_orders=total_orders,
                completed_orders=completed_orders,
                cancelled_orders=cancelled_orders,
                pending_orders=pending_orders,
                refunded_orders=refunded_orders,
                total_revenue=round(total_revenue, 2),
                average_order_value=round(average_order_value, 2),
                completion_rate=round(completion_rate, 2),
                cancellation_rate=round(cancellation_rate, 2)
            )
    
    def _calculate_return_metrics(
        self,
        seller_id: str,
        start_date: Optional[str],
        end_date: Optional[str],
        total_orders: int
    ) -> ReturnMetrics:
        """Calculate return-related metrics for a seller."""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    COUNT(*) as total_returns,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_returns,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_returns,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_returns
                FROM returns
                WHERE seller_id = ?
            """
            params = [seller_id]
            
            if start_date:
                query += " AND return_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND return_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            total_returns = row['total_returns'] or 0
            approved_returns = row['approved_returns'] or 0
            rejected_returns = row['rejected_returns'] or 0
            pending_returns = row['pending_returns'] or 0
            
            # Calculate return rate (returns / total orders)
            return_rate = safe_divide(total_returns * 100, total_orders, 0.0)
            
            return ReturnMetrics(
                total_returns=total_returns,
                approved_returns=approved_returns,
                rejected_returns=rejected_returns,
                pending_returns=pending_returns,
                return_rate=round(return_rate, 2)
            )
    
    def _calculate_rating_metrics(
        self,
        seller_id: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> RatingMetrics:
        """Calculate rating-related metrics for a seller."""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    COUNT(*) as total_ratings,
                    AVG(rating) as average_rating
                FROM ratings
                WHERE seller_id = ?
            """
            params = [seller_id]
            
            if start_date:
                query += " AND rating_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND rating_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            total_ratings = row['total_ratings'] or 0
            average_rating = row['average_rating'] or 0.0
            
            # Get rating distribution
            distribution_query = """
                SELECT rating, COUNT(*) as count
                FROM ratings
                WHERE seller_id = ?
            """
            dist_params = [seller_id]
            
            if start_date:
                distribution_query += " AND rating_date >= ?"
                dist_params.append(start_date)
            if end_date:
                distribution_query += " AND rating_date <= ?"
                dist_params.append(end_date)
            
            distribution_query += " GROUP BY rating ORDER BY rating"
            
            cursor = conn.execute(distribution_query, dist_params)
            rating_distribution = {row['rating']: row['count'] for row in cursor.fetchall()}
            
            # Calculate percentages
            five_star_count = rating_distribution.get(5, 0)
            one_star_count = rating_distribution.get(1, 0)
            five_star_percentage = safe_divide(five_star_count * 100, total_ratings, 0.0)
            one_star_percentage = safe_divide(one_star_count * 100, total_ratings, 0.0)
            
            return RatingMetrics(
                total_ratings=total_ratings,
                average_rating=round(average_rating, 2),
                rating_distribution=rating_distribution,
                five_star_percentage=round(five_star_percentage, 2),
                one_star_percentage=round(one_star_percentage, 2)
            )
    
    def _calculate_review_metrics(
        self,
        seller_id: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> ReviewMetrics:
        """Calculate review-related metrics for a seller."""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    COUNT(*) as total_reviews,
                    SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_reviews,
                    SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_reviews,
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_reviews,
                    AVG(sentiment_score) as average_sentiment_score
                FROM reviews
                WHERE seller_id = ?
            """
            params = [seller_id]
            
            if start_date:
                query += " AND review_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND review_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            total_reviews = row['total_reviews'] or 0
            positive_reviews = row['positive_reviews'] or 0
            neutral_reviews = row['neutral_reviews'] or 0
            negative_reviews = row['negative_reviews'] or 0
            average_sentiment_score = row['average_sentiment_score'] or 0.0
            
            # Calculate negative review percentage
            negative_review_percentage = safe_divide(negative_reviews * 100, total_reviews, 0.0)
            
            return ReviewMetrics(
                total_reviews=total_reviews,
                positive_reviews=positive_reviews,
                neutral_reviews=neutral_reviews,
                negative_reviews=negative_reviews,
                negative_review_percentage=round(negative_review_percentage, 2),
                average_sentiment_score=round(average_sentiment_score, 3)
            )
    
    def _calculate_operational_metrics(
        self,
        seller_id: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> OperationalMetrics:
        """Calculate operational performance metrics for a seller."""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    AVG(delivery_days) as average_delivery_days,
                    SUM(delivery_days) as total_delivery_days
                FROM orders
                WHERE seller_id = ? AND delivery_days IS NOT NULL
            """
            params = [seller_id]
            
            if start_date:
                query += " AND order_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND order_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            average_delivery_days = row['average_delivery_days'] or 0.0
            total_delivery_days = row['total_delivery_days'] or 0
            
            # For now, use a simple on-time rate based on delivery days
            # Orders delivered within 7 days are considered "on time"
            on_time_query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN delivery_days <= 7 THEN 1 ELSE 0 END) as on_time_orders
                FROM orders
                WHERE seller_id = ? AND delivery_days IS NOT NULL
            """
            on_time_params = [seller_id]
            
            if start_date:
                on_time_query += " AND order_date >= ?"
                on_time_params.append(start_date)
            if end_date:
                on_time_query += " AND order_date <= ?"
                on_time_params.append(end_date)
            
            cursor = conn.execute(on_time_query, on_time_params)
            on_time_row = cursor.fetchone()
            
            total_orders_with_delivery = on_time_row['total_orders'] or 0
            on_time_orders = on_time_row['on_time_orders'] or 0
            on_time_delivery_rate = safe_divide(on_time_orders * 100, total_orders_with_delivery, 0.0)
            
            return OperationalMetrics(
                average_delivery_days=round(average_delivery_days, 2),
                on_time_delivery_rate=round(on_time_delivery_rate, 2),
                total_delivery_days=total_delivery_days
            )
    
    def _calculate_trust_score(
        self,
        order_metrics: OrderMetrics,
        return_metrics: ReturnMetrics,
        rating_metrics: RatingMetrics,
        review_metrics: ReviewMetrics,
        operational_metrics: OperationalMetrics
    ) -> Tuple[float, TrustScoreComponents]:
        """
        Calculate Trust Score from individual metrics.
        
        Args:
            order_metrics: Order performance metrics
            return_metrics: Return behavior metrics
            rating_metrics: Customer rating metrics
            review_metrics: Customer review metrics
            operational_metrics: Operational performance metrics
        
        Returns:
            Tuple of (trust_score, components)
        """
        # Normalize individual components to 0-100 scale
        rating_component = normalize_rating(rating_metrics.average_rating)
        return_component = normalize_return_rate(return_metrics.return_rate)
        sentiment_component = normalize_sentiment(review_metrics.average_sentiment_score)
        operational_component = normalize_average_delivery_days(operational_metrics.average_delivery_days)
        reliability_component = normalize_completion_rate(order_metrics.completion_rate)
        
        # Handle missing data - use neutral values
        if rating_metrics.total_ratings == 0:
            rating_component = 50.0
        if review_metrics.total_reviews == 0:
            sentiment_component = 50.0
        if operational_metrics.total_delivery_days == 0:
            operational_component = 50.0
        
        # Calculate weighted Trust Score
        weights = DEFAULT_TRUST_SCORE_WEIGHTS
        trust_score = (
            rating_component * weights.rating_weight +
            return_component * weights.return_weight +
            sentiment_component * weights.sentiment_weight +
            operational_component * weights.operational_weight +
            reliability_component * weights.reliability_weight
        )
        
        # Clamp to 0-100 range
        trust_score = max(0.0, min(100.0, trust_score))
        
        components = TrustScoreComponents(
            rating_component=rating_component,
            return_component=return_component,
            sentiment_component=sentiment_component,
            operational_component=operational_component,
            reliability_component=reliability_component
        )
        
        return round(trust_score, 1), components
    
    def _check_data_sufficiency(
        self,
        order_count: int,
        rating_count: int,
        review_count: int
    ) -> Tuple[bool, Dict[str, bool]]:
        """
        Check if seller has sufficient data for reliable assessment.
        
        Args:
            order_count: Number of orders
            rating_count: Number of ratings
            review_count: Number of reviews
        
        Returns:
            Tuple of (has_sufficient_data, details_dict)
        """
        thresholds = DEFAULT_DATA_SUFFICIENCY
        
        details = {
            "sufficient_orders": order_count >= thresholds.min_orders,
            "sufficient_ratings": rating_count >= thresholds.min_ratings,
            "sufficient_reviews": review_count >= thresholds.min_reviews
        }
        
        has_sufficient = details["sufficient_orders"]  # Orders are the primary requirement
        
        return has_sufficient, details
    
    def calculate_marketplace_analytics(
        self,
        date_range: str = "all_time",
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> MarketplaceAnalytics:
        """
        Calculate marketplace-level analytics.
        
        Args:
            date_range: Time period for analysis
            custom_start: Custom start date for custom range
            custom_end: Custom end date for custom range
        
        Returns:
            MarketplaceAnalytics object with aggregated metrics
        """
        logger.info("Calculating marketplace analytics")
        
        # Get date filters
        start_date, end_date = self.get_date_range_filters(date_range, custom_start, custom_end)
        
        with self.db.get_connection() as conn:
            # Get seller counts
            seller_query = """
                SELECT 
                    COUNT(*) as total_sellers,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_sellers
                FROM sellers
            """
            cursor = conn.execute(seller_query)
            seller_row = cursor.fetchone()
            
            total_sellers = seller_row['total_sellers'] or 0
            active_sellers = seller_row['active_sellers'] or 0
            
            # Get order metrics
            order_query = "SELECT COUNT(*) as total_orders, SUM(order_value) as total_revenue FROM orders"
            order_params = []
            if start_date:
                order_query += " WHERE order_date >= ?"
                order_params.append(start_date)
            if end_date:
                if not start_date:
                    order_query += " WHERE"
                else:
                    order_query += " AND"
                order_query += " order_date <= ?"
                order_params.append(end_date)
            
            cursor = conn.execute(order_query, order_params)
            order_row = cursor.fetchone()
            
            total_orders = order_row['total_orders'] or 0
            total_revenue = order_row['total_revenue'] or 0.0
            
            # Get return metrics
            return_query = "SELECT COUNT(*) as total_returns FROM returns"
            return_params = []
            if start_date:
                return_query += " WHERE return_date >= ?"
                return_params.append(start_date)
            if end_date:
                if not start_date:
                    return_query += " WHERE"
                else:
                    return_query += " AND"
                return_query += " return_date <= ?"
                return_params.append(end_date)
            
            cursor = conn.execute(return_query, return_params)
            return_row = cursor.fetchone()
            total_returns = return_row['total_returns'] or 0
            
            # Get rating metrics
            rating_query = "SELECT COUNT(*) as total_ratings, AVG(rating) as average_rating FROM ratings"
            rating_params = []
            if start_date:
                rating_query += " WHERE rating_date >= ?"
                rating_params.append(start_date)
            if end_date:
                if not start_date:
                    rating_query += " WHERE"
                else:
                    rating_query += " AND"
                rating_query += " rating_date <= ?"
                rating_params.append(end_date)
            
            cursor = conn.execute(rating_query, rating_params)
            rating_row = cursor.fetchone()
            
            total_ratings = rating_row['total_ratings'] or 0
            overall_average_rating = rating_row['average_rating'] or 0.0
            
            # Get review metrics
            review_query = """
                SELECT 
                    COUNT(*) as total_reviews,
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_reviews,
                    AVG(sentiment_score) as average_sentiment
                FROM reviews
            """
            review_params = []
            if start_date:
                review_query += " WHERE review_date >= ?"
                review_params.append(start_date)
            if end_date:
                if not start_date:
                    review_query += " WHERE"
                else:
                    review_query += " AND"
                review_query += " review_date <= ?"
                review_params.append(end_date)
            
            cursor = conn.execute(review_query, review_params)
            review_row = cursor.fetchone()
            
            total_reviews = review_row['total_reviews'] or 0
            negative_reviews = review_row['negative_reviews'] or 0
            overall_average_sentiment = review_row['average_sentiment'] or 0.0
            
            # Calculate derived metrics
            overall_return_rate = safe_divide(total_returns * 100, total_orders, 0.0)
            overall_negative_review_percentage = safe_divide(negative_reviews * 100, total_reviews, 0.0)
            overall_completion_rate = self._calculate_marketplace_completion_rate(start_date, end_date)
        
        # Calculate Trust Score distribution
        trust_scores = self._calculate_all_seller_trust_scores(start_date, end_date)
        healthy_sellers = sum(1 for score in trust_scores if score >= DEFAULT_RISK_THRESHOLDS.healthy_min)
        monitor_sellers = sum(1 for score in trust_scores if DEFAULT_RISK_THRESHOLDS.monitor_min <= score < DEFAULT_RISK_THRESHOLDS.healthy_min)
        high_risk_sellers = sum(1 for score in trust_scores if score < DEFAULT_RISK_THRESHOLDS.monitor_min)
        average_trust_score = safe_average(trust_scores, 0.0)
        
        trust_score_distribution = {
            "healthy": healthy_sellers,
            "monitor": monitor_sellers,
            "high_risk": high_risk_sellers
        }
        
        analytics = MarketplaceAnalytics(
            total_sellers=total_sellers,
            active_sellers=active_sellers,
            healthy_sellers=healthy_sellers,
            monitor_sellers=monitor_sellers,
            high_risk_sellers=high_risk_sellers,
            total_orders=total_orders,
            total_revenue=round(total_revenue, 2),
            overall_completion_rate=round(overall_completion_rate, 2),
            total_returns=total_returns,
            overall_return_rate=round(overall_return_rate, 2),
            total_ratings=total_ratings,
            overall_average_rating=round(overall_average_rating, 2),
            total_reviews=total_reviews,
            overall_negative_review_percentage=round(overall_negative_review_percentage, 2),
            overall_average_sentiment=round(overall_average_sentiment, 3),
            average_trust_score=round(average_trust_score, 1),
            trust_score_distribution=trust_score_distribution,
            start_date=start_date,
            end_date=end_date,
            date_range=date_range
        )
        
        logger.info(f"Marketplace analytics calculated: {total_sellers} sellers, {total_orders} orders")
        return analytics
    
    def _calculate_marketplace_completion_rate(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> float:
        """Calculate overall order completion rate for marketplace."""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders
                FROM orders
            """
            params = []
            
            if start_date:
                query += " WHERE order_date >= ?"
                params.append(start_date)
            if end_date:
                if not start_date:
                    query += " WHERE"
                else:
                    query += " AND"
                query += " order_date <= ?"
                params.append(end_date)
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            total_orders = row['total_orders'] or 0
            completed_orders = row['completed_orders'] or 0
            
            return safe_divide(completed_orders * 100, total_orders, 0.0)
    
    def _calculate_all_seller_trust_scores(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> List[float]:
        """Calculate Trust Scores for all sellers."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT seller_id FROM sellers")
            seller_ids = [row['seller_id'] for row in cursor.fetchall()]
        
        trust_scores = []
        for seller_id in seller_ids:
            try:
                analytics = self.calculate_seller_analytics(seller_id, "custom", start_date, end_date)
                trust_scores.append(analytics.trust_score)
            except Exception as e:
                logger.warning(f"Failed to calculate trust score for seller {seller_id}: {e}")
                continue
        
        return trust_scores
    
    def rank_sellers_by_trust_score(
        self,
        limit: Optional[int] = None,
        date_range: str = "all_time",
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> List[SellerAnalytics]:
        """
        Rank sellers by Trust Score (highest first).
        
        Args:
            limit: Maximum number of sellers to return
            date_range: Time period for analysis
            custom_start: Custom start date for custom range
            custom_end: Custom end date for custom range
        
        Returns:
            List of SellerAnalytics objects sorted by Trust Score (descending)
        """
        logger.info(f"Ranking sellers by Trust Score (limit: {limit})")
        
        # Get all seller IDs
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT seller_id FROM sellers ORDER BY seller_id")
            seller_ids = [row['seller_id'] for row in cursor.fetchall()]
        
        # Calculate analytics for all sellers
        all_analytics = []
        for seller_id in seller_ids:
            try:
                analytics = self.calculate_seller_analytics(
                    seller_id, date_range, custom_start, custom_end
                )
                all_analytics.append(analytics)
            except Exception as e:
                logger.warning(f"Failed to calculate analytics for seller {seller_id}: {e}")
                continue
        
        # Sort by Trust Score (descending), then by seller_id for deterministic tie-breaking
        all_analytics.sort(key=lambda x: (-x.trust_score, x.seller_id))
        
        # Apply limit if specified
        if limit and limit > 0:
            all_analytics = all_analytics[:limit]
        
        logger.info(f"Ranked {len(all_analytics)} sellers by Trust Score")
        return all_analytics
    
    def calculate_historical_analytics(
        self,
        entity_id: str,
        entity_type: str,
        metric_name: str,
        aggregation_period: str = "month",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> HistoricalAnalytics:
        """
        Calculate historical time-series analytics for a metric.
        
        Args:
            entity_id: Seller ID or "marketplace"
            entity_type: "seller" or "marketplace"
            metric_name: Name of metric to track
            aggregation_period: "day", "week", or "month"
            start_date: Start date for historical period
            end_date: End date for historical period
        
        Returns:
            HistoricalAnalytics object with time-series data
        """
        logger.info(f"Calculating historical analytics for {entity_type} {entity_id}, metric {metric_name}")
        
        # For now, implement a simple version that returns empty data
        # Full implementation would require complex date grouping logic
        # This is a placeholder for future enhancement
        
        return HistoricalAnalytics(
            entity_id=entity_id,
            entity_type=entity_type,
            metric_name=metric_name,
            aggregation_period=aggregation_period,
            data_points=[],
            start_date=start_date,
            end_date=end_date
        )


# Global analytics engine instance
analytics_engine = AnalyticsEngine()