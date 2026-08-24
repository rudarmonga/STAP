"""
Streamlit page definitions for STAP.

This module contains the page functions for each navigation destination.
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.config.settings import settings
from src.utils.logger import get_logger
from src.analytics import analytics_engine, DateRange, RiskLevel

logger = get_logger(__name__)


def render_dashboard():
    """Render the Dashboard page with production analytics."""
    st.title("Dashboard")
    st.markdown("---")
    
    # Dashboard filters
    with st.sidebar:
        st.header("Dashboard Filters")
        
        # Time period filter
        time_period = st.selectbox(
            "Time Period",
            ["All Time", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last 1 Year"],
            index=0
        )
        
        # Category filter
        category_filter = st.selectbox(
            "Category",
            ["All Categories", "Electronics", "Clothing", "Home & Garden", "Sports", "Books", 
             "Toys", "Automotive", "Health & Beauty", "Food & Grocery", "Office Supplies"],
            index=0
        )
        
        # Region filter
        region_filter = st.selectbox(
            "Region",
            ["All Regions", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East", "Africa"],
            index=0
        )
        
        # Risk level filter
        risk_filter = st.selectbox(
            "Risk Level",
            ["All Risk Levels", "Healthy", "Monitor", "High Risk"],
            index=0
        )
        
        st.markdown("---")
        
        # Seller search
        st.header("Seller Search")
        seller_search = st.text_input("Search by Seller ID or Name", "")
        
        if st.button("Search Seller", key="search_button"):
            if seller_search:
                st.session_state.selected_seller_id = seller_search
                st.info(f"Searching for seller: {seller_search}")
                # Note: Full seller navigation will be implemented in Seller Analytics page
    
    # Convert time period to DateRange enum
    time_range_map = {
        "All Time": "all_time",
        "Last 30 Days": "last_30_days",
        "Last 90 Days": "last_90_days",
        "Last 6 Months": "last_6_months",
        "Last 1 Year": "last_1_year"
    }
    date_range = time_range_map.get(time_period, "all_time")
    
    try:
        # Get marketplace analytics
        marketplace_analytics = analytics_engine.calculate_marketplace_analytics(date_range)
        
        # KPI Cards
        st.subheader("Marketplace Overview")
        
        # Top row KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Sellers",
                f"{marketplace_analytics.total_sellers:,}",
                help="Total number of sellers in the marketplace"
            )
        
        with col2:
            st.metric(
                "Active Sellers",
                f"{marketplace_analytics.active_sellers:,}",
                help="Number of currently active sellers"
            )
        
        with col3:
            st.metric(
                "Avg Trust Score",
                f"{marketplace_analytics.average_trust_score:.1f}",
                help="Average Trust Score across all sellers (0-100)"
            )
        
        with col4:
            st.metric(
                "Total Orders",
                f"{marketplace_analytics.total_orders:,}",
                help="Total number of orders in the selected time period"
            )
        
        with col5:
            st.metric(
                "Total Revenue",
                f"${marketplace_analytics.total_revenue:,.2f}",
                help="Total revenue from all orders"
            )
        
        # Second row KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Healthy Sellers",
                f"{marketplace_analytics.healthy_sellers:,}",
                help="Sellers with Trust Score 80-100",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Monitor Sellers",
                f"{marketplace_analytics.monitor_sellers:,}",
                help="Sellers with Trust Score 60-79",
                delta_color="off"
            )
        
        with col3:
            st.metric(
                "High-Risk Sellers",
                f"{marketplace_analytics.high_risk_sellers:,}",
                help="Sellers with Trust Score 0-59",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Return Rate",
                f"{marketplace_analytics.overall_return_rate:.1f}%",
                help="Overall return rate across all orders"
            )
        
        with col5:
            st.metric(
                "Avg Rating",
                f"{marketplace_analytics.overall_average_rating:.2f}",
                help="Average customer rating (1-5 scale)"
            )
        
        st.markdown("---")
        
        # Risk Distribution Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            
            risk_data = {
                "Healthy": marketplace_analytics.healthy_sellers,
                "Monitor": marketplace_analytics.monitor_sellers,
                "High Risk": marketplace_analytics.high_risk_sellers
            }
            
            colors = {"Healthy": "#2ecc71", "Monitor": "#f39c12", "High Risk": "#e74c3c"}
            
            fig_risk = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title="Seller Risk Distribution",
                color=list(risk_data.keys()),
                color_discrete_map=colors,
                hole=0.4
            )
            
            fig_risk.update_traces(textposition='inside', textinfo='percent+label')
            fig_risk.update_layout(
                showlegend=True,
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            st.subheader("Trust Score Distribution")
            
            # Get Trust Score distribution from ranked sellers
            ranked_sellers = analytics_engine.rank_sellers_by_trust_score(limit=None, date_range=date_range)
            trust_scores = [seller.trust_score for seller in ranked_sellers]
            
            fig_trust = px.histogram(
                x=trust_scores,
                nbins=20,
                title="Distribution of Seller Trust Scores",
                labels={"x": "Trust Score", "y": "Number of Sellers"},
                color_discrete_sequence=["#3498db"]
            )
            
            fig_trust.update_layout(
                xaxis_title="Trust Score (0-100)",
                yaxis_title="Number of Sellers",
                height=400,
                margin=dict(l=0, r=0, t=30, b=0),
                bargap=0.1
            )
            
            # Add vertical lines for risk thresholds
            fig_trust.add_vline(x=80, line_dash="dash", line_color="#2ecc71", 
                              annotation_text="Healthy", annotation_position="top")
            fig_trust.add_vline(x=60, line_dash="dash", line_color="#f39c12", 
                              annotation_text="Monitor", annotation_position="top")
            
            st.plotly_chart(fig_trust, use_container_width=True)
        
        st.markdown("---")
        
        # Top Sellers Table
        st.subheader("Top Sellers by Trust Score")
        
        top_sellers = analytics_engine.rank_sellers_by_trust_score(limit=10, date_range=date_range)
        
        if top_sellers:
            seller_data = []
            for seller in top_sellers:
                seller_data.append({
                    "Seller": seller.seller_name,
                    "Seller ID": seller.seller_id,
                    "Category": seller.category,
                    "Region": seller.region,
                    "Trust Score": f"{seller.trust_score:.1f}",
                    "Risk Level": seller.risk_level.value.title(),
                    "Rating": f"{seller.rating_metrics.average_rating:.2f}",
                    "Return Rate": f"{seller.return_metrics.return_rate:.1f}%"
                })
            
            st.dataframe(
                seller_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Trust Score": st.column_config.NumberColumn(
                        "Trust Score",
                        format="%.1f",
                        help="Seller Trust Score (0-100)"
                    ),
                    "Risk Level": st.column_config.TextColumn(
                        "Risk Level",
                        help="Seller risk classification"
                    )
                }
            )
        else:
            st.info("No sellers found in the selected time period.")
        
        st.markdown("---")
        
        # Historical Trends
        st.subheader("Historical Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Trust Score Over Time**")
            # For now, show a placeholder - historical analytics needs more implementation
            st.info("Historical Trust Score trends will be available in the next update.")
        
        with col2:
            st.write("**Order Volume Over Time**")
            st.info("Historical order volume trends will be available in the next update.")
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        logger.error(f"Dashboard error: {e}", exc_info=True)
        
        st.info("Please ensure the database has been initialized and seeded with data.")
        st.code("python scripts/init_db.py\npython scripts/seed_data.py")


def render_seller_analytics():
    """Render the Seller Analytics page with basic seller selection."""
    st.title("Seller Analytics")
    st.markdown("---")
    
    # Seller selection
    st.subheader("Select Seller")
    
    # Get all sellers for dropdown
    try:
        with analytics_engine.db.get_connection() as conn:
            cursor = conn.execute("SELECT seller_id, seller_name FROM sellers ORDER BY seller_name")
            sellers = [{"id": row["seller_id"], "name": row["seller_name"]} for row in cursor.fetchall()]
        
        if sellers:
            seller_options = [f"{s['name']} ({s['id']})" for s in sellers]
            selected_seller = st.selectbox("Choose a seller to analyze", seller_options)
            
            if selected_seller:
                # Extract seller ID from selection
                seller_id = selected_seller.split("(")[-1].rstrip(")")
                
                try:
                    # Get seller analytics
                    seller_analytics = analytics_engine.calculate_seller_analytics(seller_id)
                    
                    st.markdown("---")
                    st.subheader(f"Analytics for {seller_analytics.seller_name}")
                    
                    # Basic seller info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Category", seller_analytics.category)
                    with col2:
                        st.metric("Region", seller_analytics.region)
                    with col3:
                        st.metric("Status", seller_analytics.status.title())
                    
                    # Trust Score and Risk
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Trust Score", f"{seller_analytics.trust_score:.1f}")
                    with col2:
                        st.metric("Risk Level", seller_analytics.risk_level.value.title())
                    
                    st.markdown("---")
                    st.info("🔍 Detailed seller analytics will be expanded in the next milestone.")
                    st.info("Current features include basic seller selection and Trust Score display.")
                    
                except Exception as e:
                    st.error(f"Error loading seller analytics: {str(e)}")
                    logger.error(f"Seller analytics error: {e}", exc_info=True)
        else:
            st.warning("No sellers found in the database.")
            st.info("Please seed the database with synthetic data first:")
            st.code("python scripts/seed_data.py")
            
    except Exception as e:
        st.error(f"Error loading sellers: {str(e)}")
        logger.error(f"Seller loading error: {e}", exc_info=True)
        st.info("Please ensure the database has been initialized and seeded with data.")
        st.code("python scripts/init_db.py\npython scripts/seed_data.py")


def render_reports():
    """Render the Reports page."""
    st.title("Reports")
    st.markdown("---")
    
    st.info(
        "📋 **Reports**\n\n"
        "Report generation and export functionality will be implemented here. "
        "This will include:\n"
        "- CSV export\n"
        "- Excel export\n"
        "- PDF reports\n"
        "- Custom report generation\n"
        "- Scheduled reports\n\n"
        "*Coming in the analytics implementation*"
    )
    
    # Placeholder for future reports content
    st.subheader("Available Reports")
    st.write("Report templates and generation options will appear here.")
    
    st.subheader("Export Options")
    st.write("Format selection and export configuration will appear here.")


def render_settings():
    """Render the Settings page."""
    st.title("Settings")
    st.markdown("---")
    
    st.info(
        "⚙️ **Settings**\n\n"
        "Application configuration and preferences will be implemented here. "
        "This will include:\n"
        "- Database configuration\n"
        "- Data refresh settings\n"
        "- Display preferences\n"
        "- User preferences\n\n"
        "*Coming in the analytics implementation*"
    )
    
    # Current configuration display
    st.subheader("Current Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Application Settings**")
        st.write(f"Environment: {settings.env}")
        st.write(f"Database Path: {settings.database_path}")
        st.write(f"Log Level: {settings.log_level}")
    
    with col2:
        st.write("**Data Settings**")
        st.write(f"Synthetic Data Seed: {settings.synthetic_data_seed}")
        st.write(f"Database Exists: {settings.database_path.exists()}")
    
    st.subheader("Future Settings")
    st.write("Additional configuration options will appear here.")
