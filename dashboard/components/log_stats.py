import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import json

def load_log_statistics():
    """Load and analyze log file statistics"""
    stats = {}
    
    # Check processed logs
    processed_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'json')
    if os.path.exists(processed_path):
        for file in os.listdir(processed_path):
            if file.endswith('.json'):
                file_path = os.path.join(processed_path, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        stats[file.replace('.json', '')] = {
                            'events': len(data),
                            'size_mb': os.path.getsize(file_path) / (1024 * 1024)
                        }
                except:
                    pass
    
    return stats

def display_log_overview():
    """Display log statistics overview"""
    st.header("Log Analysis Statistics")
    
    stats = load_log_statistics()
    
    if stats:
        # Overview metrics
        total_events = sum(log['events'] for log in stats.values())
        total_size = sum(log['size_mb'] for log in stats.values())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Events Processed", f"{total_events:,}")
        
        with col2:
            st.metric("Total Data Size", f"{total_size:.2f} MB")
        
        with col3:
            st.metric("Log Sources", len(stats))
        
        # Log breakdown
        st.subheader("Log Source Breakdown")
        
        # Create DataFrame for visualization
        df = pd.DataFrame([
            {'Log Source': name, 'Events': data['events'], 'Size (MB)': data['size_mb']}
            for name, data in stats.items()
        ])
        
        # Bar chart of events by source
        fig_events = px.bar(
            df, 
            x='Log Source', 
            y='Events',
            title='Events by Log Source',
            color='Log Source'
        )
        st.plotly_chart(fig_events, use_container_width=True)
        
        # Pie chart of data distribution
        fig_size = px.pie(
            df,
            values='Size (MB)',
            names='Log Source',
            title='Data Size Distribution'
        )
        st.plotly_chart(fig_size, use_container_width=True)
        
        # Detailed table
        st.subheader("Detailed Statistics")
        st.dataframe(df, use_container_width=True)
    
    else:
        st.warning("No log statistics available. Please ensure logs have been processed.")

if __name__ == "__main__":
    display_log_overview()