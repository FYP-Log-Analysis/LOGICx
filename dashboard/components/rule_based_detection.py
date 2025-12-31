"""
Rule Based Detection page for the LOGIC dashboard.
Displays Sigma detection results with rule statistics and match details.
"""

import streamlit as st
import json
import os
import requests
from services.data_service import load_sigma_rules

API_BASE_URL = "http://localhost:4000/api/pipeline"
ANALYSIS_API_URL = "http://localhost:4000/api/analysis"


def load_sigma_detection_output():
    """Load Sigma detection results from the output/logs"""
    # This would be the actual output from sigma_pipeline.py
    # For now, return empty structure - will be populated when pipeline runs
    return []


def parse_detection_output():
    """Parse detection output to get statistics"""
    # Try to load from a results file if it exists
    results_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'detection_results', 'sigma_matches.json'
    )
    
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return {
        "matches": [],
        "matched_rules": [],
        "total_matches": 0
    }


def run_sigma_detection():
    """Execute Sigma rule detection via API"""
    try:
        with st.spinner("Running Sigma rule detection... This may take a few minutes."):
            response = requests.post(f"{API_BASE_URL}/run/sigma_analysis", timeout=3600)
            return response.json()
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_threat_insights():
    """Fetch AI-generated threat insights from LLM"""
    try:
        response = requests.post(f"{ANALYSIS_API_URL}/threat-insights", timeout=60)
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "analysis": None}


def check_insights_available():
    """Check if threat insights are available"""
    try:
        response = requests.get(f"{ANALYSIS_API_URL}/threat-insights/status", timeout=10)
        return response.json()
    except Exception:
        return {"status": "unavailable"}


