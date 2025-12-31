import subprocess
import sys
import os
from typing import Dict, List, Optional


# Pipeline steps configuration
PIPELINE_STEPS = {
    "ingestion": {
        "name": "Log Ingestion",
        "description": "Convert .evtx files to XML format",
        "script": "ingestion/src/ingest_evtx.py",
        "order": 1
    },
    "parsing": {
        "name": "Log Parsing", 
        "description": "Convert XML to JSON format",
        "script": "parser/src/parse_xml.py",
        "order": 2
    },
    "normalization": {
        "name": "Data Normalization",
        "description": "Normalize and standardize JSON data",
        "script": "normalizer/src/normalize.py",
        "order": 3
    },
    "sigma_analysis": {
        "name": "Sigma Rule Analysis",
        "description": "Run Sigma rule detection on logs",
        "script": "analysis/sigma_pipeline.py",
        "order": 4
    }
}


def get_pipeline_steps() -> Dict:
    """Get available pipeline steps"""
    return PIPELINE_STEPS


def run_step(step_id: str) -> Dict:
    """Run a specific pipeline step"""
    if step_id not in PIPELINE_STEPS:
        return {
            "status": "error",
            "message": f"Unknown step: {step_id}"
        }
    
    step_config = PIPELINE_STEPS[step_id]
    script_path = step_config["script"]
    
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    
    full_script_path = os.path.join(project_root, script_path)
    
    if not os.path.exists(full_script_path):
        return {
            "status": "failed",
            "step_id": step_id,
            "step_name": step_config["name"],
            "error_message": f"Script not found: {full_script_path}"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, full_script_path],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=3600  # 1 hour timeout
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "step_id": step_id,
            "step_name": step_config["name"],
            "return_code": result.returncode,
            "output": result.stdout[:500] if result.stdout else "",
            "error": result.stderr[:500] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "step_id": step_id,
            "step_name": step_config["name"],
            "error_message": "Step execution timed out"
        }
    except Exception as e:
        return {
            "status": "error",
            "step_id": step_id,
            "step_name": step_config["name"],
            "error_message": str(e)
        }


def run_steps_in_sequence(step_ids: List[str]) -> Dict:
    """Run multiple steps in sequence"""
    if not step_ids:
        return {
            "status": "error",
            "message": "No steps specified"
        }
    
    results = []
    failed_step = None
    
    # Validate all steps exist first
    for step_id in step_ids:
        if step_id not in PIPELINE_STEPS:
            return {
                "status": "error",
                "message": f"Unknown step: {step_id}"
            }
    
    # Run each step
    for step_id in step_ids:
        result = run_step(step_id)
        results.append(result)
        
        if result["status"] in ["failed", "timeout", "error"]:
            failed_step = step_id
            break
    
    return {
        "status": "success" if not failed_step else "failed",
        "total_steps": len(step_ids),
        "completed_steps": len([r for r in results if r["status"] == "success"]),
        "failed_step": failed_step,
        "results": results
    }


def run_pipeline() -> Dict:
    """Run the complete forensics analysis pipeline in order"""
    # Get all steps sorted by order
    all_steps = sorted(
        PIPELINE_STEPS.keys(),
        key=lambda x: PIPELINE_STEPS[x]["order"]
    )
    
    return run_steps_in_sequence(all_steps)
