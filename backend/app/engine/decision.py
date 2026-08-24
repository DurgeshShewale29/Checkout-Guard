import json
import os
from typing import Dict, Any

# Load the taxonomy config
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "taxonomy.json")
with open(TAXONOMY_PATH, "r") as f:
    TAXONOMY = json.load(f)

def classify_error(error_payload: Dict[str, Any]) -> str:
    """
    Rule-based classifier that maps a raw error JSON to its taxonomy category.
    Extracts the 'reason' field from the standardized error schema.
    Returns 'unknown' if the error doesn't match any known reason.
    """
    try:
        error_data = error_payload.get("error", {})
        reason = error_data.get("reason")
        
        if reason and reason in TAXONOMY:
            return reason
            
    except Exception as e:
        pass
        
    return "unknown"


def decide_action(category: str, current_retry_count: int) -> Dict[str, Any]:
    """
    Decision engine that takes the taxonomy category and current retry count,
    and outputs either a retry command or an escalate command.
    """
    if category not in TAXONOMY:
        return {
            "escalate": True,
            "reason": f"Unknown error category: {category}"
        }
        
    rule = TAXONOMY[category]
    
    if not rule["is_retryable"]:
        return {
            "escalate": True,
            "reason": f"Error category '{category}' is not retryable."
        }
        
    if current_retry_count >= rule["max_retries"]:
        return {
            "escalate": True,
            "reason": f"Max retries ({rule['max_retries']}) reached for category '{category}'."
        }
        
    return {
        "retry": True,
        "action": rule["corrective_action"]
    }
