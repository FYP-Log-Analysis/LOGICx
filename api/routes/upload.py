from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from api.services.pipeline_service import run_pipeline

router = APIRouter()

@router.post("/upload")
async def upload_logs(file: UploadFile = File(...)):
    """Upload and process log files"""
    
    # Check file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files allowed")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded file
        zip_path = os.path.join(temp_dir, file.filename)
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract ZIP to raw_logs directory
        raw_logs_dir = Path(__file__).parent.parent.parent / "data" / "raw_logs"
        raw_logs_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(raw_logs_dir)
        
        # Run the pipeline
        result = run_pipeline()
        
        return {
            "message": "File uploaded and processed",
            "pipeline_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)