def render_rule_based_detection():
    """Render the rule based detection page"""
    st.header("Sigma Rule Based Detection")
    st.write("Security threat detection using Sigma rules")
    
    # Initialize session state for detection results
    if 'last_detection_run' not in st.session_state:
        st.session_state.last_detection_run = None
    
    # Run Detection Button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("Run Sigma Detection", type="primary", width="stretch"):
            result = run_sigma_detection()
            
            if result.get("status") == "success":
                st.success("Sigma detection completed successfully!")
                st.session_state.last_detection_run = "success"
                
                if result.get("output"):
                    with st.expander("View Execution Output"):
                        st.code(result.get("output"), language="text")
                
                st.rerun()
            else:
                st.error(f"Detection failed: {result.get('error_message', 'Unknown error')}")
                if result.get("error"):
                    with st.expander("Error Details"):
                        st.code(result.get("error"), language="text")
    
    with col2:
        if st.session_state.last_detection_run:
            status_text = "Success" if st.session_state.last_detection_run == "success" else "Failed"
            st.info(f"Last run: {status_text}")
    
    with col3:
        if st.button("Refresh Results"):
            st.rerun()
    
    st.markdown("---")
    
    # Load available rules
    all_rules = load_sigma_rules()
    
    # Load detection results
    detection_data = parse_detection_output()
    matches = detection_data.get("matches", [])
    matched_rule_ids = set(detection_data.get("matched_rules", []))
    
    # ==========================================
    # LLM THREAT INSIGHTS SECTION
    # ==========================================
    if matches:
        st.subheader("AI-Powered Threat Analysis")
        
        insights_status = check_insights_available()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("Get AI-generated threat intelligence using LLM analysis")
            st.caption("Model: Llama 3.3 70B (Groq Cloud) • Fast • Accurate • Security-Focused")
        
        with col2:
            if st.button("Generate Insights", type="primary"):
                with st.spinner("Analyzing detections with AI..."):
                    insights = get_threat_insights()
                    
                    if insights.get("status") == "success":
                        st.session_state.threat_insights = insights.get("analysis")
                        st.success("Threat analysis completed!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {insights.get('error', 'Unknown error')}")
        
        # Display cached insights if available
        if hasattr(st.session_state, 'threat_insights') and st.session_state.threat_insights:
            with st.expander("View Threat Analysis", expanded=True):
                st.markdown(st.session_state.threat_insights)
                
                # Add refresh option
                if st.button("Regenerate Analysis", key="regen_insights"):
                    with st.spinner("Regenerating threat analysis..."):
                        insights = get_threat_insights()
                        if insights.get("status") == "success":
                            st.session_state.threat_insights = insights.get("analysis")
                            st.rerun()
        elif insights_status.get("status") == "available" and matches:
            st.info("Click 'Generate Insights' button above to get AI threat analysis")
    

    if not all_rules:
        st.error("No Sigma rules found. Please ensure rules are available in the analysis/detection/sigma/rules directory.")
        return
    
    # ==========================================
    # METRICS SECTION
    # ==========================================
    st.subheader("Detection Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Rules",
            len(all_rules),
            help="Total number of Sigma rules available"
        )
    
    with col2:
        used_rules = len(matched_rule_ids)
        st.metric(
            "Used Rules",
            used_rules,
            help="Number of rules that matched at least one event"
        )
    
    with col3:
        st.metric(
            "Matched Rules",
            len(matches),
            help="Total number of rule matches across all events"
        )
    
    with col4:
        if used_rules > 0:
            match_rate = (used_rules / len(all_rules)) * 100
            st.metric(
                "Detection Rate",
                f"{match_rate:.1f}%",
                help="Percentage of rules that found threats"
            )
        else:
            st.metric("Detection Rate", "0%")
    
    # ==========================================
    # DETECTION RESULTS SECTION
    # ==========================================
    st.markdown("---")
    st.subheader("Detection Results")
    
    if matches:
        # Summary stats
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity breakdown
            severity_counts = {}
            for match in matches:
                severity = match.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            st.write("**By Severity:**")
            for severity in ["critical", "high", "medium", "low"]:
                if severity in severity_counts:
                    st.write(f"**{severity.upper()}**: {severity_counts[severity]}")
        
        with col2:
            # Affected systems
            computers = set(match.get("computer", "Unknown") for match in matches)
            st.write(f"**Affected Systems:** {len(computers)}")
            
            # Time range
            if matches:
                st.write(f"**Total Alerts:** {len(matches)}")
        
        # ==========================================
        # DETAILED MATCHES TABLE
        # ==========================================
        st.markdown("---")
        st.subheader("Detection Details")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity:",
                ["All"] + ["critical", "high", "medium", "low"]
            )
        
        with col2:
            # Get unique rule titles
            rule_titles = sorted(set(match.get("rule_title", "Unknown") for match in matches))
            rule_filter = st.selectbox(
                "Filter by Rule:",
                ["All"] + rule_titles[:20]  # Limit to first 20 for UI
            )
        
        with col3:
            search_term = st.text_input("Search:", placeholder="Search in results...")
        
        # Apply filters
        filtered_matches = matches
        
        if severity_filter != "All":
            filtered_matches = [m for m in filtered_matches if m.get("severity") == severity_filter]
        
        if rule_filter != "All":
            filtered_matches = [m for m in filtered_matches if m.get("rule_title") == rule_filter]
        
        if search_term:
            search_lower = search_term.lower()
            filtered_matches = [
                m for m in filtered_matches
                if search_lower in str(m.get("rule_title", "")).lower() or
                   search_lower in str(m.get("computer", "")).lower() or
                   search_lower in str(m.get("event_id", "")).lower()
            ]
        
        st.info(f"Showing {len(filtered_matches)} of {len(matches)} detections")
        
        # Display matches
        for i, match in enumerate(filtered_matches[:100], 1):  # Limit to 100 for performance
            severity = match.get("severity", "unknown")
            
            with st.expander(f"[{severity.upper()}] #{i} - {match.get('rule_title', 'Unknown Rule')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Rule:** {match.get('rule_title', 'Unknown')}")
                    st.write(f"**Computer:** {match.get('computer', 'Unknown')}")
                    st.write(f"**Event ID:** {match.get('event_id', 'N/A')}")
                    st.write(f"**Timestamp:** {match.get('timestamp', 'N/A')}")
                
                with col2:
                    st.write(f"**Severity:** {severity.upper()}")
                    if match.get("rule_id"):
                        st.write(f"**Rule ID:** `{match.get('rule_id')}`")
                
                # Show event details if available
                if match.get("event_data"):
                    st.markdown("**Event Data:**")
                    st.json(match.get("event_data"))
        
        if len(filtered_matches) > 100:
            st.warning(f"Showing first 100 of {len(filtered_matches)} matches. Use filters to narrow results.")
    
    else:
        st.info("No detection results available yet.")
        st.write("""
        **To generate detection results:**
        1. Go to **Pipeline Management**
        2. Run the **Sigma Rule Analysis** step or the full pipeline
        3. Return to this page to view matched threats
        
        Detection results will show:
        - Rules that matched security events
        - Severity levels of threats
        - Affected systems and timestamps
        - Detailed event information
        """)
