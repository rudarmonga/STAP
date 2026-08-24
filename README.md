# STAP - Seller Trust Analytics Platform

STAP is a desktop-oriented analytics platform for marketplace managers and operations teams. It helps monitor seller performance and marketplace trust using descriptive analytics.

## Technology Stack

- **Python** 3.10+
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **SQLite** - Database (built into Python)
- **Streamlit** - Web application framework
- **GitHub Actions** - CI/CD

## Project Structure

```
STAP/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI workflow
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── data/                   # Database directory (created at runtime)
├── scripts/
│   ├── init_db.py          # Database initialization script
│   └── seed_data.py        # Synthetic data seeding script
├── src/
│   ├── analytics/          # Analytics and business logic
│   │   ├── config.py       # Trust Score configuration and weights
│   │   ├── engine.py       # Core analytics engine
│   │   ├── models.py       # Analytics data models
│   │   └── normalization.py # Metric normalization functions
│   ├── config/             # Configuration management
│   ├── data/               # Data processing and synthetic data
│   │   ├── synthetic.py    # Synthetic data generator
│   │   └── validation.py   # Data validation layer
│   ├── database/           # Database layer
│   │   └── connection.py   # SQLite connection and schema
│   ├── reporting/          # Reporting functionality
│   ├── ui/                 # Streamlit UI components
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── test_analytics_config.py     # Analytics configuration tests
│   ├── test_analytics_engine.py     # Analytics engine tests
│   ├── test_analytics_normalization.py  # Normalization function tests
│   ├── test_config.py      # Configuration tests
│   ├── test_database.py    # Database tests
│   ├── test_imports.py     # Import validation tests
│   ├── test_synthetic_data.py  # Synthetic data generation tests
│   └── test_validation.py  # Data validation tests
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── pytest.ini              # pytest configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd STAP
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to customize settings if needed. The defaults are suitable for local development.

5. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```
   This creates the SQLite database at the configured path (default: `data/stap.db`).

6. **Seed the database with synthetic data**
   ```bash
   python scripts/seed_data.py
   ```
   This generates and inserts realistic marketplace data into the database.

## Running the Application

Start the Streamlit application:

```bash
streamlit run src/ui/app.py
```

The application will open in your browser at `http://localhost:8501`.

## Running Tests

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=html
```

View the coverage report:

```bash
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
# or
start htmlcov/index.html  # On Windows
```

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `STAP_ENV` | Environment (development, staging, production) | `development` |
| `STAP_DATABASE_PATH` | Path to SQLite database | `data/stap.db` |
| `STAP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `STAP_LOG_FILE` | Optional log file path | (console only) |
| `STAP_SYNTHETIC_DATA_SEED` | Seed for reproducible synthetic data | `42` |
| `STAP_APP_TITLE` | Application title | `STAP - Seller Trust Analytics Platform` |
| `STAP_PAGE_TITLE` | Browser page title | `STAP Analytics` |

## Database

STAP uses SQLite for data storage. The database is automatically initialized on first run or via the initialization script.

### Database Schema

The STAP database schema (version 2) includes the following tables:

**sellers**
- seller_id (TEXT, PRIMARY KEY)
- seller_name (TEXT, NOT NULL)
- category (TEXT, NOT NULL) - Electronics, Clothing, Home & Garden, Sports, Books, Toys, Automotive, Health & Beauty, Food & Grocery, Office Supplies
- region (TEXT, NOT NULL) - North America, Europe, Asia Pacific, Latin America, Middle East, Africa
- join_date (TEXT, NOT NULL)
- status (TEXT, NOT NULL) - active, inactive, suspended

**orders**
- order_id (TEXT, PRIMARY KEY)
- seller_id (TEXT, NOT NULL, FOREIGN KEY → sellers)
- order_date (TEXT, NOT NULL)
- category (TEXT, NOT NULL)
- region (TEXT, NOT NULL)
- order_value (REAL, NOT NULL)
- delivery_days (INTEGER)
- status (TEXT, NOT NULL) - completed, cancelled, pending, refunded

**returns**
- return_id (TEXT, PRIMARY KEY)
- order_id (TEXT, NOT NULL, FOREIGN KEY → orders)
- seller_id (TEXT, NOT NULL, FOREIGN KEY → sellers)
- return_date (TEXT, NOT NULL)
- return_reason (TEXT, NOT NULL)
- status (TEXT, NOT NULL) - approved, rejected, pending

**ratings**
- rating_id (TEXT, PRIMARY KEY)
- seller_id (TEXT, NOT NULL, FOREIGN KEY → sellers)
- order_id (TEXT, FOREIGN KEY → orders)
- rating (INTEGER, NOT NULL, CHECK 1-5)
- rating_date (TEXT, NOT NULL)

