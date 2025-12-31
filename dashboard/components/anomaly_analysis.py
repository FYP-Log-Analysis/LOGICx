"""
Anomaly Analysis page for the LOGIC dashboard.
Displays anomaly detection results with charts and data tables.
"""

import streamlit as st
from services.data_service import load_detection_results
from utils.helpers import create_anomaly_timeline, create_anomaly_distribution


def render_anomaly_analysis():
    """Render the anomaly analysis page"""
    st.header("Anomaly Detection Analysis")
    
    anomaly_df = load_detection_results()
    
    if not anomaly_df.empty:
        # Timeline chart
        timeline_fig = create_anomaly_timeline(anomaly_df)
        st.plotly_chart(timeline_fig, width='stretch')
        
        # Distribution chart
        dist_fig = create_anomaly_distribution(anomaly_df)
        st.plotly_chart(dist_fig, width='stretch')
        
        # Data table
        st.subheader("Detection Results")
        st.dataframe(anomaly_df, use_container_width=True)
    else:
        st.warning("No anomaly detection data available")