"""
LOGIC Dashboard - Main Application
A Windows log analysis and threat detection dashboard built with Streamlit.

This is the main entry point that handles:
- Page configuration and CSS styling
- Navigation bar rendering
- Page routing to individual render functions
"""

import streamlit as st
import os
import sys

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import page render functions
from components.overview import render_overview
from components.anomaly_analysis import render_anomaly_analysis
from components.rule_based_detection import render_rule_based_detection
from components.log_statistics import render_log_statistics
from components.pipeline_control import render_pipeline_control

# Configure page
st.set_page_config(
    page_title="LOGIC - Log Analysis Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for purple theme
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #9B59B6;
        text-align: center;
        margin-bottom: 1rem;
    }
    .navbar {
        background: linear-gradient(90deg, #2C3E50 0%, #4A148C 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .nav-button {
        background: transparent;
        border: 2px solid #9B59B6;
        color: #9B59B6;
        padding: 0.5rem 1rem;
        margin: 0 0.5rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .nav-button:hover {
        background: #9B59B6;
        color: white;
    }
    .nav-button.active {
        background: #9B59B6;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #8E44AD;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-medium {
        background-color: #AB47BC;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-low {
        background-color: #CE93D8;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Override Streamlit's default styling with purple theme */
    .stButton > button {
        background-color: #9B59B6;
        color: white;
        border: 1px solid #8E44AD;
    }
    .stButton > button:hover {
        background-color: #8E44AD;
        color: white;
        border: 1px solid #7B1FA2;
    }
    .stSidebar {
        background-color: #2C3E50;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #9B59B6;
    }
    </style>
""", unsafe_allow_html=True)


def render_navigation():
    """Render the sidebar navigation"""
    # Main header in the main area
    st.markdown('<h1 class="main-header">LOGIC Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Windows Log Analysis & Threat Detection</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Navigation options
        nav_options = [
            "Overview",
            "Anomaly Analysis", 
            "Rule Based Detection",
            "Log Statistics",
            "Pipeline Control"
        ]
        
        # Initialize session state for selected page
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = "Overview"
        
        # Create navigation buttons in sidebar
        for option in nav_options:
            if st.button(option, key=f"nav_{option}", use_container_width=True):
                st.session_state.selected_page = option
    
    return st.session_state.selected_page


def main():
    """Main application function"""
    # Render navigation and get selected page
    current_page = render_navigation()
    
    # Route to the appropriate page render function
    if current_page == "Overview":
        render_overview()
    elif current_page == "Anomaly Analysis":
        render_anomaly_analysis()
    elif current_page == "Rule Based Detection":
        render_rule_based_detection()
    elif current_page == "Log Statistics":
        render_log_statistics()
    elif current_page == "Pipeline Control":
        render_pipeline_control()


if __name__ == "__main__":
    main()