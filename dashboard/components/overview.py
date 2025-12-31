"""
Overview page for the LOGIC dashboard.
Displays system metrics, recent anomalies, and overall status.
"""

import streamlit as st
import pandas as pd
from services.data_service import load_detection_results


def render_overview():
    """Render the system overview page"""
    st.header("System Overview")
    
    # Load data
    anomaly_df = load_detection_results()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_windows = len(anomaly_df)
        st.metric("Total Time Windows", total_windows)
        
    with col2:
        anomalies = len(anomaly_df[anomaly_df['is_anomalous'] == True]) if not anomaly_df.empty else 0
        st.metric("Anomalies Detected", anomalies, delta=None if anomalies == 0 else f"+{anomalies}")
        
    with col3:
        if not anomaly_df.empty and len(anomaly_df) > 0:
            last_scan = pd.to_datetime(anomaly_df['window_end']).max().strftime('%Y-%m-%d %H:%M')
            st.metric("Last Analysis", last_scan)
        else:
            st.metric("Last Analysis", "No data")
            
    with col4:
        status = "Operational" if not anomaly_df.empty else "No Data"
        st.metric("System Status", status)
    
    # Recent alerts
    if not anomaly_df.empty:
        st.subheader("Recent Anomalies")
        recent_anomalies = anomaly_df[anomaly_df['is_anomalous'] == True].tail(5)
        
        if not recent_anomalies.empty:
            for _, row in recent_anomalies.iterrows():
                st.markdown(f"""
                <div class="alert-high">
                    <strong>Anomaly Detected</strong><br>
                    Time: {pd.to_datetime(row['window_start']).strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Score: {row['anomaly_score']:.4f}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No recent anomalies detected")