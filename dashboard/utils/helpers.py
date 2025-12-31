"""
Utility functions for the LOGIC dashboard.
Contains helper functions for data processing and formatting.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def create_suspicious_indicator(event_id):
    """
    Create a suspicious indicator based on Windows Security Event ID
    Simple rule-based logic for forensic analysis
    """
    # Convert to string in case it's stored as integer
    event_id_str = str(event_id)
    
    # Define suspicious indicators based on common security events
    if event_id_str == '4672':
        return 'Privilege Use'
    elif event_id_str == '4688':
        return 'Process Execution'
    elif event_id_str == '4625':
        return 'Failed Logon'
    elif event_id_str == '4624':
        return 'Successful Logon'
    elif event_id_str == '4648':
        return 'Explicit Credential Use'
    elif event_id_str == '4720':
        return 'User Account Created'
    elif event_id_str == '4726':
        return 'User Account Deleted'
    elif event_id_str == '4634':
        return 'Account Logoff'
    elif event_id_str == '4647':
        return 'User Initiated Logoff'
    elif event_id_str == '4768':
        return 'Kerberos TGT Requested'
    elif event_id_str == '4769':
        return 'Kerberos Service Ticket'
    elif event_id_str == '4776':
        return 'NTLM Authentication'
    elif event_id_str in ['4798', '4799']:
        return 'Group Membership Change'
    elif event_id_str in ['4732', '4733']:
        return 'Group Member Added/Removed'
    else:
        return 'Normal'


def create_anomaly_timeline(df):
    """Create timeline visualization of anomalies"""
    if df.empty:
        return go.Figure()
    
    df['window_start'] = pd.to_datetime(df['window_start'])
    
    fig = go.Figure()
    
    # Add anomaly points
    anomalous = df[df['is_anomalous'] == True]
    normal = df[df['is_anomalous'] == False]
    
    fig.add_trace(go.Scatter(
        x=anomalous['window_start'],
        y=anomalous['anomaly_score'],
        mode='markers',
        marker=dict(color='red', size=10, symbol='diamond'),
        name='Anomalies',
        hovertemplate='<b>Anomaly Detected</b><br>Time: %{x}<br>Score: %{y:.4f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=normal['window_start'],
        y=normal['anomaly_score'],
        mode='markers',
        marker=dict(color='green', size=6),
        name='Normal',
        hovertemplate='<b>Normal Activity</b><br>Time: %{x}<br>Score: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Anomaly Detection Timeline',
        xaxis_title='Time',
        yaxis_title='Anomaly Score',
        hovermode='closest',
        height=400
    )
    
    return fig


def create_anomaly_distribution(df):
    """Create distribution plot of anomaly scores"""
    if df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df, 
        x='anomaly_score',
        color='is_anomalous',
        title='Distribution of Anomaly Scores',
        labels={'anomaly_score': 'Anomaly Score', 'count': 'Frequency'},
        color_discrete_map={True: 'red', False: 'green'}
    )
    
    return fig