**reviews**
- review_id (TEXT, PRIMARY KEY)
- seller_id (TEXT, NOT NULL, FOREIGN KEY → sellers)
- order_id (TEXT, FOREIGN KEY → orders)
- review_date (TEXT, NOT NULL)
- review_text (TEXT, NOT NULL)
- sentiment (TEXT) - positive, neutral, negative
- sentiment_score (REAL, CHECK -1 to 1)

The schema version is tracked in the `schema_version` table. Future schema migrations will be handled through the database layer.

### Database Location

By default, the database is stored at `data/stap.db` in the project root. This can be customized via the `STAP_DATABASE_PATH` environment variable.

## Synthetic Data Generation

STAP uses a synthetic data generator to create realistic marketplace data without external dependencies. This ensures the application can be deployed and tested without requiring access to real marketplace data.

### Data Generation Approach

The synthetic data generator uses a deterministic, reproducible approach:

- **Seed-based Randomness**: Uses a fixed random seed (default: 42) for reproducibility
- **Performance Profiles**: Sellers are assigned performance profiles (healthy, average, declining, high_risk) that influence their behavior
- **Historical Distribution**: Orders are distributed using weighted random distributions that mimic real marketplace patterns
- **Realistic Relationships**: Returns, ratings, and reviews are linked to existing orders and sellers
- **Business Logic Integration**: High-risk sellers have higher return rates, declining sellers have worsening ratings over time, etc.

### Default Dataset Sizes

The default synthetic dataset generation creates:
- **100 sellers** across 10 categories and 6 regions
- **5,000 orders** distributed over 1 year (configurable)
- **~400 returns** (8% return rate, realistic for e-commerce)
- **~3,000 ratings** (60% of orders have ratings)
- **~2,000 reviews** (40% of orders have reviews)

### Data Generation Commands

**Initialize database (creates schema):**
```bash
python scripts/init_db.py
```

**Reset database (drops and recreates schema):**
```bash
python scripts/init_db.py --reset
```

**Generate and seed synthetic data:**
```bash
python scripts/seed_data.py
```

**Generate custom dataset size:**
```bash
python scripts/seed_data.py --sellers 200 --orders 10000 --days 365
```

**Force re-seed (replaces existing data):**
```bash
python scripts/seed_data.py --reset
```

**Complete fresh setup workflow:**
```bash
python scripts/init_db.py --reset
python scripts/seed_data.py --reset
```

### Data Validation

All synthetic data is validated before insertion into the database. Validation checks include:

- Required fields are present
- Seller IDs are valid and unique
- Foreign-key relationships are valid
- Ratings are within the 1-5 range
- Sentiment scores are within -1 to 1 range
- Dates are valid and follow chronological constraints
- No impossible negative quantities/values
- No unexpected null values in required fields

If invalid data is detected, the seeding process fails clearly rather than silently inserting corrupt data.

### Idempotent Seeding

The data seeding process is idempotent - running it multiple times will not create uncontrolled duplicates. The script uses `INSERT OR REPLACE` statements, so re-running will update existing records rather than creating duplicates. For a complete reset, use the `--reset` flag.

## Analytics Engine

STAP includes a comprehensive analytics engine that calculates seller performance metrics, Trust Scores, and risk classifications.

### Trust Score

The Trust Score is a deterministic metric (0-100 scale) that assesses seller performance based on five weighted components:

1. **Rating Component (30%)**: Customer satisfaction through product ratings (1-5 scale)
2. **Return Component (25%)**: Product quality through return behavior
3. **Sentiment Component (20%)**: Customer sentiment from review text analysis
4. **Operational Component (15%)**: Delivery performance and efficiency
5. **Reliability Component (10%)**: Order fulfillment reliability

**Risk Classification:**
- **Healthy (80-100)**: Strong performance metrics
- **Monitor (60-79)**: Requires attention and monitoring
- **High Risk (0-59)**: Significant performance issues

For detailed Trust Score documentation, see [TRUST_SCORE_DOCUMENTATION.md](TRUST_SCORE_DOCUMENTATION.md).

### Seller Metrics

The analytics engine calculates comprehensive seller metrics:

**Order Metrics:**
- Total orders, completed orders, cancelled orders
- Total revenue, average order value
- Completion rate, cancellation rate

**Return Metrics:**
- Total returns, approved/rejected returns
- Return rate (returns / total orders)

**Rating Metrics:**
- Total ratings, average rating
- Rating distribution (1-5 stars)
- Five-star and one-star percentages

**Review Metrics:**
- Total reviews, positive/neutral/negative reviews
- Negative review percentage
- Average sentiment score

**Operational Metrics:**
- Average delivery days
- On-time delivery rate
- Total delivery days

### Time-Based Analytics

The analytics engine supports flexible time filtering:

- All time
- Last 30 days
- Last 90 days
- Last 6 months
- Last 1 year
- Last 3 years
- Last 5 years
- Custom date range

### Marketplace Analytics

The engine also provides marketplace-level aggregated metrics:

- Total sellers, active sellers
- Risk distribution (healthy/monitor/high-risk)
- Total orders, total revenue
- Overall return rate, average rating
- Overall review sentiment
- Average Trust Score

