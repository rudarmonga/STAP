#!/usr/bin/env python3
"""
Data seeding script for STAP.

This script generates synthetic marketplace data and seeds the database.
Run this after initializing the database with init_db.py.

Usage:
    python scripts/seed_data.py [--reset] [--sellers N] [--orders N] [--days N]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.data.synthetic import (
    MarketplaceDataGenerator,
    SellerData,
    OrderData,
    ReturnData,
    RatingData,
    ReviewData
)
from src.data.validation import DataValidator
from src.utils.logger import setup_logging, get_logger
from src.config.settings import settings

# Ensure logging is set up
setup_logging()
logger = get_logger(__name__)


# Default data volumes - chosen for realistic but manageable dataset
DEFAULT_SELLERS = 100
DEFAULT_ORDERS = 5000
DEFAULT_DAYS_BACK = 365  # 1 year of historical data


def insert_sellers(conn, sellers: list[SellerData]) -> None:
    """Insert sellers into database."""
    logger.info(f"Inserting {len(sellers)} sellers into database")
    
    cursor = conn.executemany(
        """
        INSERT OR REPLACE INTO sellers 
        (seller_id, seller_name, category, region, join_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (s.seller_id, s.seller_name, s.category, s.region, s.join_date, s.status)
            for s in sellers
        ]
    )
    conn.commit()
    logger.info(f"Inserted {cursor.rowcount} sellers")


def insert_orders(conn, orders: list[OrderData]) -> None:
    """Insert orders into database."""
    logger.info(f"Inserting {len(orders)} orders into database")
    
    cursor = conn.executemany(
        """
        INSERT OR REPLACE INTO orders 
        (order_id, seller_id, order_date, category, region, order_value, delivery_days, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (o.order_id, o.seller_id, o.order_date, o.category, o.region, 
             o.order_value, o.delivery_days, o.status)
            for o in orders
        ]
    )
    conn.commit()
    logger.info(f"Inserted {cursor.rowcount} orders")


def insert_returns(conn, returns: list[ReturnData]) -> None:
    """Insert returns into database."""
    logger.info(f"Inserting {len(returns)} returns into database")
    
    cursor = conn.executemany(
        """
        INSERT OR REPLACE INTO returns 
        (return_id, order_id, seller_id, return_date, return_reason, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (r.return_id, r.order_id, r.seller_id, r.return_date, r.return_reason, r.status)
            for r in returns
        ]
    )
    conn.commit()
    logger.info(f"Inserted {cursor.rowcount} returns")


def insert_ratings(conn, ratings: list[RatingData]) -> None:
    """Insert ratings into database."""
    logger.info(f"Inserting {len(ratings)} ratings into database")
    
    cursor = conn.executemany(
        """
        INSERT OR REPLACE INTO ratings 
        (rating_id, seller_id, order_id, rating, rating_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (r.rating_id, r.seller_id, r.order_id, r.rating, r.rating_date)
            for r in ratings
        ]
    )
    conn.commit()
    logger.info(f"Inserted {cursor.rowcount} ratings")


def insert_reviews(conn, reviews: list[ReviewData]) -> None:
    """Insert reviews into database."""
    logger.info(f"Inserting {len(reviews)} reviews into database")
    
    cursor = conn.executemany(
        """
        INSERT OR REPLACE INTO reviews 
        (review_id, seller_id, order_id, review_date, review_text, sentiment, sentiment_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (r.review_id, r.seller_id, r.order_id, r.review_date, r.review_text, 
             r.sentiment, r.sentiment_score)
            for r in reviews
        ]
    )
    conn.commit()
    logger.info(f"Inserted {cursor.rowcount} reviews")


def get_database_counts(conn) -> dict:
    """Get current record counts from database."""
    counts = {}
    
    for table in ["sellers", "orders", "returns", "ratings", "reviews"]:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    
    return counts


