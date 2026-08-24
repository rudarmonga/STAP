"""
Tests for analytics normalization functions.
"""

import pytest
import math
from src.analytics.normalization import (
    normalize_rating,
    normalize_return_rate,
    normalize_sentiment,
    normalize_delivery_rate,
    normalize_completion_rate,
    normalize_average_delivery_days,
    safe_divide,
    safe_average
)


class TestNormalizeRating:
    """Test rating normalization."""
    
    def test_normalize_rating_max(self):
        """Test normalizing maximum rating."""
        assert normalize_rating(5.0) == 100.0
    
    def test_normalize_rating_min(self):
        """Test normalizing minimum rating."""
        assert normalize_rating(1.0) == 0.0
    
    def test_normalize_rating_middle(self):
        """Test normalizing middle rating."""
        assert normalize_rating(3.0) == 50.0
    
    def test_normalize_rating_clamp_high(self):
        """Test clamping of high values."""
        assert normalize_rating(6.0) == 100.0
        assert normalize_rating(10.0) == 100.0
    
    def test_normalize_rating_clamp_low(self):
        """Test clamping of low values."""
        assert normalize_rating(0.0) == 0.0
        assert normalize_rating(-5.0) == 0.0
    
    def test_normalize_rating_none(self):
        """Test handling of None values."""
        assert normalize_rating(None) == 50.0
    
    def test_normalize_rating_nan(self):
        """Test handling of NaN values."""
        assert normalize_rating(math.nan) == 50.0
    
    def test_normalize_rating_custom_range(self):
        """Test normalization with custom range."""
        assert normalize_rating(10.0, min_rating=0.0, max_rating=10.0) == 100.0
        assert normalize_rating(0.0, min_rating=0.0, max_rating=10.0) == 0.0
        assert normalize_rating(5.0, min_rating=0.0, max_rating=10.0) == 50.0


class TestNormalizeReturnRate:
    """Test return rate normalization."""
    
    def test_normalize_return_rate_zero(self):
        """Test normalizing zero return rate."""
        assert normalize_return_rate(0.0) == 100.0
    
    def test_normalize_return_rate_at_threshold(self):
        """Test normalizing at threshold."""
        assert normalize_return_rate(20.0) == 0.0
    
    def test_normalize_return_rate_half_threshold(self):
        """Test normalizing half of threshold."""
        assert normalize_return_rate(10.0) == 50.0
    
    def test_normalize_return_rate_above_threshold(self):
        """Test normalizing above threshold."""
        assert normalize_return_rate(25.0) == 0.0
        assert normalize_return_rate(100.0) == 0.0
    
    def test_normalize_return_rate_clamp_low(self):
        """Test clamping of negative values."""
        assert normalize_return_rate(-5.0) == 100.0
    
    def test_normalize_return_rate_none(self):
        """Test handling of None values."""
        assert normalize_return_rate(None) == 50.0
    
    def test_normalize_return_rate_nan(self):
        """Test handling of NaN values."""
        assert normalize_return_rate(math.nan) == 50.0
    
    def test_normalize_return_rate_custom_threshold(self):
        """Test normalization with custom threshold."""
        assert normalize_return_rate(0.0, max_acceptable_rate=10.0) == 100.0
        assert normalize_return_rate(10.0, max_acceptable_rate=10.0) == 0.0
        assert normalize_return_rate(5.0, max_acceptable_rate=10.0) == 50.0


class TestNormalizeSentiment:
    """Test sentiment normalization."""
    
    def test_normalize_sentiment_max(self):
        """Test normalizing maximum sentiment."""
        assert normalize_sentiment(1.0) == 100.0
    
    def test_normalize_sentiment_min(self):
        """Test normalizing minimum sentiment."""
        assert normalize_sentiment(-1.0) == 0.0
    
    def test_normalize_sentiment_neutral(self):
        """Test normalizing neutral sentiment."""
        assert normalize_sentiment(0.0) == 50.0
    
    def test_normalize_sentiment_clamp_high(self):
        """Test clamping of high values."""
        assert normalize_sentiment(2.0) == 100.0
    
    def test_normalize_sentiment_clamp_low(self):
        """Test clamping of low values."""
        assert normalize_sentiment(-2.0) == 0.0
    
    def test_normalize_sentiment_none(self):
        """Test handling of None values."""
        assert normalize_sentiment(None) == 50.0
    
    def test_normalize_sentiment_nan(self):
        """Test handling of NaN values."""
        assert normalize_sentiment(math.nan) == 50.0
    
    def test_normalize_sentiment_partial_positive(self):
        """Test normalizing partial positive sentiment."""
        assert normalize_sentiment(0.5) == 75.0
    
    def test_normalize_sentiment_partial_negative(self):
        """Test normalizing partial negative sentiment."""
        assert normalize_sentiment(-0.5) == 25.0


class TestNormalizeDeliveryRate:
    """Test delivery rate normalization."""
    
    def test_normalize_delivery_rate_perfect(self):
        """Test normalizing perfect delivery rate."""
        assert normalize_delivery_rate(100.0) == 100.0
    
    def test_normalize_delivery_rate_zero(self):
        """Test normalizing zero delivery rate."""
        assert normalize_delivery_rate(0.0) == 0.0
    
    def test_normalize_delivery_rate_partial(self):
        """Test normalizing partial delivery rate."""
        assert normalize_delivery_rate(75.0) == 75.0
    
    def test_normalize_delivery_rate_clamp_high(self):
        """Test clamping of high values."""
        assert normalize_delivery_rate(150.0) == 100.0
    
    def test_normalize_delivery_rate_clamp_low(self):
        """Test clamping of negative values."""
        assert normalize_delivery_rate(-10.0) == 0.0
    
    def test_normalize_delivery_rate_none(self):
        """Test handling of None values."""
        assert normalize_delivery_rate(None) == 50.0
    
    def test_normalize_delivery_rate_nan(self):
        """Test handling of NaN values."""
        assert normalize_delivery_rate(math.nan) == 50.0


