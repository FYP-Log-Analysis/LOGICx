import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import json

def load_sigma_detection_results():
    """Load Sigma rule detection results"""
    return pd.DataFrame()

def create_severity_distribution(df):
    """Create pie chart of detection severity distribution"""
    if df.empty:
        return go.Figure()
    
    severity_counts = df['severity'].value_counts()
    
    colors = {
        'high': '#FF4444',
        'medium': '#FFB444', 
        'low': '#44FF44',
        'info': '#4444FF'
    }
    
    fig = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title='Detection Severity Distribution',
        color=severity_counts.index,
        color_discrete_map=colors
    )
    
    return fig

def create_detections_timeline(df):
    """Create timeline of detections"""
    if df.empty:
        return go.Figure()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Group by hour and count detections
    hourly = df.set_index('timestamp').resample('H').size().reset_index()
    hourly.columns = ['timestamp', 'count']
    
    fig = px.line(
        hourly,
        x='timestamp',
        y='count',
        title='Detections Over Time',
        labels={'count': 'Number of Detections', 'timestamp': 'Time'}
    )
    
    fig.update_traces(line=dict(color='#FF4444', width=3))
    
    return fig

def display_sigma_detections():
    """Display Sigma rule detection results"""
    st.header("Sigma Rule Detections")
    
    # Load detection data
    df = load_sigma_detection_results()
    
    if not df.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Detections", len(df))
        
        with col2:
            high_severity = len(df[df['severity'] == 'high'])
            st.metric("High Severity", high_severity, delta=f"+{high_severity}" if high_severity > 0 else None)
        
        with col3:
            unique_computers = df['computer'].nunique()
            st.metric("Affected Systems", unique_computers)
        
        with col4:
            if not df.empty:
                latest = pd.to_datetime(df['timestamp']).max().strftime('%H:%M')
                st.metric("Latest Detection", latest)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            severity_fig = create_severity_distribution(df)
            st.plotly_chart(severity_fig, use_container_width=True)
        
        with col2:
            timeline_fig = create_detections_timeline(df)
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Recent detections table
        st.subheader("Recent Detections")
        
        # Add severity styling
        def highlight_severity(row):
            if row['severity'] == 'high':
                return ['background-color: #FF444440'] * len(row)
            elif row['severity'] == 'medium':
                return ['background-color: #FFB44440'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Filter options
        st.subheader("Filter Detections")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.selectbox("Severity", ['All'] + list(df['severity'].unique()))
        
        with col2:
            computer_filter = st.selectbox("Computer", ['All'] + list(df['computer'].unique()))
        
        with col3:
            time_filter = st.selectbox("Time Range", ['All', 'Last Hour', 'Last 6 Hours', 'Last 24 Hours'])
        
        # Apply filters
        filtered_df = df.copy()
        
        if severity_filter != 'All':
            filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
        
        if computer_filter != 'All':
            filtered_df = filtered_df[filtered_df['computer'] == computer_filter]
        
        if time_filter != 'All':
            now = datetime.now()
            hours = {'Last Hour': 1, 'Last 6 Hours': 6, 'Last 24 Hours': 24}[time_filter]
            cutoff = now - timedelta(hours=hours)
            filtered_df = filtered_df[pd.to_datetime(filtered_df['timestamp']) >= cutoff]
        
        if len(filtered_df) != len(df):
            st.subheader(f"Filtered Results ({len(filtered_df)} detections)")
            st.dataframe(filtered_df, use_container_width=True)
    
    else:
        st.info("No Sigma detection results available yet.")
        st.markdown("""
        **Sigma Detection Status:**
        - 🔄 Sigma rules are configured in `/analysis/detection/sigma/rules/`
        - Detection results will appear here after processing
        - Run the analysis pipeline to generate detection data
        """)

if __name__ == "__main__":
    display_sigma_detections()