### Using the Analytics Engine

```python
from src.analytics import analytics_engine, DateRange

# Calculate seller analytics
seller_analytics = analytics_engine.calculate_seller_analytics(
    seller_id="SELLER-12345",
    date_range=DateRange.LAST_90_DAYS
)

# Calculate marketplace analytics
marketplace_analytics = analytics_engine.calculate_marketplace_analytics(
    date_range=DateRange.LAST_30_DAYS
)

# Rank sellers by Trust Score
top_sellers = analytics_engine.rank_sellers_by_trust_score(limit=10)
```

### Analytics Configuration

Trust Score weights and risk thresholds are configurable in `src/analytics/config.py`:

- **TrustScoreWeights**: Component weights (must sum to 1.0)
- **RiskThresholds**: Risk classification boundaries
- **DataSufficiencyThresholds**: Minimum data requirements

To modify the Trust Score calculation, update the weights in the configuration file.

## Deployment

### Streamlit Cloud Deployment

1. Push your code to a GitHub repository
2. Connect your repository to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Streamlit will automatically:
   - Install dependencies from `requirements.txt`
   - Run the application using `streamlit run src/ui/app.py`
4. Configure any required environment variables in the Streamlit Cloud dashboard

### Requirements for Deployment

- All dependencies must be listed in `requirements.txt`
- No hardcoded local paths
- No external data dependencies (synthetic data is generated internally)
- Environment variables must be documented in `.env.example`
- Application must start without errors
- Database initialization and data seeding must work in the deployment environment

### Deployment Workflow

When deploying to a fresh environment (e.g., Streamlit Cloud):

1. The application will automatically create the database directory
2. Run the database initialization script as part of deployment setup
3. Run the data seeding script to populate the database with synthetic data
4. The application will then connect to the initialized database

For automated deployments, you may want to add these initialization steps to your deployment script or startup process.

## Current Features (Foundation)

The current version provides the foundation for future analytics:

- **Dashboard**: Foundation page for marketplace-level analytics
- **Seller Analytics**: Foundation page for individual seller analysis
- **Reports**: Foundation page for report generation and export
- **Settings**: Configuration page with current settings display
- **Synthetic Data Generation**: Complete marketplace data generation with realistic seller performance patterns
- **Data Validation**: Comprehensive validation layer ensuring data quality
- **Database Schema**: Complete STAP schema supporting sellers, orders, returns, ratings, and reviews
- **Idempotent Seeding**: Safe, repeatable database seeding without duplicate data
- **Analytics Engine**: Core business logic for seller performance calculation and Trust Score computation

## Future Features

The following features will be implemented in future iterations:

- Dashboard UI with marketplace-level KPIs
- Seller analytics page with detailed performance charts
- Historical performance trends and charts
- Seller rankings and leaderboards
- Filtering and search functionality
- CSV, Excel, and PDF reporting
- Daily data refresh automation

## Development

### Adding New Features

1. **Database changes**: Update schema in `src/database/connection.py`
2. **Business logic**: Add to `src/analytics/`
3. **Analytics calculations**: Update engine in `src/analytics/engine.py`
4. **Trust Score changes**: Update config in `src/analytics/config.py`
5. **UI components**: Add pages to `src/ui/pages.py`
6. **Data processing**: Add to `src/data/`
7. **Tests**: Add corresponding tests in `tests/`

### Code Style

- Use type hints where useful
- Keep modules focused
- Follow existing naming conventions
- Add docstrings for public functions
- Handle errors properly
- Log important events

## Troubleshooting

### Database Initialization Errors

If database initialization fails:
1. Ensure the `data/` directory exists or can be created
2. Check file permissions
3. Verify `STAP_DATABASE_PATH` in `.env`

### Data Seeding Errors

If data seeding fails:
1. Ensure the database has been initialized with `python scripts/init_db.py`
2. Check that the schema version is at least 2
3. Review validation errors in the logs
4. Ensure the synthetic data seed is set correctly in `.env`

### Validation Errors

If you encounter validation errors during data seeding:
1. Check the error messages in the logs
2. Ensure the synthetic data generator is working correctly
3. Verify that performance profiles are being assigned correctly
4. Check for duplicate IDs or invalid foreign key references

### Analytics Errors

If you encounter analytics calculation errors:
1. Ensure the database has been seeded with synthetic data
2. Check that the schema version is at least 2
3. Verify that seller IDs exist in the database
4. Review the analytics logs for specific metric calculation errors
5. Ensure date ranges are valid when using time-based analytics

### Import Errors

If you encounter import errors:
1. Ensure you're running from the project root
2. Activate your virtual environment
3. Reinstall dependencies: `pip install -r requirements.txt`

### Streamlit Won't Start

If Streamlit fails to start:
1. Check that all dependencies are installed
2. Verify the Python version (3.10+)
3. Check for port conflicts (default: 8501)
4. Review Streamlit logs for error details

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
