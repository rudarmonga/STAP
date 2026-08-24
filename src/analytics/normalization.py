"""
Normalization functions for analytics metrics.

This module provides utilities to normalize different metric scales
to a common 0-100 range for Trust Score calculation.
"""

from typing import Optional
import math


def normalize_rating(rating: float, min_rating: float = 1.0, max_rating: float = 5.0) -> float:
    """
    Normalize rating from 1-5 scale to 0-100 scale.
    
    Args:
        rating: Rating value (1-5)
        min_rating: Minimum possible rating (default: 1.0)
        max_rating: Maximum possible rating (default: 5.0)
    
    Returns:
        Normalized rating (0-100)
    
    Examples:
        >>> normalize_rating(5.0)
        100.0
        >>> normalize_rating(1.0)
        0.0
        >>> normalize_rating(3.0)
        50.0
    """
    if rating is None or math.isnan(rating):
        return 50.0  # Neutral value for missing data
    
    # Clamp to valid range
    rating = max(min_rating, min(max_rating, rating))
    
    # Normalize to 0-100
    normalized = ((rating - min_rating) / (max_rating - min_rating)) * 100
    return round(normalized, 2)


def normalize_return_rate(return_rate: float, max_acceptable_rate: float = 20.0) -> float:
    """
    Normalize return rate to 0-100 scale (inverted - lower is better).
    
    Args:
        return_rate: Return rate as percentage (0-100)
        max_acceptable_rate: Maximum acceptable return rate (default: 20%)
    
    Returns:
        Normalized return score (0-100, higher is better)
    
    Examples:
        >>> normalize_return_rate(0.0)  # No returns
        100.0
        >>> normalize_return_rate(20.0)  # At threshold
        0.0
        >>> normalize_return_rate(10.0)  # Half threshold
        50.0
    """
    if return_rate is None or math.isnan(return_rate):
        return 50.0  # Neutral value for missing data
    
    # Clamp to valid range
    return_rate = max(0.0, min(100.0, return_rate))
    
    # Invert: lower return rate = higher score
    if return_rate >= max_acceptable_rate:
        return 0.0
    else:
        normalized = 100 - (return_rate / max_acceptable_rate * 100)
        return round(normalized, 2)


def normalize_sentiment(sentiment: float, min_sentiment: float = -1.0, max_sentiment: float = 1.0) -> float:
    """
    Normalize sentiment score from -1 to 1 scale to 0-100 scale.
    
    Args:
        sentiment: Sentiment score (-1 to 1)
        min_sentiment: Minimum possible sentiment (default: -1.0)
        max_sentiment: Maximum possible sentiment (default: 1.0)
    
    Returns:
        Normalized sentiment (0-100)
    
    Examples:
        >>> normalize_sentiment(1.0)  # Very positive
        100.0
        >>> normalize_sentiment(-1.0)  # Very negative
        0.0
        >>> normalize_sentiment(0.0)  # Neutral
        50.0
    """
    if sentiment is None or math.isnan(sentiment):
        return 50.0  # Neutral value for missing data
    
    # Clamp to valid range
    sentiment = max(min_sentiment, min(max_sentiment, sentiment))
    
    # Normalize -1 to 1 range to 0-100
    normalized = ((sentiment - min_sentiment) / (max_sentiment - min_sentiment)) * 100
    return round(normalized, 2)


def normalize_delivery_rate(delivery_rate: float) -> float:
    """
    Normalize delivery rate to 0-100 scale.
    
    Args:
        delivery_rate: Delivery rate as percentage (0-100)
    
    Returns:
        Normalized delivery score (0-100)
    
    Examples:
        >>> normalize_delivery_rate(100.0)
        100.0
        >>> normalize_delivery_rate(0.0)
        0.0
        >>> normalize_delivery_rate(95.0)
        95.0
    """
    if delivery_rate is None or math.isnan(delivery_rate):
        return 50.0  # Neutral value for missing data
    
    # Clamp to valid range
    delivery_rate = max(0.0, min(100.0, delivery_rate))
    
    return round(delivery_rate, 2)


def normalize_completion_rate(completion_rate: float) -> float:
    """
    Normalize order completion rate to 0-100 scale.
    
    Args:
        completion_rate: Completion rate as percentage (0-100)
    
    Returns:
        Normalized completion score (0-100)
    
    Examples:
        >>> normalize_completion_rate(100.0)
        100.0
        >>> normalize_completion_rate(0.0)
        0.0
        >>> normalize_completion_rate(85.0)
        85.0
    """
    if completion_rate is None or math.isnan(completion_rate):
        return 50.0  # Neutral value for missing data
    
    # Clamp to valid range
    completion_rate = max(0.0, min(100.0, completion_rate))
    
    return round(completion_rate, 2)


def normalize_average_delivery_days(avg_days: float, max_acceptable_days: float = 10.0) -> float:
    """
    Normalize average delivery days to 0-100 scale (inverted - lower is better).
    
    Args:
        avg_days: Average delivery days
        max_acceptable_days: Maximum acceptable delivery days (default: 10)
    
    Returns:
        Normalized delivery score (0-100, higher is better)
    
    Examples:
        >>> normalize_average_delivery_days(1.0)  # Very fast
        90.0
        >>> normalize_average_delivery_days(10.0)  # At threshold
        0.0
        >>> normalize_average_delivery_days(5.5)  # Half threshold
        45.0
    """
    if avg_days is None or math.isnan(avg_days) or avg_days <= 0:
        return 50.0  # Neutral value for missing/invalid data
    
    # Invert: lower delivery days = higher score
    if avg_days >= max_acceptable_days:
        return 0.0
    else:
        # Linear interpolation with minimum score of 10 for very fast delivery
        # to avoid giving 100 for unreasonably fast times
        min_score = 10.0
        normalized = 100 - (avg_days / max_acceptable_days * (100 - min_score))
        return round(max(min_score, normalized), 2)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division is not possible
    
    Returns:
        Result of division or default value
    """
    if denominator is None or math.isnan(denominator) or denominator == 0:
        return default
    if numerator is None or math.isnan(numerator):
        return default
    
    try:
        return numerator / denominator
    except (ZeroDivisionError, ArithmeticError):
        return default


def safe_average(values: list, default: float = 0.0) -> float:
    """
    Safely calculate average of a list of values.
    
    Args:
        values: List of numeric values
        default: Default value if list is empty or contains invalid values
    
    Returns:
        Average of values or default value
    """
    if not values:
        return default
    
    # Filter out None and NaN values
    valid_values = [v for v in values if v is not None and not math.isnan(v)]
    
    if not valid_values:
        return default
    
    try:
        return sum(valid_values) / len(valid_values)
    except (ArithmeticError, TypeError):
        return default