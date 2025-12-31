"""
LLM Analysis Service using Groq Cloud.
Provides AI-powered threat analysis and insights for security detections.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from groq import Groq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)



def _get_client():
    """
    Get or create Groq client instance with API key from environment.
    
    Returns:
        Groq: Initialized Groq client
        
    Raises:
        RuntimeError: If GROQ_API_KEY environment variable is not set
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set your Groq API key: export GROQ_API_KEY='your_api_key_here'"
        )
    return Groq(api_key=api_key)


def analyze_detection_results(
    detection_data: Dict,
    matched_rules: List[Dict],
    focus_areas: Optional[List[str]] = None
) -> Dict:
    """
    Analyze detection results using Groq LLM to provide threat intelligence.
    
    Args:
        detection_data: Dictionary containing detection results from sigma_pipeline
        matched_rules: List of matched rule objects with details
        focus_areas: Optional list of specific areas to focus on (e.g., ['severity', 'frequency', 'patterns'])
    
    Returns:
        Dictionary containing LLM analysis with threat insights and recommendations
    """
    
    try:
        # Prepare summary of detections for LLM
        summary = _prepare_detection_summary(detection_data, matched_rules)
        
        # Build system prompt
        system_prompt = """You are a cybersecurity threat analysis expert. Analyze the provided Windows security detection data and provide:
1. Key threat indicators and their significance
2. Attack patterns or TTPs (Tactics, Techniques, Procedures) detected
3. Risk assessment and severity evaluation
4. Recommended immediate actions
5. Long-term mitigation strategies

Be concise, technical, and actionable. Focus on what matters most for incident response."""
        
        # Build user prompt
        user_prompt = f"""Analyze the following security detections:

{summary}

Provide a comprehensive threat analysis with:
- Top 3 most concerning findings
- Patterns or correlations between detections
- Risk assessment (Critical/High/Medium/Low)
- Immediate actions to take
- Preventive measures"""
        
        logger.info(f"Calling Groq API with {len(summary)} character summary")
        
        # Call Groq API - using llama-3.3-70b-versatile (production model)
        client = _get_client()
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        logger.info("Groq API call successful")
        analysis_text = message.choices[0].message.content
        
        return {
            "status": "success",
            "analysis": analysis_text,
            "detection_summary": {
                "total_matches": detection_data.get("total_matches", 0),
                "unique_rules": len(detection_data.get("matched_rules", [])),
                "affected_systems": len(set(m.get("computer") for m in detection_data.get("matches", []))),
            }
        }
    
    except Exception as e:
        error_msg = f"LLM analysis failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error_message": error_msg,
            "analysis": None
        }


def analyze_specific_match(match_data: Dict) -> Dict:
    """
    Analyze a specific detection match for detailed threat context.
    
    Args:
        match_data: Single detection match from sigma_pipeline
    
    Returns:
        Dictionary containing detailed analysis for the match
    """
    
    try:
        system_prompt = "You are a cybersecurity analyst. Provide brief, technical analysis of security detection indicators."
        
        user_prompt = f"""Analyze this Windows security detection:

Rule: {match_data.get('rule_title', 'Unknown')}
Severity: {match_data.get('severity', 'Unknown')}
Event ID: {match_data.get('event_id', 'N/A')}
Computer: {match_data.get('computer', 'Unknown')}
Event Data: {json.dumps(match_data.get('event_data', {}), indent=2)}

Provide:
1. What attack does this indicate?
2. Why is it important?
3. What should be done about it?
Keep response to 3-4 sentences."""
        
        logger.info(f"Analyzing specific match for rule {match_data.get('rule_id')}")
        client = _get_client()
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=512,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        logger.info(f"Analysis complete for rule {match_data.get('rule_id')}")
        return {
            "status": "success",
            "analysis": message.choices[0].message.content,
            "match_id": match_data.get("rule_id")
        }
    
    except Exception as e:
        error_msg = f"Specific match analysis failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error_message": error_msg
        }


def _prepare_detection_summary(detection_data: Dict, matched_rules: List[Dict]) -> str:
    """
    Prepare a formatted summary of detections for LLM analysis.
    """
    
    matches = detection_data.get("matches", [])
    
    # Count by severity
    severity_counts = {}
    for match in matches:
        severity = match.get("severity", "unknown").lower()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Count by rule
    rule_counts = {}
    for match in matches:
        rule = match.get("rule_title", "Unknown")
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    # Get unique computers - exclude None and missing values
    computers = set()
    for match in matches:
        computer = match.get("computer")
        if computer and computer.strip():  # Check if computer exists and is not empty
            computers.add(computer)
    
    # Build summary text
    # Format systems list - show up to 5, indicate if more exist
    if computers:
        systems_display = ', '.join(sorted(list(computers))[:5])
        if len(computers) > 5:
            systems_display = systems_display + '...'
        systems_line = f"Affected Systems: {len(computers)} ({systems_display})"
    else:
        systems_line = "Affected Systems: 0 (No systems identified)"
    
    summary_lines = [
        f"Total Detections: {len(matches)}",
        f"Unique Rules Triggered: {len(matched_rules)}",
        systems_line,
        "",
        "Severity Distribution:",
    ]
    
    for severity in ["critical", "high", "medium", "low"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            summary_lines.append(f"  - {severity.upper()}: {count}")
    
    summary_lines.append("")
    summary_lines.append("Top Triggered Rules:")
    
    # Sort by frequency and show top 10
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for rule, count in top_rules:
        summary_lines.append(f"  - {rule}: {count} matches")
    
    return "\n".join(summary_lines)
