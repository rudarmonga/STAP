"""
Synthetic data generation for STAP.

This module provides the foundation for generating realistic marketplace data
without external dependencies. The architecture supports:

- Reproducible data generation using seeds
- Multiple entity types (sellers, orders, returns, ratings, reviews)
- Historical data generation
- Configurable data volumes
- Realistic data distributions
- Seller performance variation
"""

import random
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SellerPerformance(Enum):
    """Seller performance profile types."""
    HEALTHY = "healthy"
    AVERAGE = "average"
    DECLINING = "declining"
    HIGH_RISK = "high_risk"


@dataclass
class SellerProfile:
    """Seller performance profile with characteristic patterns."""
    performance_type: SellerPerformance
    base_rating_mean: float
    base_rating_std: float
    return_rate: float
    negative_sentiment_rate: float
    order_frequency: float
    delivery_days_mean: float
    delivery_days_std: float


class SyntheticDataGenerator:
    """
    Base class for synthetic data generation.
    
    This class provides the foundation for generating various types of
    marketplace data with realistic properties and reproducible seeds.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize the data generator.
        
        Args:
            seed: Random seed for reproducibility. If None, uses settings.
        """
        self.seed = seed or settings.synthetic_data_seed
        self._rng = random.Random(self.seed)
        logger.debug(f"SyntheticDataGenerator initialized with seed: {self.seed}")
    
    def reset_seed(self, seed: int) -> None:
        """
        Reset the random seed.
        
        Args:
            seed: New random seed
        """
        self.seed = seed
        self._rng = random.Random(self.seed)
        logger.debug(f"Random seed reset to: {self.seed}")
    
    def generate_seller_id(self) -> str:
        """
        Generate a realistic seller ID.
        
        Returns:
            Seller ID string
        """
        return f"SELLER-{self._rng.randint(10000, 99999)}"
    
    def generate_product_id(self) -> str:
        """
        Generate a realistic product ID.
        
        Returns:
            Product ID string
        """
        return f"PROD-{self._rng.randint(100000, 999999)}"
    
    def generate_order_id(self) -> str:
        """
        Generate a realistic order ID.
        
        Returns:
            Order ID string
        """
        return f"ORD-{self._rng.randint(1000000, 9999999)}"
    
    def generate_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        count: int
    ) -> List[datetime]:
        """
        Generate a list of random dates within a range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            count: Number of dates to generate
        
        Returns:
            List of datetime objects
        """
        delta = end_date - start_date
        return [
            start_date + timedelta(
                days=self._rng.randint(0, delta.days),
                seconds=self._rng.randint(0, 86400)
            )
            for _ in range(count)
        ]
    
    def generate_category(self) -> str:
        """
        Generate a realistic product category.
        
        Returns:
            Category name
        """
        categories = [
            "Electronics", "Clothing", "Home & Garden", "Sports",
            "Books", "Toys", "Automotive", "Health & Beauty",
            "Food & Grocery", "Office Supplies"
        ]
        return self._rng.choice(categories)
    
    def generate_region(self) -> str:
        """
        Generate a realistic geographic region.
        
        Returns:
            Region name
        """
        regions = [
            "North America", "Europe", "Asia Pacific", 
            "Latin America", "Middle East", "Africa"
        ]
        return self._rng.choice(regions)


@dataclass
class SellerData:
    """Data structure for seller information."""
    seller_id: str
    seller_name: str
    category: str
    region: str
    join_date: str
    status: str


@dataclass
class OrderData:
    """Data structure for order information."""
    order_id: str
    seller_id: str
    order_date: str
    category: str
    region: str
    order_value: float
    delivery_days: int
    status: str


@dataclass
class ReturnData:
    """Data structure for return information."""
    return_id: str
    order_id: str
    seller_id: str
    return_date: str
    return_reason: str
    status: str


@dataclass
class RatingData:
    """Data structure for rating information."""
    rating_id: str
    seller_id: str
    order_id: Optional[str]
    rating: int
    rating_date: str


@dataclass
class ReviewData:
    """Data structure for review information."""
    review_id: str
    seller_id: str
    order_id: Optional[str]
    review_date: str
    review_text: str
    sentiment: Optional[str]
    sentiment_score: Optional[float]


