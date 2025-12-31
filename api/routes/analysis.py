"""
Analysis routes for threat intelligence and LLM-based insights.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
from api.services.llm_service import analyze_detection_results, analyze_specific_match
import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/threat-insights")
async def get_threat_insights() -> Dict:
    """
    Generate AI-powered threat analysis using Groq LLM.
    Analyzes detection results and provides security insights and recommendations.
    """
    
    try:
        # Load detection results from file
        results_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'detection_results', 'sigma_matches.json'
        )
        
        if not os.path.exists(results_file):
            error_msg = "No detection results found. Run Sigma detection first."
            logger.error(error_msg)
            raise HTTPException(
                status_code=404,
                detail=error_msg
            )
        
        with open(results_file, 'r') as f:
            detection_data = json.load(f)
        
        # Get matched rules
        matched_rules = detection_data.get("matched_rules", [])
        
        # Analyze with LLM
        logger.info(f"Calling LLM analysis with {len(detection_data.get('matches', []))} matches")
        analysis = analyze_detection_results(detection_data, matched_rules)
        
        if analysis.get("status") == "error":
            error_msg = f"LLM analysis error: {analysis.get('error_message')}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        return {
            "status": "success",
            "analysis": analysis.get("analysis"),
            "detection_summary": analysis.get("detection_summary")
        }
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=404,
            detail="Detection results file not found. Run Sigma detection first."
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/threat-insights/{rule_id}")
async def analyze_rule_match(rule_id: str) -> Dict:
    """
    Analyze a specific rule match for detailed threat context.
    
    Args:
        rule_id: The rule ID to analyze
    """
    
    try:
        # Load detection results
        results_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'detection_results', 'sigma_matches.json'
        )
        
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="No detection results found.")
        
        with open(results_file, 'r') as f:
            detection_data = json.load(f)
        
        # Find the match with the given rule_id
        matches = detection_data.get("matches", [])
        target_match = next((m for m in matches if m.get("rule_id") == rule_id), None)
        
        if not target_match:
            raise HTTPException(status_code=404, detail=f"No match found for rule {rule_id}")
        
        # Analyze specific match
        analysis = analyze_specific_match(target_match)
        
        if analysis.get("status") == "error":
            raise HTTPException(status_code=500, detail=analysis.get("error_message"))
        
        return {
            "status": "success",
            "analysis": analysis.get("analysis"),
            "rule_id": rule_id,
            "match_details": target_match
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threat-insights/status")
async def get_insights_status() -> Dict:
    """
    Check if threat insights are available (detection results exist).
    """
    
    results_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'detection_results', 'sigma_matches.json'
    )
    
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
            return {
                "status": "available",
                "total_matches": data.get("total_matches", 0),
                "matched_rules": len(data.get("matched_rules", []))
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    else:
        return {
            "status": "no_data",
            "message": "No detection results available yet"
        }
