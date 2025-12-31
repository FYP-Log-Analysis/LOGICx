"""
Data loading services for the LOGIC dashboard.
Handles loading of log files, detection results, and Sigma rules.
"""

import streamlit as st
import pandas as pd
import json
import os
import yaml


def load_detection_results():
    """Load anomaly detection results"""
    try:
        results_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'detection_results', 'isolation_forest_scores.json')
        with open(results_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading detection results: {e}")
        return pd.DataFrame()


def load_log_statistics():
    """Load and analyze log file statistics"""
    stats = {}
    
    # Check processed logs - go up two directories from services to reach data
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
                            'size_mb': os.path.getsize(file_path) / (1024 * 1024),
                            'file_path': file_path,
                            'data': data
                        }
                except:
                    pass
    
    return stats


def load_sigma_rules():
    """Load all Sigma rules from the detection directory"""
    rules = []
    
    # Path to Sigma rules directory
    rules_path = os.path.join(os.path.dirname(__file__), '..', '..', 'analysis', 'detection', 'sigma', 'rules')
    
    if os.path.exists(rules_path):
        # Walk through all subdirectories to find YAML rule files
        for root, dirs, files in os.walk(rules_path):
            for file in files:
                if file.endswith('.yml') or file.endswith('.yaml'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            rule_content = yaml.safe_load(f)
                            
                            # Extract rule information
                            rule_info = {
                                'filename': file,
                                'path': file_path,
                                'title': rule_content.get('title', 'Unknown'),
                                'id': rule_content.get('id', 'No ID'),
                                'description': rule_content.get('description', 'No description'),
                                'author': rule_content.get('author', 'Unknown'),
                                'date': rule_content.get('date', 'Unknown'),
                                'status': rule_content.get('status', 'Unknown'),
                                'tags': rule_content.get('tags', []),
                                'level': rule_content.get('level', 'medium'),
                                'logsource': rule_content.get('logsource', {}),
                                'detection': rule_content.get('detection', {}),
                                'references': rule_content.get('references', []),
                                'full_content': rule_content
                            }
                            rules.append(rule_info)
                    except Exception as e:
                        st.warning(f"Error loading rule {file}: {e}")
                        continue
    
    return rules


def search_users_in_logs(search_term):
    """Search for users across all logs"""
    results = []
    user_fields = ['SubjectUserName', 'TargetUserName', 'UserName', 'AccountName', 'User', 'LogonUser']
    
    stats = load_log_statistics()
    
    for log_name, log_info in stats.items():
        for event in log_info['data']:
            # Search in user-related fields
            for field in user_fields:
                if field in event and isinstance(event[field], str):
                    if search_term.lower() in event[field].lower():
                        results.append({
                            'log_source': log_name,
                            'user_field': field,
                            'user_value': event[field],
                            'event': event,
                            'timestamp': event.get('TimeCreated', event.get('CreationTime', 'Unknown')),
                            'event_id': event.get('EventID', event.get('Id', 'Unknown'))
                        })
            
            # Also search in all string fields for comprehensive results
            for key, value in event.items():
                if isinstance(value, str) and search_term.lower() in value.lower():
                    if not any(r['event'] == event for r in results):  # Avoid duplicates
                        results.append({
                            'log_source': log_name,
                            'user_field': key,
                            'user_value': value,
                            'event': event,
                            'timestamp': event.get('TimeCreated', event.get('CreationTime', 'Unknown')),
                            'event_id': event.get('EventID', event.get('Id', 'Unknown'))
                        })
    
    return results


def extract_all_users():
    """Extract all unique users from logs"""
    users = set()
    user_fields = ['SubjectUserName', 'TargetUserName', 'UserName', 'AccountName', 'User', 'LogonUser']
    
    stats = load_log_statistics()
    
    for log_name, log_info in stats.items():
        for event in log_info['data']:
            for field in user_fields:
                if field in event and isinstance(event[field], str) and event[field].strip():
                    # Filter out system accounts and empty values
                    username = event[field].strip()
                    if username and username not in ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE', '-', '']:
                        users.add(username)
    
    return sorted(list(users))