from fastapi import APIRouter
from services.pipeline_service import (
    run_pipeline, 
    get_pipeline_steps, 
    run_step,
    run_steps_in_sequence
)

router = APIRouter()


@router.get("/steps")
def get_steps():
    """Get available pipeline steps"""
    return {"steps": get_pipeline_steps()}


@router.post("/run/{step_id}")
def run_single_step(step_id: str):
    """Run a specific pipeline step"""
    result = run_step(step_id)
    return result


@router.post("/run-sequence")
def run_sequence(step_ids: list[str]):
    """Run multiple steps in sequence"""
    result = run_steps_in_sequence(step_ids)
    return result


@router.post("/run")
def run_full_pipeline():
    """Run the complete pipeline"""
    result = run_pipeline()
    return result
