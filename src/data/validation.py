"""
Data validation for STAP synthetic data.

This module provides validation functions to ensure synthetic data meets
quality standards before being inserted into the database.
"""

from typing import List, Dict, Any
from datetime import datetime
from src.data.synthetic import (
    SellerData, OrderData, ReturnData, RatingData, ReviewData
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataValidator:
    """Validates synthetic data before database insertion."""
    
    # Valid values for enum-like fields
    VALID_SELLER_STATUSES = {"active", "inactive", "suspended"}
    VALID_ORDER_STATUSES = {"completed", "cancelled", "pending", "refunded"}
    VALID_RETURN_STATUSES = {"approved", "rejected", "pending"}
    VALID_SENTIMENTS = {"positive", "neutral", "negative"}
    VALID_CATEGORIES = {
        "Electronics", "Clothing", "Home & Garden", "Sports",
        "Books", "Toys", "Automotive", "Health & Beauty",
        "Food & Grocery", "Office Supplies"
    }
    VALID_REGIONS = {
        "North America", "Europe", "Asia Pacific",
        "Latin America", "Middle East", "Africa"
    }
    
    def __init__(self):
        self._errors: List[str] = []
    
    def validate_sellers(self, sellers: List[SellerData]) -> bool:
        """
        Validate seller data.
        
        Args:
            sellers: List of SellerData objects to validate
        
        Returns:
            True if validation passes, False otherwise
        """
        self._errors = []
        
        if not sellers:
            self._errors.append("No sellers provided")
            return False
        
        seller_ids = set()
        
        for i, seller in enumerate(sellers):
            try:
                # Check required fields
                if not seller.seller_id:
                    self._errors.append(f"Seller {i}: Missing seller_id")
                if not seller.seller_name:
                    self._errors.append(f"Seller {i}: Missing seller_name")
                if not seller.category:
                    self._errors.append(f"Seller {i}: Missing category")
                if not seller.region:
                    self._errors.append(f"Seller {i}: Missing region")
                if not seller.join_date:
                    self._errors.append(f"Seller {i}: Missing join_date")
                if not seller.status:
                    self._errors.append(f"Seller {i}: Missing status")
                
                # Validate field formats
                if seller.category and seller.category not in self.VALID_CATEGORIES:
                    self._errors.append(f"Seller {i}: Invalid category '{seller.category}'")
                
                if seller.region and seller.region not in self.VALID_REGIONS:
                    self._errors.append(f"Seller {i}: Invalid region '{seller.region}'")
                
                if seller.status and seller.status not in self.VALID_SELLER_STATUSES:
                    self._errors.append(f"Seller {i}: Invalid status '{seller.status}'")
                
                # Validate date format
                if seller.join_date:
                    try:
                        datetime.strptime(seller.join_date, "%Y-%m-%d")
                    except ValueError:
                        self._errors.append(f"Seller {i}: Invalid join_date format '{seller.join_date}'")
                
                # Check for duplicate seller IDs
                if seller.seller_id:
                    if seller.seller_id in seller_ids:
                        self._errors.append(f"Seller {i}: Duplicate seller_id '{seller.seller_id}'")
                    seller_ids.add(seller.seller_id)
                
            except Exception as e:
                self._errors.append(f"Seller {i}: Unexpected error {e}")
        
        if self._errors:
            logger.error(f"Seller validation failed: {self._errors}")
            return False
        
        logger.info(f"Validated {len(sellers)} sellers successfully")
        return True
    
    def validate_orders(
        self, 
        orders: List[OrderData], 
        seller_ids: set
    ) -> bool:
        """
        Validate order data.
        
        Args:
            orders: List of OrderData objects to validate
            seller_ids: Set of valid seller IDs
        
        Returns:
            True if validation passes, False otherwise
        """
        self._errors = []
        
        if not orders:
            self._errors.append("No orders provided")
            return False
        
        order_ids = set()
        
        for i, order in enumerate(orders):
            try:
                # Check required fields
                if not order.order_id:
                    self._errors.append(f"Order {i}: Missing order_id")
                if not order.seller_id:
                    self._errors.append(f"Order {i}: Missing seller_id")
                if not order.order_date:
                    self._errors.append(f"Order {i}: Missing order_date")
                if not order.category:
                    self._errors.append(f"Order {i}: Missing category")
                if not order.region:
                    self._errors.append(f"Order {i}: Missing region")
                if order.order_value is None:
                    self._errors.append(f"Order {i}: Missing order_value")
                if order.delivery_days is None:
                    self._errors.append(f"Order {i}: Missing delivery_days")
                if not order.status:
                    self._errors.append(f"Order {i}: Missing status")
                
                # Validate field values
                if order.seller_id and order.seller_id not in seller_ids:
                    self._errors.append(f"Order {i}: Invalid seller_id '{order.seller_id}' (not in sellers)")
                
                if order.category and order.category not in self.VALID_CATEGORIES:
                    self._errors.append(f"Order {i}: Invalid category '{order.category}'")
                
                if order.region and order.region not in self.VALID_REGIONS:
                    self._errors.append(f"Order {i}: Invalid region '{order.region}'")
                
                if order.order_value is not None and order.order_value < 0:
                    self._errors.append(f"Order {i}: Negative order_value '{order.order_value}'")
                
                if order.delivery_days is not None and order.delivery_days < 0:
                    self._errors.append(f"Order {i}: Negative delivery_days '{order.delivery_days}'")
                
                if order.status and order.status not in self.VALID_ORDER_STATUSES:
                    self._errors.append(f"Order {i}: Invalid status '{order.status}'")
                
                # Validate date format
                if order.order_date:
                    try:
                        datetime.strptime(order.order_date, "%Y-%m-%d")
                    except ValueError:
                        self._errors.append(f"Order {i}: Invalid order_date format '{order.order_date}'")
                
                # Check for duplicate order IDs
                if order.order_id:
                    if order.order_id in order_ids:
                        self._errors.append(f"Order {i}: Duplicate order_id '{order.order_id}'")
                    order_ids.add(order.order_id)
                
            except Exception as e:
                self._errors.append(f"Order {i}: Unexpected error {e}")
        
        if self._errors:
            logger.error(f"Order validation failed: {self._errors}")
            return False
        
        logger.info(f"Validated {len(orders)} orders successfully")
        return True
    
    def validate_returns(
        self, 
        returns: List[ReturnData], 
        order_ids: set,
        seller_ids: set
    ) -> bool:
        """
        Validate return data.
        
        Args:
            returns: List of ReturnData objects to validate
            order_ids: Set of valid order IDs
            seller_ids: Set of valid seller IDs
        
        Returns:
            True if validation passes, False otherwise
        """
        self._errors = []
        
        if not returns:
            logger.info("No returns to validate")
            return True
        
        return_ids = set()
        
        for i, return_data in enumerate(returns):
            try:
                # Check required fields
                if not return_data.return_id:
                    self._errors.append(f"Return {i}: Missing return_id")
                if not return_data.order_id:
                    self._errors.append(f"Return {i}: Missing order_id")
                if not return_data.seller_id:
                    self._errors.append(f"Return {i}: Missing seller_id")
                if not return_data.return_date:
                    self._errors.append(f"Return {i}: Missing return_date")
                if not return_data.return_reason:
                    self._errors.append(f"Return {i}: Missing return_reason")
                if not return_data.status:
                    self._errors.append(f"Return {i}: Missing status")
                
                # Validate foreign keys
                if return_data.order_id and return_data.order_id not in order_ids:
                    self._errors.append(f"Return {i}: Invalid order_id '{return_data.order_id}' (not in orders)")
                
                if return_data.seller_id and return_data.seller_id not in seller_ids:
                    self._errors.append(f"Return {i}: Invalid seller_id '{return_data.seller_id}' (not in sellers)")
                
                # Validate field values
                if return_data.status and return_data.status not in self.VALID_RETURN_STATUSES:
                    self._errors.append(f"Return {i}: Invalid status '{return_data.status}'")
                
                # Validate date format
                if return_data.return_date:
                    try:
                        datetime.strptime(return_data.return_date, "%Y-%m-%d")
                    except ValueError:
                        self._errors.append(f"Return {i}: Invalid return_date format '{return_data.return_date}'")
                
                # Check for duplicate return IDs
                if return_data.return_id:
                    if return_data.return_id in return_ids:
                        self._errors.append(f"Return {i}: Duplicate return_id '{return_data.return_id}'")
                    return_ids.add(return_data.return_id)
                
            except Exception as e:
                self._errors.append(f"Return {i}: Unexpected error {e}")
        
        if self._errors:
            logger.error(f"Return validation failed: {self._errors}")
            return False
        
        logger.info(f"Validated {len(returns)} returns successfully")
        return True
    
    def validate_ratings(
        self, 
        ratings: List[RatingData], 
        seller_ids: set,
        order_ids: set = None
    ) -> bool:
        """
        Validate rating data.
        
        Args:
            ratings: List of RatingData objects to validate
            seller_ids: Set of valid seller IDs
            order_ids: Set of valid order IDs (optional)
        
        Returns:
            True if validation passes, False otherwise
        """
        self._errors = []
        
        if not ratings:
            logger.info("No ratings to validate")
            return True
        
        rating_ids = set()
        
        for i, rating in enumerate(ratings):
            try:
                # Check required fields
                if not rating.rating_id:
                    self._errors.append(f"Rating {i}: Missing rating_id")
                if not rating.seller_id:
                    self._errors.append(f"Rating {i}: Missing seller_id")
                if rating.rating is None:
                    self._errors.append(f"Rating {i}: Missing rating")
                if not rating.rating_date:
                    self._errors.append(f"Rating {i}: Missing rating_date")
                
                # Validate foreign keys
                if rating.seller_id and rating.seller_id not in seller_ids:
                    self._errors.append(f"Rating {i}: Invalid seller_id '{rating.seller_id}' (not in sellers)")
                
                if rating.order_id and order_ids and rating.order_id not in order_ids:
                    self._errors.append(f"Rating {i}: Invalid order_id '{rating.order_id}' (not in orders)")
                
                # Validate rating range
                if rating.rating is not None and (rating.rating < 1 or rating.rating > 5):
                    self._errors.append(f"Rating {i}: Rating {rating.rating} out of range (1-5)")
                
                # Validate date format
                if rating.rating_date:
                    try:
                        datetime.strptime(rating.rating_date, "%Y-%m-%d")
                    except ValueError:
                        self._errors.append(f"Rating {i}: Invalid rating_date format '{rating.rating_date}'")
                
                # Check for duplicate rating IDs
                if rating.rating_id:
                    if rating.rating_id in rating_ids:
                        self._errors.append(f"Rating {i}: Duplicate rating_id '{rating.rating_id}'")
                    rating_ids.add(rating.rating_id)
                
            except Exception as e:
                self._errors.append(f"Rating {i}: Unexpected error {e}")
        
        if self._errors:
            logger.error(f"Rating validation failed: {self._errors}")
            return False
        
        logger.info(f"Validated {len(ratings)} ratings successfully")
        return True
    
    def validate_reviews(
        self, 
        reviews: List[ReviewData], 
        seller_ids: set,
        order_ids: set = None
    ) -> bool:
        """
        Validate review data.
        
        Args:
            reviews: List of ReviewData objects to validate
            seller_ids: Set of valid seller IDs
            order_ids: Set of valid order IDs (optional)
        
        Returns:
            True if validation passes, False otherwise
        """
        self._errors = []
        
        if not reviews:
            logger.info("No reviews to validate")
            return True
        
        review_ids = set()
        
        for i, review in enumerate(reviews):
            try:
                # Check required fields
                if not review.review_id:
                    self._errors.append(f"Review {i}: Missing review_id")
                if not review.seller_id:
                    self._errors.append(f"Review {i}: Missing seller_id")
                if not review.review_date:
                    self._errors.append(f"Review {i}: Missing review_date")
                if not review.review_text:
                    self._errors.append(f"Review {i}: Missing review_text")
                
                # Validate foreign keys
                if review.seller_id and review.seller_id not in seller_ids:
                    self._errors.append(f"Review {i}: Invalid seller_id '{review.seller_id}' (not in sellers)")
                
                if review.order_id and order_ids and review.order_id not in order_ids:
                    self._errors.append(f"Review {i}: Invalid order_id '{review.order_id}' (not in orders)")
                
                # Validate sentiment
                if review.sentiment and review.sentiment not in self.VALID_SENTIMENTS:
                    self._errors.append(f"Review {i}: Invalid sentiment '{review.sentiment}'")
                
                # Validate sentiment score range
                if review.sentiment_score is not None:
                    if review.sentiment_score < -1 or review.sentiment_score > 1:
                        self._errors.append(f"Review {i}: Sentiment score {review.sentiment_score} out of range (-1 to 1)")
                
                # Validate date format
                if review.review_date:
                    try:
                        datetime.strptime(review.review_date, "%Y-%m-%d")
                    except ValueError:
                        self._errors.append(f"Review {i}: Invalid review_date format '{review.review_date}'")
                
                # Check for duplicate review IDs
                if review.review_id:
                    if review.review_id in review_ids:
                        self._errors.append(f"Review {i}: Duplicate review_id '{review.review_id}'")
                    review_ids.add(review.review_id)
                
            except Exception as e:
                self._errors.append(f"Review {i}: Unexpected error {e}")
        
        if self._errors:
            logger.error(f"Review validation failed: {self._errors}")
            return False
        
        logger.info(f"Validated {len(reviews)} reviews successfully")
        return True
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self._errors
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self._errors) > 0


def create_validator() -> DataValidator:
    """Factory function to create a data validator."""
    return DataValidator()
