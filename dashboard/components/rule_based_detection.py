"""
Rule Based Detection page for the LOGIC dashboard.
Displays Sigma detection rules organized by categories with filtering capabilities.
"""

import streamlit as st
import yaml
from services.data_service import load_sigma_rules


def render_rule_based_detection():
    """Render the rule based detection page"""
    st.header("Rule Based Detection System")
    st.write("Comprehensive threat detection rules for Windows security analysis")
    
    # Load all available rules
    rules = load_sigma_rules()
    
    if rules:
        # ===============================
        # 1. RULE SUMMARY SECTION
        # ===============================
        st.markdown("---")
        st.subheader("Rule Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rules", len(rules))
        
        with col2:
            # Count by status - Active rules include stable and test
            status_count = {}
            for rule in rules:
                status = rule['status']
                status_count[status] = status_count.get(status, 0) + 1
            active_rules = status_count.get('stable', 0) + status_count.get('test', 0)
            st.metric("Active Rules", active_rules)
        
        with col3:
            # Count high/critical severity rules
            level_count = {}
            for rule in rules:
                level = rule['level']
                level_count[level] = level_count.get(level, 0) + 1
            high_critical = level_count.get('high', 0) + level_count.get('critical', 0)
            st.metric("High/Critical", high_critical)
        
        with col4:
            # Count unique rule authors
            authors = set(rule['author'] for rule in rules if rule['author'] != 'Unknown')
            st.metric("Authors", len(authors))
        
        # ===============================
        # 2. RULE FILTERS SECTION
        # ===============================
        st.markdown("---")
        st.subheader("Rule Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filter by rule status
            status_options = ['All'] + sorted(list(set(rule['status'] for rule in rules)))
            selected_status = st.selectbox("Filter by Status:", status_options)
        
        with col2:
            # Filter by severity level
            level_options = ['All'] + sorted(list(set(rule['level'] for rule in rules)))
            selected_level = st.selectbox("Filter by Severity:", level_options)
        
        with col3:
            # Search functionality
            search_term = st.text_input("Search Rules:", placeholder="Enter keywords to search...")
        
        # Apply filters to rules
        filtered_rules = rules
        
        if selected_status != 'All':
            filtered_rules = [r for r in filtered_rules if r['status'] == selected_status]
        
        if selected_level != 'All':
            filtered_rules = [r for r in filtered_rules if r['level'] == selected_level]
        
        if search_term:
            search_lower = search_term.lower()
            filtered_rules = [r for r in filtered_rules if 
                            search_lower in r['title'].lower() or 
                            search_lower in r['description'].lower()]
        
        # ===============================
        # 3. RULE CATEGORIES SECTION
        # ===============================
        st.markdown("---")
        st.subheader("Rule Categories")
        st.write("Rules organized by MITRE ATT&CK techniques and tactics")
        
        # Categorize rules by MITRE ATT&CK tags
        categories = {}
        
        for rule in filtered_rules:
            # Extract MITRE ATT&CK categories from tags
            rule_categories = []
            for tag in rule['tags']:
                if tag.startswith('attack.'):
                    # Extract technique/tactic (e.g., attack.defense-evasion -> defense-evasion)
                    category = tag.replace('attack.', '').split('.')[0]
                    rule_categories.append(category)
            
            # If no MITRE tags, categorize as 'other'
            if not rule_categories:
                rule_categories = ['other']
            
            # Add rule to each of its categories
            for category in rule_categories:
                if category not in categories:
                    categories[category] = []
                categories[category].append(rule)
        
        # Define category display names
        category_info = {
            'initial-access': {'name': 'Initial Access'},
            'execution': {'name': 'Execution'},
            'persistence': {'name': 'Persistence'},
            'privilege-escalation': {'name': 'Privilege Escalation'},
            'defense-evasion': {'name': 'Defense Evasion'},
            'credential-access': {'name': 'Credential Access'},
            'discovery': {'name': 'Discovery'},
            'lateral-movement': {'name': 'Lateral Movement'},
            'collection': {'name': 'Collection'},
            'command-and-control': {'name': 'Command & Control'},
            'exfiltration': {'name': 'Exfiltration'},
            'impact': {'name': 'Impact'},
            'other': {'name': 'Other/Miscellaneous'}
        }
        
        # Sort categories by number of rules (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Display category overview metrics
        if len(sorted_categories) > 0:
            cols = st.columns(min(len(sorted_categories), 4))
            for i, (category, rules_in_cat) in enumerate(sorted_categories[:4]):
                with cols[i]:
                    name = category_info.get(category, {}).get('name', category.title())
                    st.metric(f"{name}", len(rules_in_cat))
        
        # ===============================
        # 4. RULE BROWSER SECTION
        # ===============================
        st.markdown("---")
        st.subheader("Rule Browser")
        
        if filtered_rules:
            st.success(f"Displaying {len(filtered_rules)} rules across {len(categories)} categories")
            
            # Display rules grouped by category
            for category, rules_in_category in sorted_categories:
                # Get category display info
                display_name = category_info.get(category, {}).get('name', category.title())
                
                # Create expandable section for each category
                with st.expander(f"**{display_name}** ({len(rules_in_category)} rules)", expanded=False):
                    
                    # Display rules in this category as cards
                    for i, rule in enumerate(rules_in_category):
                        
                        # Rule card container
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                                <h4>{rule['title']}</h4>
                                <p><strong>Severity:</strong> {rule['level'].upper()} | <strong>Status:</strong> {rule['status'].title()}</p>
                                <p><strong>Description:</strong> {rule['description'][:150]}{'...' if len(rule['description']) > 150 else ''}</p>
                                <p><strong>Author:</strong> {rule['author']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show details button (using toggle instead of nested expander)
                            if st.button(f"📋 View Details: {rule['title'][:50]}...", key=f"details_{category}_{i}", use_container_width=True):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"**Full Description:** {rule['description']}")
                                    st.markdown(f"**Author:** {rule['author']}")
                                    st.markdown(f"**Date:** {rule['date']}")
                                    
                                    if rule['references']:
                                        st.markdown("**References:**")
                                        for ref in rule['references'][:3]:
                                            st.markdown(f"- {ref}")
                                
                                with col2:
                                    st.markdown(f"**Rule ID:** `{rule['id']}`")
                                    st.markdown(f"**Severity:** `{rule['level']}`")
                                    st.markdown(f"**Status:** `{rule['status']}`")
                                    
                                    if rule['tags']:
                                        st.markdown("**MITRE Tags:**")
                                        mitre_tags = [tag for tag in rule['tags'] if tag.startswith('attack.')][:3]
                                        for tag in mitre_tags:
                                            st.markdown(f"- `{tag}`")
                                    
                                    # Log source information
                                    if rule['logsource']:
                                        st.markdown("**Log Source:**")
                                        logsource = rule['logsource']
                                        if 'product' in logsource:
                                            st.markdown(f"Product: `{logsource['product']}`")
                                        if 'service' in logsource:
                                            st.markdown(f"Service: `{logsource['service']}`")
                                
                                # Detection logic preview (only for detailed view)
                                if rule['detection']:
                                    st.markdown("**Detection Logic:**")
                                    detection_str = yaml.dump(rule['detection'], default_flow_style=False)
                                    st.code(detection_str, language='yaml')
        else:
            st.warning("No rules match the current filters. Try adjusting your search criteria.")
    else:
        st.error("No detection rules found. Please ensure Sigma rules are available in the analysis/detection/sigma/rules directory.")