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
│   └── init_db.py          # Database initialization script
├── src/
│   ├── analytics/          # Analytics and business logic
│   ├── config/             # Configuration management
│   ├── data/               # Data processing and synthetic data
│   ├── database/           # Database layer
│   ├── reporting/          # Reporting functionality
│   ├── ui/                 # Streamlit UI components
│   └── utils/              # Utility functions
├── tests/                  # Test suite
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

The current schema version is tracked in the `schema_version` table. Future schema migrations will be handled through the database layer.

### Database Location

By default, the database is stored at `data/stap.db` in the project root. This can be customized via the `STAP_DATABASE_PATH` environment variable.

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

## Current Features (Foundation)

The current version provides the foundation for future analytics:

- **Dashboard**: Foundation page for marketplace-level analytics
- **Seller Analytics**: Foundation page for individual seller analysis
- **Reports**: Foundation page for report generation and export
- **Settings**: Configuration page with current settings display

## Future Features

The following features will be implemented in future iterations:

- Marketplace-level performance monitoring
- Seller-level analytics and metrics
- Seller Trust Score calculation
- Seller risk classification
- Historical performance trends
- Customer rating and review sentiment analysis
- Return-rate analysis
- Seller rankings
- High-risk seller identification
- Filtering and search functionality
- CSV, Excel, and PDF reporting
- Daily data refresh

## Development

### Adding New Features

1. **Database changes**: Update schema in `src/database/connection.py`
2. **Business logic**: Add to `src/analytics/`
3. **UI components**: Add pages to `src/ui/pages.py`
4. **Data processing**: Add to `src/data/`
5. **Tests**: Add corresponding tests in `tests/`

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
# STAP
