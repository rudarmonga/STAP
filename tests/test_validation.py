"""
Tests for data validation.
"""

import pytest
from datetime import datetime
from src.data.synthetic import (
    SellerData,
    OrderData,
    ReturnData,
    RatingData,
    ReviewData
)
from src.data.validation import DataValidator, ValidationError, create_validator


class TestDataValidator:
    """Test DataValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator for testing."""
        return DataValidator()
    
    @pytest.fixture
    def valid_seller(self):
        """Create a valid seller for testing."""
        return SellerData(
            seller_id="SELLER-12345",
            seller_name="Test Store",
            category="Electronics",
            region="North America",
            join_date="2023-01-15",
            status="active"
        )
    
    @pytest.fixture
    def valid_order(self):
        """Create a valid order for testing."""
        return OrderData(
            order_id="ORD-1234567",
            seller_id="SELLER-12345",
            order_date="2023-06-15",
            category="Electronics",
            region="North America",
            order_value=99.99,
            delivery_days=3,
            status="completed"
        )
    
    @pytest.fixture
    def valid_return(self):
        """Create a valid return for testing."""
        return ReturnData(
            return_id="RET-123456",
            order_id="ORD-1234567",
            seller_id="SELLER-12345",
            return_date="2023-06-20",
            return_reason="Defective product",
            status="approved"
        )
    
    @pytest.fixture
    def valid_rating(self):
        """Create a valid rating for testing."""
        return RatingData(
            rating_id="RAT-123456",
            seller_id="SELLER-12345",
            order_id="ORD-1234567",
            rating=5,
            rating_date="2023-06-18"
        )
    
    @pytest.fixture
    def valid_review(self):
        """Create a valid review for testing."""
        return ReviewData(
            review_id="REV-123456",
            seller_id="SELLER-12345",
            order_id="ORD-1234567",
            review_date="2023-06-18",
            review_text="Great product!",
            sentiment="positive",
            sentiment_score=0.9
        )
    
    def test_validator_initialization(self, validator):
        """Test that validator can be initialized."""
        assert validator is not None
        assert not validator.has_errors()
        assert len(validator.get_errors()) == 0
    
    def test_validate_sellers_success(self, validator, valid_seller):
        """Test successful seller validation."""
        result = validator.validate_sellers([valid_seller])
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_sellers_empty_list(self, validator):
        """Test validation with empty seller list."""
        result = validator.validate_sellers([])
        assert result is False
        assert validator.has_errors()
        assert "No sellers provided" in validator.get_errors()
    
    def test_validate_sellers_missing_seller_id(self, validator, valid_seller):
        """Test validation fails with missing seller_id."""
        valid_seller.seller_id = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_missing_seller_name(self, validator, valid_seller):
        """Test validation fails with missing seller_name."""
        valid_seller.seller_name = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_missing_category(self, validator, valid_seller):
        """Test validation fails with missing category."""
        valid_seller.category = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_missing_region(self, validator, valid_seller):
        """Test validation fails with missing region."""
        valid_seller.region = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_missing_join_date(self, validator, valid_seller):
        """Test validation fails with missing join_date."""
        valid_seller.join_date = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_missing_status(self, validator, valid_seller):
        """Test validation fails with missing status."""
        valid_seller.status = ""
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_invalid_category(self, validator, valid_seller):
        """Test validation fails with invalid category."""
        valid_seller.category = "Invalid Category"
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_invalid_region(self, validator, valid_seller):
        """Test validation fails with invalid region."""
        valid_seller.region = "Invalid Region"
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_invalid_status(self, validator, valid_seller):
        """Test validation fails with invalid status."""
        valid_seller.status = "invalid_status"
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_invalid_date_format(self, validator, valid_seller):
        """Test validation fails with invalid date format."""
        valid_seller.join_date = "2023/01/15"
        result = validator.validate_sellers([valid_seller])
        assert result is False
        assert validator.has_errors()
    
    def test_validate_sellers_duplicate_ids(self, validator, valid_seller):
        """Test validation fails with duplicate seller IDs."""
        result = validator.validate_sellers([valid_seller, valid_seller])
        assert result is False
        assert validator.has_errors()
        assert "Duplicate" in str(validator.get_errors())
    
    def test_validate_sellers_multiple_valid(self, validator):
        """Test validation with multiple valid sellers."""
        sellers = [
            SellerData(
                seller_id=f"SELLER-{i}",
                seller_name=f"Store {i}",
                category="Electronics",
                region="North America",
                join_date="2023-01-15",
                status="active"
            )
            for i in range(10)
        ]
        result = validator.validate_sellers(sellers)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_orders_success(self, validator, valid_order):
        """Test successful order validation."""
        seller_ids = {"SELLER-12345"}
        result = validator.validate_orders([valid_order], seller_ids)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_orders_empty_list(self, validator):
        """Test validation with empty order list."""
        result = validator.validate_orders([], set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_order_id(self, validator, valid_order):
        """Test validation fails with missing order_id."""
        valid_order.order_id = ""
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_seller_id(self, validator, valid_order):
        """Test validation fails with missing seller_id."""
        valid_order.seller_id = ""
        result = validator.validate_orders([valid_order], set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_order_date(self, validator, valid_order):
        """Test validation fails with missing order_date."""
        valid_order.order_date = ""
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_category(self, validator, valid_order):
        """Test validation fails with missing category."""
        valid_order.category = ""
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_region(self, validator, valid_order):
        """Test validation fails with missing region."""
        valid_order.region = ""
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_order_value(self, validator, valid_order):
        """Test validation fails with missing order_value."""
        valid_order.order_value = None
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_delivery_days(self, validator, valid_order):
        """Test validation fails with missing delivery_days."""
        valid_order.delivery_days = None
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_missing_status(self, validator, valid_order):
        """Test validation fails with missing status."""
        valid_order.status = ""
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_invalid_seller_id(self, validator, valid_order):
        """Test validation fails with invalid seller_id."""
        result = validator.validate_orders([valid_order], {"SELLER-99999"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_invalid_category(self, validator, valid_order):
        """Test validation fails with invalid category."""
        valid_order.category = "Invalid Category"
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_invalid_region(self, validator, valid_order):
        """Test validation fails with invalid region."""
        valid_order.region = "Invalid Region"
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_negative_order_value(self, validator, valid_order):
        """Test validation fails with negative order_value."""
        valid_order.order_value = -10.0
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_negative_delivery_days(self, validator, valid_order):
        """Test validation fails with negative delivery_days."""
        valid_order.delivery_days = -5
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_invalid_status(self, validator, valid_order):
        """Test validation fails with invalid status."""
        valid_order.status = "invalid_status"
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_invalid_date_format(self, validator, valid_order):
        """Test validation fails with invalid date format."""
        valid_order.order_date = "2023/06/15"
        result = validator.validate_orders([valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_orders_duplicate_ids(self, validator, valid_order):
        """Test validation fails with duplicate order IDs."""
        result = validator.validate_orders([valid_order, valid_order], {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_success(self, validator, valid_return):
        """Test successful return validation."""
        order_ids = {"ORD-1234567"}
        seller_ids = {"SELLER-12345"}
        result = validator.validate_returns([valid_return], order_ids, seller_ids)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_returns_empty_list(self, validator):
        """Test validation with empty return list."""
        result = validator.validate_returns([], set(), set())
        assert result is True  # Empty returns is valid
    
    def test_validate_returns_missing_return_id(self, validator, valid_return):
        """Test validation fails with missing return_id."""
        valid_return.return_id = ""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_missing_order_id(self, validator, valid_return):
        """Test validation fails with missing order_id."""
        valid_return.order_id = ""
        result = validator.validate_returns([valid_return], set(), {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_missing_seller_id(self, validator, valid_return):
        """Test validation fails with missing seller_id."""
        valid_return.seller_id = ""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_missing_return_date(self, validator, valid_return):
        """Test validation fails with missing return_date."""
        valid_return.return_date = ""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_missing_return_reason(self, validator, valid_return):
        """Test validation fails with missing return_reason."""
        valid_return.return_reason = ""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_missing_status(self, validator, valid_return):
        """Test validation fails with missing status."""
        valid_return.status = ""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_invalid_order_id(self, validator, valid_return):
        """Test validation fails with invalid order_id."""
        result = validator.validate_returns([valid_return], {"ORD-999999"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_invalid_seller_id(self, validator, valid_return):
        """Test validation fails with invalid seller_id."""
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-99999"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_invalid_status(self, validator, valid_return):
        """Test validation fails with invalid status."""
        valid_return.status = "invalid_status"
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_invalid_date_format(self, validator, valid_return):
        """Test validation fails with invalid date format."""
        valid_return.return_date = "2023/06/20"
        result = validator.validate_returns([valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_returns_duplicate_ids(self, validator, valid_return):
        """Test validation fails with duplicate return IDs."""
        result = validator.validate_returns([valid_return, valid_return], {"ORD-1234567"}, {"SELLER-12345"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_success(self, validator, valid_rating):
        """Test successful rating validation."""
        seller_ids = {"SELLER-12345"}
        order_ids = {"ORD-1234567"}
        result = validator.validate_ratings([valid_rating], seller_ids, order_ids)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_ratings_empty_list(self, validator):
        """Test validation with empty rating list."""
        result = validator.validate_ratings([], set(), set())
        assert result is True  # Empty ratings is valid
    
    def test_validate_ratings_missing_rating_id(self, validator, valid_rating):
        """Test validation fails with missing rating_id."""
        valid_rating.rating_id = ""
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_missing_seller_id(self, validator, valid_rating):
        """Test validation fails with missing seller_id."""
        valid_rating.seller_id = ""
        result = validator.validate_ratings([valid_rating], set(), set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_missing_rating(self, validator, valid_rating):
        """Test validation fails with missing rating."""
        valid_rating.rating = None
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_missing_rating_date(self, validator, valid_rating):
        """Test validation fails with missing rating_date."""
        valid_rating.rating_date = ""
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_invalid_seller_id(self, validator, valid_rating):
        """Test validation fails with invalid seller_id."""
        result = validator.validate_ratings([valid_rating], {"SELLER-99999"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_invalid_order_id(self, validator, valid_rating):
        """Test validation fails with invalid order_id."""
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, {"ORD-999999"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_rating_too_low(self, validator, valid_rating):
        """Test validation fails with rating too low."""
        valid_rating.rating = 0
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_rating_too_high(self, validator, valid_rating):
        """Test validation fails with rating too high."""
        valid_rating.rating = 6
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_invalid_date_format(self, validator, valid_rating):
        """Test validation fails with invalid date format."""
        valid_rating.rating_date = "2023/06/18"
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_duplicate_ids(self, validator, valid_rating):
        """Test validation fails with duplicate rating IDs."""
        result = validator.validate_ratings([valid_rating, valid_rating], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_ratings_without_order_id(self, validator, valid_rating):
        """Test validation succeeds with None order_id."""
        valid_rating.order_id = None
        result = validator.validate_ratings([valid_rating], {"SELLER-12345"}, set())
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_reviews_success(self, validator, valid_review):
        """Test successful review validation."""
        seller_ids = {"SELLER-12345"}
        order_ids = {"ORD-1234567"}
        result = validator.validate_reviews([valid_review], seller_ids, order_ids)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_reviews_empty_list(self, validator):
        """Test validation with empty review list."""
        result = validator.validate_reviews([], set(), set())
        assert result is True  # Empty reviews is valid
    
    def test_validate_reviews_missing_review_id(self, validator, valid_review):
        """Test validation fails with missing review_id."""
        valid_review.review_id = ""
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_missing_seller_id(self, validator, valid_review):
        """Test validation fails with missing seller_id."""
        valid_review.seller_id = ""
        result = validator.validate_reviews([valid_review], set(), set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_missing_review_date(self, validator, valid_review):
        """Test validation fails with missing review_date."""
        valid_review.review_date = ""
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_missing_review_text(self, validator, valid_review):
        """Test validation fails with missing review_text."""
        valid_review.review_text = ""
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_invalid_seller_id(self, validator, valid_review):
        """Test validation fails with invalid seller_id."""
        result = validator.validate_reviews([valid_review], {"SELLER-99999"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_invalid_order_id(self, validator, valid_review):
        """Test validation fails with invalid order_id."""
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, {"ORD-999999"})
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_invalid_sentiment(self, validator, valid_review):
        """Test validation fails with invalid sentiment."""
        valid_review.sentiment = "invalid_sentiment"
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_sentiment_score_too_low(self, validator, valid_review):
        """Test validation fails with sentiment score too low."""
        valid_review.sentiment_score = -1.5
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_sentiment_score_too_high(self, validator, valid_review):
        """Test validation fails with sentiment score too high."""
        valid_review.sentiment_score = 1.5
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_invalid_date_format(self, validator, valid_review):
        """Test validation fails with invalid date format."""
        valid_review.review_date = "2023/06/18"
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_duplicate_ids(self, validator, valid_review):
        """Test validation fails with duplicate review IDs."""
        result = validator.validate_reviews([valid_review, valid_review], {"SELLER-12345"}, set())
        assert result is False
        assert validator.has_errors()
    
    def test_validate_reviews_without_order_id(self, validator, valid_review):
        """Test validation succeeds with None order_id."""
        valid_review.order_id = None
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_reviews_without_sentiment(self, validator, valid_review):
        """Test validation succeeds with None sentiment."""
        valid_review.sentiment = None
        valid_review.sentiment_score = None
        result = validator.validate_reviews([valid_review], {"SELLER-12345"}, set())
        assert result is True
        assert not validator.has_errors()
    
    def test_get_errors(self, validator, valid_seller):
        """Test getting validation errors."""
        valid_seller.seller_id = ""
        validator.validate_sellers([valid_seller])
        errors = validator.get_errors()
        assert len(errors) > 0
        assert isinstance(errors, list)
    
    def test_has_errors(self, validator, valid_seller):
        """Test checking for validation errors."""
        assert not validator.has_errors()
        valid_seller.seller_id = ""
        validator.validate_sellers([valid_seller])
        assert validator.has_errors()
    
    def test_error_reset_between_validations(self, validator, valid_seller):
        """Test that errors are reset between validations."""
        valid_seller.seller_id = ""
        validator.validate_sellers([valid_seller])
        assert validator.has_errors()
        
        # Next validation should reset errors
        valid_seller.seller_id = "SELLER-12345"
        validator.validate_sellers([valid_seller])
        assert not validator.has_errors()


class TestCreateValidator:
    """Test factory function for creating validators."""
    
    def test_create_validator(self):
        """Test creating a validator."""
        validator = create_validator()
        assert validator is not None
        assert isinstance(validator, DataValidator)
    
    def test_create_validator_is_fresh(self):
        """Test that created validator has no errors."""
        validator = create_validator()
        assert not validator.has_errors()
        assert len(validator.get_errors()) == 0