import streamlit as st
import requests
import json

def run_pipeline():
    """Trigger the pipeline via API"""
    try:
        response = requests.post("http://api:4000/api/pipeline/run")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Pipeline failed with status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_api_status():
    """Check if the API is accessible"""
    try:
        response = requests.get("http://api:4000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_pipeline_controls():
    """Display pipeline control interface"""
    st.subheader("Pipeline Controls")
    
    # API Status
    api_status = get_api_status()
    status_color = "Green" if api_status else "Red"
    st.write(f"API Status: {status_color} {'Connected' if api_status else 'Disconnected'}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Run Full Pipeline", disabled=not api_status):
            with st.spinner("Running pipeline..."):
                result = run_pipeline()
                if "error" in result:
                    st.error(f"Pipeline Error: {result['error']}")
                else:
                    st.success("Pipeline completed successfully!")
                    st.json(result)
    
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    with col3:
        if st.button("🔄 Check Status"):
            st.rerun()