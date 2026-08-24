"""
Tests for synthetic data generation.
"""

import pytest
from datetime import datetime, timedelta
from src.data.synthetic import (
    SyntheticDataGenerator,
    MarketplaceDataGenerator,
    SellerData,
    OrderData,
    ReturnData,
    RatingData,
    ReviewData,
    SellerPerformance,
    create_generator
)


class TestSyntheticDataGenerator:
    """Test base SyntheticDataGenerator class."""
    
    def test_generator_initialization(self):
        """Test that generator can be initialized."""
        gen = SyntheticDataGenerator(seed=42)
        assert gen is not None
        assert gen.seed == 42
    
    def test_generator_initialization_with_default_seed(self):
        """Test generator initialization with default seed."""
        gen = SyntheticDataGenerator()
        assert gen is not None
        assert gen.seed is not None
    
    def test_reset_seed(self):
        """Test seed reset functionality."""
        gen = SyntheticDataGenerator(seed=42)
        gen.reset_seed(100)
        assert gen.seed == 100
    
    def test_generate_seller_id(self):
        """Test seller ID generation."""
        gen = SyntheticDataGenerator(seed=42)
        seller_id = gen.generate_seller_id()
        assert seller_id.startswith("SELLER-")
        assert len(seller_id) > 7
    
    def test_generate_product_id(self):
        """Test product ID generation."""
        gen = SyntheticDataGenerator(seed=42)
        product_id = gen.generate_product_id()
        assert product_id.startswith("PROD-")
        assert len(product_id) > 5
    
    def test_generate_order_id(self):
        """Test order ID generation."""
        gen = SyntheticDataGenerator(seed=42)
        order_id = gen.generate_order_id()
        assert order_id.startswith("ORD-")
        assert len(order_id) > 4
    
    def test_generate_date_range(self):
        """Test date range generation."""
        gen = SyntheticDataGenerator(seed=42)
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
        dates = gen.generate_date_range(start, end, 10)
        assert len(dates) == 10
        for date in dates:
            assert start <= date <= end
    
    def test_generate_category(self):
        """Test category generation."""
        gen = SyntheticDataGenerator(seed=42)
        category = gen.generate_category()
        assert category is not None
        assert isinstance(category, str)
    
    def test_generate_region(self):
        """Test region generation."""
        gen = SyntheticDataGenerator(seed=42)
        region = gen.generate_region()
        assert region is not None
        assert isinstance(region, str)
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        gen1 = SyntheticDataGenerator(seed=42)
        gen2 = SyntheticDataGenerator(seed=42)
        
        id1 = gen1.generate_seller_id()
        id2 = gen2.generate_seller_id()
        
        assert id1 == id2


