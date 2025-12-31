"""
Pipeline Control page for the LOGIC dashboard.
Provides comprehensive manual pipeline execution and status monitoring.
"""

import os
import streamlit as st
import requests
import json
from datetime import datetime


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:4000/api/pipeline")


def get_pipeline_steps():
    """Fetch available pipeline steps from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/steps", timeout=5)
        if response.status_code == 200:
            return response.json().get("steps", {})
    except Exception as e:
        st.error(f"Failed to fetch pipeline steps: {e}")
    return {}


def run_step(step_id: str):
    """Execute a single pipeline step"""
    try:
        with st.spinner(f"Executing {step_id}..."):
            response = requests.post(f"{API_BASE_URL}/run/{step_id}", timeout=3600)
            return response.json()
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def run_pipeline_full():
    """Execute the complete pipeline"""
    try:
        with st.spinner("Running complete pipeline..."):
            response = requests.post(f"{API_BASE_URL}/run", timeout=3600)
            return response.json()
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def render_step_result(result: dict, step_name: str = ""):
    """Render the result of a pipeline step execution"""
    status = result.get("status", "unknown")
    
    if status == "success":
        st.success(f"{step_name or 'Step'} completed successfully")
        if result.get("output"):
            with st.expander("View Output"):
                st.code(result.get("output"), language="text")
    elif status == "failed":
        st.error(f"{step_name or 'Step'} failed")
        if result.get("error"):
            st.code(result.get("error"), language="text")
    elif status == "timeout":
        st.warning(f"{step_name or 'Step'} timed out")
    else:
        st.error(f"{step_name or 'Step'} error: {result.get('error_message', 'Unknown error')}")


def render_pipeline_control():
    """Render the pipeline control page"""
    st.header("Pipeline Management & Control")
    st.write("Full backend pipeline control with granular step execution")
    
    # Initialize session state
    if 'pipeline_results' not in st.session_state:
        st.session_state.pipeline_results = []
    
    # Get available steps
    steps = get_pipeline_steps()
    
    if not steps:
        st.error("Unable to load pipeline steps. Ensure the API is running.")
        return
    
    # Sort steps by order
    sorted_steps = sorted(steps.items(), key=lambda x: x[1].get("order", 999))
    
    # ========================================
    # Section 1: Quick Actions
    # ========================================
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Run Full Pipeline", use_container_width=True, type="primary"):
            result = run_pipeline_full()
            
            st.subheader("Pipeline Execution Results")
            
            if result.get("status") == "success":
                st.success(f"Pipeline completed successfully!")
                st.metric("Completed Steps", result.get("completed_steps", 0))
                
                # Display individual step results
                for step_result in result.get("results", []):
                    render_step_result(step_result, step_result.get("step_name", ""))
            else:
                st.error(f"Pipeline failed at step: {result.get('failed_step', 'Unknown')}")
                st.metric("Completed Steps", result.get("completed_steps", 0))
                
                # Display step results
                for step_result in result.get("results", []):
                    render_step_result(step_result, step_result.get("step_name", ""))
    
    with col2:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.pipeline_results = []
            st.rerun()
    
    with col3:
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
    
    # ========================================
    # Section 2: Individual Step Execution
    # ========================================
    st.markdown("---")
    st.subheader("Individual Step Execution")
    st.write("Run specific pipeline steps independently")
    
    # Create columns for each step button
    cols = st.columns(min(len(sorted_steps), 4))
    
    for idx, (step_id, step_info) in enumerate(sorted_steps):
        with cols[idx % 4]:
            step_name = step_info.get("name", step_id.title())
            step_order = step_info.get("order", 0)
            
            if st.button(
                f"#{step_order} {step_name}",
                use_container_width=True,
                key=f"btn_{step_id}"
            ):
                result = run_step(step_id)
                st.session_state.pipeline_results.append({
                    "step_id": step_id,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                st.rerun()
    
    # Display step information
    with st.expander("Step Details"):
        for step_id, step_info in sorted_steps:
            st.markdown(f"""
            **#{step_info.get('order', 0)} {step_info.get('name', step_id)}**
            - *Description:* {step_info.get('description', 'No description')}
            - *Script:* `{step_info.get('script', 'Unknown')}`
            """)
    
    # ========================================
    # Section 3: Execution History
    # ========================================
    if st.session_state.pipeline_results:
        st.markdown("---")
        st.subheader("📊 Execution History")
        
        for i, execution in enumerate(reversed(st.session_state.pipeline_results[-10:])):
            step_id = execution.get("step_id", "Unknown")
            result = execution.get("result", {})
            timestamp = execution.get("timestamp", "")
            
            step_info = steps.get(step_id, {})
            step_name = step_info.get("name", step_id.title())
            
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    status_text = {
                        "success": "SUCCESS",
                        "failed": "FAILED",
                        "timeout": "TIMEOUT",
                        "error": "ERROR"
                    }.get(result.get("status"), "UNKNOWN")
                    
                    st.write(f"{status_text} **{step_name}**")
                
                with col2:
                    status_color = {
                        "success": "green",
                        "failed": "red",
                        "timeout": "orange",
                        "error": "red"
                    }.get(result.get("status"), "gray")
                    
                    st.write(f":{status_color}[{result.get('status', 'unknown').upper()}]")
                
                with col3:
                    st.write(f"*{timestamp}*" if timestamp else "")
                
                # Show output/error details
                if result.get("output"):
                    with st.expander(f"Output - {step_name}"):
                        st.code(result.get("output"), language="text")
                
                if result.get("error"):
                    with st.expander(f"Error - {step_name}"):
                        st.code(result.get("error"), language="text")
    
    # ========================================
    # Section 4: Advanced Options
    # ========================================
    st.markdown("---")
    st.subheader("Advanced Options")
    
    with st.expander("Custom Step Sequence"):
        st.write("Select steps to run in a custom order:")
        
        selected_steps = []
        for step_id, step_info in sorted_steps:
            if st.checkbox(
                f"{step_info.get('name', step_id)}",
                key=f"select_{step_id}"
            ):
                selected_steps.append(step_id)
        
        if selected_steps and st.button("Run Custom Sequence", type="primary"):
            result_data = {
                "status": "info",
                "message": "Custom sequence execution selected steps in order"
            }
            
            for step_id in selected_steps:
                result = run_step(step_id)
                step_info = steps.get(step_id, {})
                render_step_result(result, step_info.get("name", step_id))
                
                # Stop if a step fails
                if result.get("status") != "success":
                    st.warning("Stopping sequence due to step failure")
                    break
