import subprocess
import sys
import os


def run_pipeline():
    """Run the complete forensics analysis pipeline"""
    
    # Get the root directory of the project
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    # Complete pipeline steps in order
    steps = [
        # Step 1: Convert .evtx to XML
        "ingestion/src/ingest_evtx.py",
        
        # Step 2: Convert XML to JSON
        "parser/src/parse_xml.py",
        
        # Step 3: Normalize the JSON data  
        "normalizer/src/normalize.py",
        
        # Step 4: Run Sigma analysis
        "analysis/sigma_pipeline.py"
    ]

    results = []
    
    # Run each step one by one
    for i, step in enumerate(steps, 1):
        script_path = os.path.join(project_root, step)
        
        print(f"Step {i}/{len(steps)}: Running {step}")
        
        # Check if script file exists
        if not os.path.exists(script_path):
            return {
                "status": "failed",
                "failed_step": step,
                "error_message": f"Script not found: {script_path}"
            }

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        # If a step fails, stop the pipeline
        if result.returncode != 0:
            return {
                "status": "failed", 
                "failed_step": step,
                "error_message": result.stderr or result.stdout,
                "completed_steps": i-1
            }
        
        results.append({
            "step": step,
            "status": "success",
            "output": result.stdout[:200] if result.stdout else "Completed successfully"
        })

    # If all steps run successfully
    return {
        "status": "success",
        "message": f"Pipeline completed successfully. All {len(steps)} steps finished.",
        "results": results
    }
