"""
Log Statistics page for the LOGIC dashboard.
Displays log file statistics and provides detailed log data viewing capabilities.
"""

import streamlit as st
import pandas as pd
from services.data_service import load_log_statistics
from utils.helpers import create_suspicious_indicator


def render_log_statistics():
    """Render the log statistics page"""
    st.header("Log Analysis Statistics")
    
    # Initialize session state for selected log
    if 'selected_log' not in st.session_state:
        st.session_state.selected_log = None
    
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
        
        # Log sources as clickable buttons
        st.subheader("Log Sources")
        st.write("Click on a log source to view its data:")
        
        # Create buttons for each log source
        cols = st.columns(min(len(stats), 4))
        for i, (log_name, log_info) in enumerate(stats.items()):
            with cols[i % 4]:
                if st.button(f"{log_name}\n({log_info['events']:,} events)", 
                           key=f"log_{log_name}", 
                           use_container_width=True):
                    st.session_state.selected_log = log_name
        
        # Display selected log data
        if st.session_state.selected_log and st.session_state.selected_log in stats:
            selected_log = st.session_state.selected_log
            log_data = stats[selected_log]['data']
            
            st.subheader(f"{selected_log} Log Data")
            
            # Log info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Events in this log", f"{len(log_data):,}")
            with col2:
                st.metric("File size", f"{stats[selected_log]['size_mb']:.2f} MB")
            
            # Clear selection button
            if st.button("← Back to Overview", key="back_to_overview"):
                st.session_state.selected_log = None
                st.rerun()
            
            # Display log data in table
            if log_data:
                # Convert to DataFrame for better display
                df = pd.DataFrame(log_data)
                
                # Forensic fields enhancement for Security logs
                show_forensic_fields = False
                if selected_log.lower() == 'security':
                    show_forensic_fields = st.checkbox("Show forensic fields", value=False, 
                                                      help="Display columns most relevant for forensic analysis and threat detection")
                
                # Determine which columns to display
                if show_forensic_fields and selected_log.lower() == 'security':
                    # Define forensic columns to look for
                    forensic_columns = [
                        'event_id', 'EventID',  # Event ID variations
                        'timestamp', 'TimeCreated',  # Time variations
                        'computer', 'Computer', 'Hostname',  # Computer name variations
                        'record_id', 'RecordID'  # Record ID
                    ]
                    
                    # Check for user-related fields in event_data
                    available_columns = []
                    
                    # Add basic columns that exist
                    for col in forensic_columns:
                        if col in df.columns:
                            available_columns.append(col)
                    
                    # Check if we have event_data column with nested forensic fields
                    if 'event_data' in df.columns:
                        # Extract forensic fields from event_data if they exist
                        forensic_event_fields = [
                            'TargetUserName', 'SubjectUserName', 'LogonType', 
                            'NewProcessName', 'ProcessName', 'ParentProcessName',
                            'IpAddress', 'SourceIP', 'CommandLine', 'Status', 'FailureReason'
                        ]
                        
                        # Extract event_data fields and add them as separate columns
                        for field in forensic_event_fields:
                            if not df.empty:
                                # Check if this field exists in any event_data
                                field_exists = False
                                for idx, row in df.head(10).iterrows():  # Check first 10 rows
                                    if isinstance(row.get('event_data'), dict) and field in row['event_data']:
                                        field_exists = True
                                        break
                                
                                if field_exists:
                                    # Create new column from event_data field
                                    df[field] = df['event_data'].apply(
                                        lambda x: x.get(field, '') if isinstance(x, dict) else ''
                                    )
                                    available_columns.append(field)
                    
                    # Add Suspicious Indicator column for Security logs
                    if 'event_id' in df.columns:
                        df['Suspicious_Indicator'] = df['event_id'].apply(create_suspicious_indicator)
                        available_columns.append('Suspicious_Indicator')
                    
                    # Create display dataframe with available forensic columns
                    if available_columns:
                        df_display = df[available_columns]
                        st.info(f"Showing {len(available_columns)} forensic columns")
                    else:
                        df_display = df.iloc[:, :10]  # Fallback to first 10 columns
                        st.warning("No specific forensic columns found, showing first 10 columns")
                else:
                    # Standard display: show first few columns if there are many
                    if len(df.columns) > 10:
                        st.warning(f"Showing first 10 columns out of {len(df.columns)} total columns")
                        df_display = df.iloc[:, :10]
                    else:
                        df_display = df
                
                # Search/filter functionality
                search_term = st.text_input("Search in log data:", placeholder="Enter search term...")
                
                if search_term:
                    # Search across all columns
                    mask = df_display.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    df_display = df_display[mask]
                    st.info(f"Found {len(df_display)} matching records")
                
                # Display the data
                st.dataframe(df_display, use_container_width=True, height=400)
                
                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_log}_log_data.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data available for this log")
    else:
        st.warning("No log statistics available. Please ensure logs have been processed.")