class TestNormalizeCompletionRate:
    """Test completion rate normalization."""
    
    def test_normalize_completion_rate_perfect(self):
        """Test normalizing perfect completion rate."""
        assert normalize_completion_rate(100.0) == 100.0
    
    def test_normalize_completion_rate_zero(self):
        """Test normalizing zero completion rate."""
        assert normalize_completion_rate(0.0) == 0.0
    
    def test_normalize_completion_rate_partial(self):
        """Test normalizing partial completion rate."""
        assert normalize_completion_rate(85.0) == 85.0
    
    def test_normalize_completion_rate_clamp_high(self):
        """Test clamping of high values."""
        assert normalize_completion_rate(120.0) == 100.0
    
    def test_normalize_completion_rate_clamp_low(self):
        """Test clamping of negative values."""
        assert normalize_completion_rate(-5.0) == 0.0
    
    def test_normalize_completion_rate_none(self):
        """Test handling of None values."""
        assert normalize_completion_rate(None) == 50.0
    
    def test_normalize_completion_rate_nan(self):
        """Test handling of NaN values."""
        assert normalize_completion_rate(math.nan) == 50.0


class TestNormalizeAverageDeliveryDays:
    """Test average delivery days normalization."""
    
    def test_normalize_average_delivery_days_very_fast(self):
        """Test normalizing very fast delivery."""
        result = normalize_average_delivery_days(1.0)
        assert result >= 80.0  # Should be high but not 100
    
    def test_normalize_average_delivery_days_at_threshold(self):
        """Test normalizing at threshold."""
        assert normalize_average_delivery_days(10.0) == 0.0
    
    def test_normalize_average_delivery_days_half_threshold(self):
        """Test normalizing half of threshold."""
        result = normalize_average_delivery_days(5.0)
        # The function uses a linear interpolation with minimum score of 10
        # So at half threshold (5 days), the score should be around 45-55
        assert 45.0 <= result <= 55.0
    
    def test_normalize_average_delivery_days_above_threshold(self):
        """Test normalizing above threshold."""
        assert normalize_average_delivery_days(15.0) == 0.0
    
    def test_normalize_average_delivery_days_zero(self):
        """Test handling of zero days."""
        assert normalize_average_delivery_days(0.0) == 50.0
    
    def test_normalize_average_delivery_days_negative(self):
        """Test handling of negative days."""
        assert normalize_average_delivery_days(-5.0) == 50.0
    
    def test_normalize_average_delivery_days_none(self):
        """Test handling of None values."""
        assert normalize_average_delivery_days(None) == 50.0
    
    def test_normalize_average_delivery_days_nan(self):
        """Test handling of NaN values."""
        assert normalize_average_delivery_days(math.nan) == 50.0
    
    def test_normalize_average_delivery_days_custom_threshold(self):
        """Test normalization with custom threshold."""
        assert normalize_average_delivery_days(0.0, max_acceptable_days=5.0) == 50.0
        assert normalize_average_delivery_days(5.0, max_acceptable_days=5.0) == 0.0


class TestSafeDivide:
    """Test safe division function."""
    
    def test_safe_divide_normal(self):
        """Test normal division."""
        assert safe_divide(10.0, 2.0) == 5.0
        assert safe_divide(100.0, 4.0) == 25.0
    
    def test_safe_divide_zero_denominator(self):
        """Test division by zero."""
        assert safe_divide(10.0, 0.0) == 0.0
        assert safe_divide(100.0, 0.0) == 0.0
    
    def test_safe_divide_none_numerator(self):
        """Test None numerator."""
        assert safe_divide(None, 2.0) == 0.0
    
    def test_safe_divide_none_denominator(self):
        """Test None denominator."""
        assert safe_divide(10.0, None) == 0.0
    
    def test_safe_divide_nan_numerator(self):
        """Test NaN numerator."""
        assert safe_divide(math.nan, 2.0) == 0.0
    
    def test_safe_divide_nan_denominator(self):
        """Test NaN denominator."""
        assert safe_divide(10.0, math.nan) == 0.0
    
    def test_safe_divide_custom_default(self):
        """Test custom default value."""
        assert safe_divide(10.0, 0.0, default=99.0) == 99.0


class TestSafeAverage:
    """Test safe average function."""
    
    def test_safe_average_normal(self):
        """Test normal average."""
        assert safe_average([1.0, 2.0, 3.0]) == 2.0
        assert safe_average([10.0, 20.0, 30.0]) == 20.0
    
    def test_safe_average_empty_list(self):
        """Test empty list."""
        assert safe_average([]) == 0.0
    
    def test_safe_average_none_values(self):
        """Test list with None values."""
        assert safe_average([1.0, None, 3.0]) == 2.0
        assert safe_average([None, None]) == 0.0
    
    def test_safe_average_nan_values(self):
        """Test list with NaN values."""
        assert safe_average([1.0, math.nan, 3.0]) == 2.0
        assert safe_average([math.nan, math.nan]) == 0.0
    
    def test_safe_average_mixed_invalid(self):
        """Test list with mixed invalid values."""
        assert safe_average([1.0, None, math.nan, 4.0]) == 2.5
    
    def test_safe_average_custom_default(self):
        """Test custom default value."""
        assert safe_average([], default=99.0) == 99.0
    
    def test_safe_average_single_value(self):
        """Test single value."""
        assert safe_average([5.0]) == 5.0