class MarketplaceDataGenerator(SyntheticDataGenerator):
    """
    Generates complete marketplace dataset with realistic seller performance patterns.
    
    This class generates comprehensive synthetic data including sellers, orders, 
    returns, ratings, and reviews with meaningful relationships and performance variation.
    """
    
    # Constants for data generation
    SELLER_NAMES = [
        "TechMart", "HomeEssentials", "FashionHub", "SportsCentral", 
        "BookWorld", "ToyEmporium", "AutoParts Pro", "BeautyBox",
        "FreshGrocery", "OfficeDepot", "ElectroWorld", "StyleCorner",
        "GardenMart", "FitnessPro", "ReadersParadise", "KidsZone",
        "CarCare", "GlowUp", "MarketFresh", "WorkSpace"
    ]
    
    CATEGORIES = [
        "Electronics", "Clothing", "Home & Garden", "Sports",
        "Books", "Toys", "Automotive", "Health & Beauty",
        "Food & Grocery", "Office Supplies"
    ]
    
    REGIONS = [
        "North America", "Europe", "Asia Pacific", 
        "Latin America", "Middle East", "Africa"
    ]
    
    RETURN_REASONS = [
        "Defective product", "Not as described", "Wrong item", 
        "Changed mind", "Damaged in shipping", "Poor quality"
    ]
    
    REVIEW_TEMPLATES = {
        "positive": [
            "Great product, exactly as described!",
            "Excellent quality and fast shipping.",
            "Very satisfied with this purchase.",
            "Highly recommend this seller.",
            "Perfect condition, great value.",
            "Amazing quality, will buy again.",
            "Exceeded my expectations completely.",
            "Fantastic product and service."
        ],
        "neutral": [
            "Product is okay, nothing special.",
            "Average quality for the price.",
            "Received what I ordered, on time.",
            "Decent product, could be better.",
            "It's fine, meets basic expectations.",
            "Reasonable quality, standard shipping."
        ],
        "negative": [
            "Poor quality, not worth the price.",
            "Disappointed with this purchase.",
            "Not as described, very different.",
            "Would not recommend this seller.",
            "Terrible quality, arrived damaged.",
            "Very slow shipping, poor communication.",
            "Product broke after one use.",
            "Complete waste of money."
        ]
    }
    
    SELLER_PROFILES = {
        SellerPerformance.HEALTHY: SellerProfile(
            performance_type=SellerPerformance.HEALTHY,
            base_rating_mean=4.5,
            base_rating_std=0.5,
            return_rate=0.02,
            negative_sentiment_rate=0.05,
            order_frequency=1.0,
            delivery_days_mean=3.0,
            delivery_days_std=1.0
        ),
        SellerPerformance.AVERAGE: SellerProfile(
            performance_type=SellerPerformance.AVERAGE,
            base_rating_mean=3.5,
            base_rating_std=0.8,
            return_rate=0.05,
            negative_sentiment_rate=0.15,
            order_frequency=0.8,
            delivery_days_mean=5.0,
            delivery_days_std=2.0
        ),
        SellerPerformance.DECLINING: SellerProfile(
            performance_type=SellerPerformance.DECLINING,
            base_rating_mean=2.8,
            base_rating_std=1.0,
            return_rate=0.10,
            negative_sentiment_rate=0.35,
            order_frequency=0.6,
            delivery_days_mean=7.0,
            delivery_days_std=3.0
        ),
        SellerPerformance.HIGH_RISK: SellerProfile(
            performance_type=SellerPerformance.HIGH_RISK,
            base_rating_mean=2.0,
            base_rating_std=1.2,
            return_rate=0.20,
            negative_sentiment_rate=0.60,
            order_frequency=0.4,
            delivery_days_mean=10.0,
            delivery_days_std=5.0
        )
    }
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self._seller_profiles: Dict[str, SellerProfile] = {}
        logger.info("MarketplaceDataGenerator initialized")
    
    def _assign_seller_profile(self) -> SellerPerformance:
        """Assign a performance profile to a seller based on realistic distribution."""
        # Distribution: 40% healthy, 30% average, 20% declining, 10% high risk
        rand = self._rng.random()
        if rand < 0.40:
            return SellerPerformance.HEALTHY
        elif rand < 0.70:
            return SellerPerformance.AVERAGE
        elif rand < 0.90:
            return SellerPerformance.DECLINING
        else:
            return SellerPerformance.HIGH_RISK
    
    def _generate_rating(self, profile: SellerProfile) -> int:
        """Generate a rating based on seller profile."""
        rating = self._rng.gauss(profile.base_rating_mean, profile.base_rating_std)
        rating = max(1, min(5, round(rating)))
        return int(rating)
    
    def _generate_sentiment(self, profile: SellerProfile) -> tuple[str, float]:
        """Generate sentiment and score based on seller profile."""
        rand = self._rng.random()
        
        if rand < profile.negative_sentiment_rate:
            sentiment = "negative"
            sentiment_score = -self._rng.uniform(0.5, 1.0)
        elif rand < profile.negative_sentiment_rate + 0.3:
            sentiment = "neutral"
            sentiment_score = self._rng.uniform(-0.3, 0.3)
        else:
            sentiment = "positive"
            sentiment_score = self._rng.uniform(0.5, 1.0)
        
        return sentiment, sentiment_score
    
    def _generate_delivery_days(self, profile: SellerProfile) -> int:
        """Generate delivery days based on seller profile."""
        import math
        days = self._rng.gauss(profile.delivery_days_mean, profile.delivery_days_std)
        return max(1, min(30, round(days)))
    
    def generate_sellers(
        self, 
        count: int = 100,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[SellerData]:
        """
        Generate synthetic seller data with performance profiles.
        
        Args:
            count: Number of sellers to generate
            start_date: Earliest join date (default: 5 years ago)
            end_date: Latest join date (default: now)
        
        Returns:
            List of SellerData objects
        """
        logger.info(f"Generating {count} synthetic sellers")
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=5*365)
        if end_date is None:
            end_date = datetime.now()
        
        sellers = []
        used_names = set()
        used_seller_ids = set()
        
        for i in range(count):
            # Generate unique seller ID
            while True:
                seller_id = self.generate_seller_id()
                if seller_id not in used_seller_ids:
                    used_seller_ids.add(seller_id)
                    break
            
            # Generate unique seller name
            while True:
                base_name = self._rng.choice(self.SELLER_NAMES)
                suffix = self._rng.randint(1, 9999)
                seller_name = f"{base_name} {suffix}"
                if seller_name not in used_names:
                    used_names.add(seller_name)
                    break
            
            category = self.generate_category()
            region = self.generate_region()
            
            # Join date distributed over historical period
            join_date = self.generate_date_range(start_date, end_date, 1)[0]
            
            # Most sellers are active
            status = "active" if self._rng.random() < 0.9 else "inactive"
            
            # Assign performance profile
            performance_type = self._assign_seller_profile()
            self._seller_profiles[seller_id] = self.SELLER_PROFILES[performance_type]
            
            seller = SellerData(
                seller_id=seller_id,
                seller_name=seller_name,
                category=category,
                region=region,
                join_date=join_date.strftime("%Y-%m-%d"),
                status=status
            )
            sellers.append(seller)
        
        logger.info(f"Generated {len(sellers)} sellers with performance profiles")
        return sellers
    
    def generate_orders(
        self,
        sellers: List[SellerData],
        count: int = 5000,
        days_back: int = 365
    ) -> List[OrderData]:
        """
        Generate synthetic order data with realistic seller-specific patterns.
        
        Args:
            sellers: List of sellers to generate orders for
            count: Total number of orders to generate
            days_back: Historical period in days
        
        Returns:
            List of OrderData objects
        """
        logger.info(f"Generating {count} synthetic orders over {days_back} days")
        
        if not sellers:
            logger.warning("No sellers provided, cannot generate orders")
            return []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        orders = []
        seller_map = {s.seller_id: s for s in sellers}
        used_order_ids = set()
        
        # Distribute orders across sellers based on their profile
        total_order_weight = sum(
            self._seller_profiles.get(s.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE]).order_frequency
            for s in sellers
        )
        
        for i in range(count):
            # Select seller weighted by order frequency
            rand = self._rng.uniform(0, total_order_weight)
            cumulative = 0
            selected_seller = None
            
            for seller in sellers:
                profile = self._seller_profiles.get(seller.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE])
                cumulative += profile.order_frequency
                if rand <= cumulative:
                    selected_seller = seller
                    break
            
            if selected_seller is None:
                selected_seller = self._rng.choice(sellers)
            
            profile = self._seller_profiles.get(selected_seller.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE])
            
            # Generate unique order ID
            while True:
                order_id = self.generate_order_id()
                if order_id not in used_order_ids:
                    used_order_ids.add(order_id)
                    break
            
            # Order date distributed over historical period
            order_date = self.generate_date_range(start_date, end_date, 1)[0]
            
            # Use seller's category and region
            category = selected_seller.category
            region = selected_seller.region
            
            # Order value based on realistic distribution
            order_value = self._rng.triangular(10, 500, 50)
            
            # Delivery days based on seller profile
            delivery_days = self._generate_delivery_days(profile)
            
            # Most orders are completed
            status_rand = self._rng.random()
            if status_rand < 0.85:
                status = "completed"
            elif status_rand < 0.95:
                status = "cancelled"
            elif status_rand < 0.98:
                status = "refunded"
            else:
                status = "pending"
            
            order = OrderData(
                order_id=order_id,
                seller_id=selected_seller.seller_id,
                order_date=order_date.strftime("%Y-%m-%d"),
                category=category,
                region=region,
                order_value=round(order_value, 2),
                delivery_days=delivery_days,
                status=status
            )
            orders.append(order)
        
        logger.info(f"Generated {len(orders)} orders")
        return orders
    
    def generate_returns(
        self,
        orders: List[OrderData],
        return_rate: float = 0.08
    ) -> List[ReturnData]:
        """
        Generate synthetic return data based on orders.
        
        Args:
            orders: List of orders to potentially generate returns for
            return_rate: Overall return rate (will be adjusted by seller profile)
        
        Returns:
            List of ReturnData objects
        """
        logger.info(f"Generating returns from {len(orders)} orders")
        
        returns = []
        used_return_ids = set()
        
        for order in orders:
            # Get seller profile for this order
            profile = self._seller_profiles.get(order.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE])
            
            # Adjust return rate based on seller profile
            adjusted_return_rate = profile.return_rate
            
            if self._rng.random() < adjusted_return_rate:
                # Generate unique return ID
                while True:
                    return_id = f"RET-{self._rng.randint(100000, 999999)}"
                    if return_id not in used_return_ids:
                        used_return_ids.add(return_id)
                        break
                
                # Return date after order date
                order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
                return_date = order_date + timedelta(days=self._rng.randint(1, 30))
                
                return_reason = self._rng.choice(self.RETURN_REASONS)
                
                # Most returns are approved
                status = "approved" if self._rng.random() < 0.7 else "rejected"
                
                return_data = ReturnData(
                    return_id=return_id,
                    order_id=order.order_id,
                    seller_id=order.seller_id,
                    return_date=return_date.strftime("%Y-%m-%d"),
                    return_reason=return_reason,
                    status=status
                )
                returns.append(return_data)
        
        logger.info(f"Generated {len(returns)} returns")
        return returns
    
    def generate_ratings(
        self,
        orders: List[OrderData],
        rating_rate: float = 0.6
    ) -> List[RatingData]:
        """
        Generate synthetic rating data based on orders.
        
        Args:
            orders: List of orders to potentially generate ratings for
            rating_rate: Rate at which orders receive ratings
        
        Returns:
            List of RatingData objects
        """
        logger.info(f"Generating ratings from {len(orders)} orders")
        
        ratings = []
        used_rating_ids = set()
        
        for order in orders:
            if self._rng.random() < rating_rate:
                # Generate unique rating ID
                while True:
                    rating_id = f"RAT-{self._rng.randint(100000, 999999)}"
                    if rating_id not in used_rating_ids:
                        used_rating_ids.add(rating_id)
                        break
                
                profile = self._seller_profiles.get(order.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE])
                rating = self._generate_rating(profile)
                
                # Rating date after order date
                order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
                rating_date = order_date + timedelta(days=self._rng.randint(1, 14))
                
                rating_data = RatingData(
                    rating_id=rating_id,
                    seller_id=order.seller_id,
                    order_id=order.order_id,
                    rating=rating,
                    rating_date=rating_date.strftime("%Y-%m-%d")
                )
                ratings.append(rating_data)
        
        logger.info(f"Generated {len(ratings)} ratings")
        return ratings
    
    def generate_reviews(
        self,
        orders: List[OrderData],
        review_rate: float = 0.4
    ) -> List[ReviewData]:
        """
        Generate synthetic review data based on orders.
        
        Args:
            orders: List of orders to potentially generate reviews for
            review_rate: Rate at which orders receive reviews
        
        Returns:
            List of ReviewData objects
        """
        logger.info(f"Generating reviews from {len(orders)} orders")
        
        reviews = []
        used_review_ids = set()
        
        for order in orders:
            if self._rng.random() < review_rate:
                # Generate unique review ID
                while True:
                    review_id = f"REV-{self._rng.randint(100000, 999999)}"
                    if review_id not in used_review_ids:
                        used_review_ids.add(review_id)
                        break
                
                profile = self._seller_profiles.get(order.seller_id, self.SELLER_PROFILES[SellerPerformance.AVERAGE])
                sentiment, sentiment_score = self._generate_sentiment(profile)
                
                # Select review template based on sentiment
                review_templates = self.REVIEW_TEMPLATES.get(sentiment, self.REVIEW_TEMPLATES["neutral"])
                review_text = self._rng.choice(review_templates)
                
                # Review date after order date
                order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
                review_date = order_date + timedelta(days=self._rng.randint(1, 21))
                
                review_data = ReviewData(
                    review_id=review_id,
                    seller_id=order.seller_id,
                    order_id=order.order_id,
                    review_date=review_date.strftime("%Y-%m-%d"),
                    review_text=review_text,
                    sentiment=sentiment,
                    sentiment_score=round(sentiment_score, 3)
                )
                reviews.append(review_data)
        
        logger.info(f"Generated {len(reviews)} reviews")
        return reviews


def create_generator(seed: int = None) -> MarketplaceDataGenerator:
    """
    Factory function to create a marketplace data generator.
    
    Args:
        seed: Random seed for reproducibility
    
    Returns:
        MarketplaceDataGenerator instance
    """
    return MarketplaceDataGenerator(seed)
