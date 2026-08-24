"""
Main Streamlit application for STAP.

This is the entry point for the Streamlit application.
Run with: streamlit run src/ui/app.py
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from src.config.settings import settings
from src.utils.logger import setup_logging, get_logger
from src.ui.pages import (
    render_dashboard,
    render_seller_analytics,
    render_reports,
    render_settings
)

# Set up logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title=settings.app_page_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Application branding
    st.title(settings.app_title)
    st.markdown("---")
    
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        
        page = st.radio(
            "Select Page",
            ["Dashboard", "Seller Analytics", "Reports", "Settings"],
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        # Update session state when navigation changes
        st.session_state.page = page
        
        st.markdown("---")
        st.subheader("About")
        st.markdown(
            """
            **STAP**  
            Seller Trust Analytics Platform
            
            Version 0.1.0
            
            Analytics platform for marketplace
            managers and operations teams.
            """
        )
    
    # Route to selected page
    try:
        if page == "Dashboard":
            render_dashboard()
        elif page == "Seller Analytics":
            render_seller_analytics()
        elif page == "Reports":
            render_reports()
        elif page == "Settings":
            render_settings()
        else:
            st.error("Unknown page selected")
            logger.error(f"Unknown page selected: {page}")
    except Exception as e:
        st.error(f"An error occurred while rendering the page: {e}")
        logger.error(f"Page rendering error: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting STAP application")
    main()