class TestMarketplaceDataGenerator:
    """Test MarketplaceDataGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create a generator for testing."""
        return MarketplaceDataGenerator(seed=42)
    
    def test_generator_initialization(self, generator):
        """Test marketplace generator initialization."""
        assert generator is not None
        assert generator.seed == 42
    
    def test_generate_sellers_basic(self, generator):
        """Test basic seller generation."""
        sellers = generator.generate_sellers(count=10)
        assert len(sellers) == 10
        assert all(isinstance(s, SellerData) for s in sellers)
    
    def test_generate_sellers_with_custom_count(self, generator):
        """Test seller generation with custom count."""
        sellers = generator.generate_sellers(count=50)
        assert len(sellers) == 50
    
    def test_generate_sellers_unique_ids(self, generator):
        """Test that seller IDs are unique."""
        sellers = generator.generate_sellers(count=100)
        seller_ids = [s.seller_id for s in sellers]
        assert len(seller_ids) == len(set(seller_ids))
    
    def test_generate_sellers_unique_names(self, generator):
        """Test that seller names are unique."""
        sellers = generator.generate_sellers(count=100)
        seller_names = [s.seller_name for s in sellers]
        assert len(seller_names) == len(set(seller_names))
    
    def test_generate_sellers_valid_categories(self, generator):
        """Test that sellers have valid categories."""
        sellers = generator.generate_sellers(count=50)
        valid_categories = generator.CATEGORIES
        for seller in sellers:
            assert seller.category in valid_categories
    
    def test_generate_sellers_valid_regions(self, generator):
        """Test that sellers have valid regions."""
        sellers = generator.generate_sellers(count=50)
        valid_regions = generator.REGIONS
        for seller in sellers:
            assert seller.region in valid_regions
    
    def test_generate_sellers_valid_status(self, generator):
        """Test that sellers have valid status."""
        sellers = generator.generate_sellers(count=50)
        for seller in sellers:
            assert seller.status in ["active", "inactive", "suspended"]
    
    def test_generate_sellers_historical_dates(self, generator):
        """Test that seller join dates are historical."""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        sellers = generator.generate_sellers(count=50, start_date=start_date, end_date=end_date)
        
        for seller in sellers:
            join_date = datetime.strptime(seller.join_date, "%Y-%m-%d")
            assert start_date <= join_date <= end_date
    
    def test_generate_orders_basic(self, generator):
        """Test basic order generation."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        assert len(orders) == 50
        assert all(isinstance(o, OrderData) for o in orders)
    
    def test_generate_orders_without_sellers(self, generator):
        """Test order generation without sellers returns empty."""
        orders = generator.generate_orders(sellers=[], count=50)
        assert len(orders) == 0
    
    def test_generate_orders_valid_seller_ids(self, generator):
        """Test that orders reference valid seller IDs."""
        sellers = generator.generate_sellers(count=20)
        seller_ids = {s.seller_id for s in sellers}
        orders = generator.generate_orders(sellers=sellers, count=100)
        
        for order in orders:
            assert order.seller_id in seller_ids
    
    def test_generate_orders_unique_ids(self, generator):
        """Test that order IDs are unique."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=200)
        order_ids = [o.order_id for o in orders]
        assert len(order_ids) == len(set(order_ids))
    
    def test_generate_orders_valid_categories(self, generator):
        """Test that orders have valid categories."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        valid_categories = generator.CATEGORIES
        
        for order in orders:
            assert order.category in valid_categories
    
    def test_generate_orders_valid_regions(self, generator):
        """Test that orders have valid regions."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        valid_regions = generator.REGIONS
        
        for order in orders:
            assert order.region in valid_regions
    
    def test_generate_orders_positive_values(self, generator):
        """Test that order values are positive."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        
        for order in orders:
            assert order.order_value >= 0
    
    def test_generate_orders_valid_delivery_days(self, generator):
        """Test that delivery days are non-negative."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        
        for order in orders:
            assert order.delivery_days >= 0
    
    def test_generate_orders_valid_status(self, generator):
        """Test that orders have valid status."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        valid_statuses = ["completed", "cancelled", "pending", "refunded"]
        
        for order in orders:
            assert order.status in valid_statuses
    
    def test_generate_orders_historical_dates(self, generator):
        """Test that order dates are historical."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50, days_back=365)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        for order in orders:
            order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
            assert start_date <= order_date <= end_date
    
    def test_generate_returns_basic(self, generator):
        """Test basic return generation."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        returns = generator.generate_returns(orders=orders)
        
        assert all(isinstance(r, ReturnData) for r in returns)
    
    def test_generate_returns_valid_order_ids(self, generator):
        """Test that returns reference valid order IDs."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        order_ids = {o.order_id for o in orders}
        returns = generator.generate_returns(orders=orders)
        
        for return_data in returns:
            assert return_data.order_id in order_ids
    
    def test_generate_returns_valid_seller_ids(self, generator):
        """Test that returns reference valid seller IDs."""
        sellers = generator.generate_sellers(count=10)
        seller_ids = {s.seller_id for s in sellers}
        orders = generator.generate_orders(sellers=sellers, count=50)
        returns = generator.generate_returns(orders=orders)
        
        for return_data in returns:
            assert return_data.seller_id in seller_ids
    
    def test_generate_returns_unique_ids(self, generator):
        """Test that return IDs are unique."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        returns = generator.generate_returns(orders=orders)
        return_ids = [r.return_id for r in returns]
        assert len(return_ids) == len(set(return_ids))
    
    def test_generate_returns_valid_status(self, generator):
        """Test that returns have valid status."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        returns = generator.generate_returns(orders=orders)
        valid_statuses = ["approved", "rejected", "pending"]
        
        for return_data in returns:
            assert return_data.status in valid_statuses
    
    def test_generate_returns_date_after_order(self, generator):
        """Test that return dates are after order dates."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        returns = generator.generate_returns(orders=orders)
        
        order_map = {o.order_id: o for o in orders}
        for return_data in returns:
            order = order_map[return_data.order_id]
            return_date = datetime.strptime(return_data.return_date, "%Y-%m-%d")
            order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
            assert return_date >= order_date
    
    def test_generate_ratings_basic(self, generator):
        """Test basic rating generation."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        ratings = generator.generate_ratings(orders=orders)
        
        assert all(isinstance(r, RatingData) for r in ratings)
    
    def test_generate_ratings_valid_seller_ids(self, generator):
        """Test that ratings reference valid seller IDs."""
        sellers = generator.generate_sellers(count=10)
        seller_ids = {s.seller_id for s in sellers}
        orders = generator.generate_orders(sellers=sellers, count=50)
        ratings = generator.generate_ratings(orders=orders)
        
        for rating in ratings:
            assert rating.seller_id in seller_ids
    
    def test_generate_ratings_valid_order_ids(self, generator):
        """Test that ratings reference valid order IDs."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        order_ids = {o.order_id for o in orders}
        ratings = generator.generate_ratings(orders=orders)
        
        for rating in ratings:
            if rating.order_id:
                assert rating.order_id in order_ids
    
    def test_generate_ratings_unique_ids(self, generator):
        """Test that rating IDs are unique."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        ratings = generator.generate_ratings(orders=orders)
        rating_ids = [r.rating_id for r in ratings]
        assert len(rating_ids) == len(set(rating_ids))
    
    def test_generate_ratings_valid_range(self, generator):
        """Test that ratings are within valid range."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        ratings = generator.generate_ratings(orders=orders)
        
        for rating in ratings:
            assert 1 <= rating.rating <= 5
    
    def test_generate_ratings_date_after_order(self, generator):
        """Test that rating dates are after order dates."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        ratings = generator.generate_ratings(orders=orders)
        
        order_map = {o.order_id: o for o in orders}
        for rating in ratings:
            if rating.order_id and rating.order_id in order_map:
                order = order_map[rating.order_id]
                rating_date = datetime.strptime(rating.rating_date, "%Y-%m-%d")
                order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
                assert rating_date >= order_date
    
    def test_generate_reviews_basic(self, generator):
        """Test basic review generation."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        
        assert all(isinstance(r, ReviewData) for r in reviews)
    
    def test_generate_reviews_valid_seller_ids(self, generator):
        """Test that reviews reference valid seller IDs."""
        sellers = generator.generate_sellers(count=10)
        seller_ids = {s.seller_id for s in sellers}
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        
        for review in reviews:
            assert review.seller_id in seller_ids
    
    def test_generate_reviews_valid_order_ids(self, generator):
        """Test that reviews reference valid order IDs."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        order_ids = {o.order_id for o in orders}
        reviews = generator.generate_reviews(orders=orders)
        
        for review in reviews:
            if review.order_id:
                assert review.order_id in order_ids
    
    def test_generate_reviews_unique_ids(self, generator):
        """Test that review IDs are unique."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        review_ids = [r.review_id for r in reviews]
        assert len(review_ids) == len(set(review_ids))
    
    def test_generate_reviews_valid_sentiment(self, generator):
        """Test that reviews have valid sentiment."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        valid_sentiments = ["positive", "neutral", "negative"]
        
        for review in reviews:
            if review.sentiment:
                assert review.sentiment in valid_sentiments
    
    def test_generate_reviews_valid_sentiment_score(self, generator):
        """Test that sentiment scores are within valid range."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        
        for review in reviews:
            if review.sentiment_score is not None:
                assert -1 <= review.sentiment_score <= 1
    
    def test_generate_reviews_has_text(self, generator):
        """Test that reviews have text content."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        
        for review in reviews:
            assert len(review.review_text) > 0
    
    def test_generate_reviews_date_after_order(self, generator):
        """Test that review dates are after order dates."""
        sellers = generator.generate_sellers(count=10)
        orders = generator.generate_orders(sellers=sellers, count=50)
        reviews = generator.generate_reviews(orders=orders)
        
        order_map = {o.order_id: o for o in orders}
        for review in reviews:
            if review.order_id and review.order_id in order_map:
                order = order_map[review.order_id]
                review_date = datetime.strptime(review.review_date, "%Y-%m-%d")
                order_date = datetime.strptime(order.order_date, "%Y-%m-%d")
                assert review_date >= order_date
    
    def test_performance_profile_assignment(self, generator):
        """Test that sellers get performance profiles assigned."""
        sellers = generator.generate_sellers(count=100)
        
        # Check that profiles were assigned
        assert len(generator._seller_profiles) > 0
        
        # Check that all sellers have profiles
        for seller in sellers:
            assert seller.seller_id in generator._seller_profiles
    
    def test_performance_profile_distribution(self, generator):
        """Test that performance profiles follow expected distribution."""
        sellers = generator.generate_sellers(count=1000)
        
        profile_counts = {}
        for seller in sellers:
            profile = generator._seller_profiles[seller.seller_id]
            profile_type = profile.performance_type
            profile_counts[profile_type] = profile_counts.get(profile_type, 0) + 1
        
        # Expected distribution: 40% healthy, 30% average, 20% declining, 10% high risk
        total = len(sellers)
        assert profile_counts[SellerPerformance.HEALTHY] >= total * 0.35  # At least 35%
        assert profile_counts[SellerPerformance.AVERAGE] >= total * 0.25  # At least 25%
        assert profile_counts[SellerPerformance.DECLINING] >= total * 0.15  # At least 15%
        assert profile_counts[SellerPerformance.HIGH_RISK] >= total * 0.05  # At least 5%
    
    def test_high_risk_sellers_have_higher_return_rates(self, generator):
        """Test that high-risk sellers have higher return rates."""
        sellers = generator.generate_sellers(count=100)
        orders = generator.generate_orders(sellers=sellers, count=1000)
        returns = generator.generate_returns(orders=orders)
        
        # Group returns by seller
        seller_returns = {}
        for ret in returns:
            seller_returns[ret.seller_id] = seller_returns.get(ret.seller_id, 0) + 1
        
        # Group orders by seller
        seller_orders = {}
        for order in orders:
            seller_orders[order.seller_id] = seller_orders.get(order.seller_id, 0) + 1
        
        # Calculate return rates by profile
        profile_return_rates = {}
        for seller in sellers:
            profile = generator._seller_profiles[seller.seller_id]
            profile_type = profile.performance_type
            
            returns_count = seller_returns.get(seller.seller_id, 0)
            orders_count = seller_orders.get(seller.seller_id, 1)
            return_rate = returns_count / orders_count
            
            if profile_type not in profile_return_rates:
                profile_return_rates[profile_type] = []
            profile_return_rates[profile_type].append(return_rate)
        
        # High-risk should have higher return rates than healthy
        avg_high_risk = sum(profile_return_rates[SellerPerformance.HIGH_RISK]) / len(profile_return_rates[SellerPerformance.HIGH_RISK])
        avg_healthy = sum(profile_return_rates[SellerPerformance.HEALTHY]) / len(profile_return_rates[SellerPerformance.HEALTHY])
        
        assert avg_high_risk > avg_healthy
    
    def test_marketplace_reproducibility(self, generator):
        """Test that marketplace data generation is reproducible."""
        gen1 = MarketplaceDataGenerator(seed=42)
        gen2 = MarketplaceDataGenerator(seed=42)
        
        sellers1 = gen1.generate_sellers(count=10)
        sellers2 = gen2.generate_sellers(count=10)
        
        # Should generate same seller IDs
        ids1 = [s.seller_id for s in sellers1]
        ids2 = [s.seller_id for s in sellers2]
        assert ids1 == ids2


class TestCreateGenerator:
    """Test factory function for creating generators."""
    
    def test_create_generator_with_seed(self):
        """Test creating generator with seed."""
        gen = create_generator(seed=42)
        assert gen is not None
        assert gen.seed == 42
    
    def test_create_generator_without_seed(self):
        """Test creating generator without seed."""
        gen = create_generator()
        assert gen is not None
        assert gen.seed is not None
    
    def test_create_generator_returns_correct_type(self):
        """Test that factory returns correct type."""
        gen = create_generator(seed=42)
        assert isinstance(gen, MarketplaceDataGenerator)