def seed_database(
    num_sellers: int = DEFAULT_SELLERS,
    num_orders: int = DEFAULT_ORDERS,
    days_back: int = DEFAULT_DAYS_BACK,
    reset: bool = False
) -> int:
    """
    Seed the database with synthetic marketplace data.
    
    Args:
        num_sellers: Number of sellers to generate
        num_orders: Number of orders to generate
        days_back: Historical period in days
        reset: Whether to reset database before seeding
    
    Returns:
        0 on success, 1 on failure
    """
    logger.info("Starting database seeding process")
    
    try:
        # Reset database if requested
        if reset:
            logger.warning("Resetting database before seeding")
            db.reset_database()
        
        # Check if database is initialized
        if not db.database_exists():
            logger.error("Database does not exist. Run init_db.py first.")
            return 1
        
        schema_version = db.get_schema_version()
        if schema_version < 2:
            logger.error(f"Database schema version {schema_version} is too old. Reinitialize database.")
            return 1
        
        # Initialize data generator
        generator = MarketplaceDataGenerator(seed=settings.synthetic_data_seed)
        
        logger.info(f"Generating synthetic data with seed: {settings.synthetic_data_seed}")
        logger.info(f"Target: {num_sellers} sellers, {num_orders} orders over {days_back} days")
        
        # Generate sellers
        logger.info("Step 1: Generating sellers")
        start_date = datetime.now() - timedelta(days=days_back)
        sellers = generator.generate_sellers(
            count=num_sellers,
            start_date=start_date,
            end_date=datetime.now()
        )
        
        # Validate sellers
        validator = DataValidator()
        if not validator.validate_sellers(sellers):
            logger.error("Seller validation failed")
            for error in validator.get_errors():
                logger.error(f"  {error}")
            return 1
        
        # Generate orders
        logger.info("Step 2: Generating orders")
        orders = generator.generate_orders(
            sellers=sellers,
            count=num_orders,
            days_back=days_back
        )
        
        # Validate orders
        seller_ids = {s.seller_id for s in sellers}
        if not validator.validate_orders(orders, seller_ids):
            logger.error("Order validation failed")
            for error in validator.get_errors():
                logger.error(f"  {error}")
            return 1
        
        # Generate returns
        logger.info("Step 3: Generating returns")
        returns = generator.generate_returns(orders=orders)
        
        # Validate returns
        order_ids = {o.order_id for o in orders}
        if not validator.validate_returns(returns, order_ids, seller_ids):
            logger.error("Return validation failed")
            for error in validator.get_errors():
                logger.error(f"  {error}")
            return 1
        
        # Generate ratings
        logger.info("Step 4: Generating ratings")
        ratings = generator.generate_ratings(orders=orders)
        
        # Validate ratings
        if not validator.validate_ratings(ratings, seller_ids, order_ids):
            logger.error("Rating validation failed")
            for error in validator.get_errors():
                logger.error(f"  {error}")
            return 1
        
        # Generate reviews
        logger.info("Step 5: Generating reviews")
        reviews = generator.generate_reviews(orders=orders)
        
        # Validate reviews
        if not validator.validate_reviews(reviews, seller_ids, order_ids):
            logger.error("Review validation failed")
            for error in validator.get_errors():
                logger.error(f"  {error}")
            return 1
        
        # Insert all data into database
        logger.info("Step 6: Inserting data into database")
        with db.get_connection() as conn:
            # Get initial counts
            initial_counts = get_database_counts(conn)
            logger.info(f"Initial database counts: {initial_counts}")
            
            # Insert data
            insert_sellers(conn, sellers)
            insert_orders(conn, orders)
            insert_returns(conn, returns)
            insert_ratings(conn, ratings)
            insert_reviews(conn, reviews)
            
            # Get final counts
            final_counts = get_database_counts(conn)
            logger.info(f"Final database counts: {final_counts}")
        
        logger.info("Database seeding completed successfully")
        logger.info(f"Summary: {len(sellers)} sellers, {len(orders)} orders, {len(returns)} returns, {len(ratings)} ratings, {len(reviews)} reviews")
        
        return 0
        
    except Exception as e:
        logger.error(f"Database seeding failed: {e}", exc_info=True)
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed STAP database with synthetic marketplace data")
    parser.add_argument("--reset", action="store_true", help="Reset database before seeding")
    parser.add_argument("--sellers", type=int, default=DEFAULT_SELLERS, 
                       help=f"Number of sellers (default: {DEFAULT_SELLERS})")
    parser.add_argument("--orders", type=int, default=DEFAULT_ORDERS,
                       help=f"Number of orders (default: {DEFAULT_ORDERS})")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS_BACK,
                       help=f"Historical period in days (default: {DEFAULT_DAYS_BACK})")
    
    args = parser.parse_args()
    
    return seed_database(
        num_sellers=args.sellers,
        num_orders=args.orders,
        days_back=args.days,
        reset=args.reset
    )


if __name__ == "__main__":
    sys.exit(main())
