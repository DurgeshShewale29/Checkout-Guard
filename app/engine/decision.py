import json
import os
from typing import Dict, Any, Tuple
from groq import Groq

# Load the taxonomy config
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "taxonomy.json")
with open(TAXONOMY_PATH, "r") as f:
    TAXONOMY = json.load(f)

def classify_error(error_payload: Dict[str, Any]) -> Tuple[str, float]:
    """
    Rule-based classifier that maps a raw error JSON to its taxonomy category.
    Extracts the 'reason' field from the standardized error schema.
    Returns (category, confidence_score). Rule-based matches get 1.0 confidence.
    Returns ('unknown', 0.0) if it doesn't match any known reason.
    """
    try:
        error_data = error_payload.get("error", {})
        reason = error_data.get("reason")
        
        if reason and reason in TAXONOMY:
            return reason, 1.0
            
    except Exception as e:
        pass
        
    # Fallback to LLM if unknown
    return classify_with_llm(error_payload)

def classify_with_llm(error_payload: Dict[str, Any]) -> Tuple[str, float]:
    """Uses an LLM to map ambiguous errors to the known taxonomy."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "unknown", 0.0
        
    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""
        You are an expert payments classification agent. Map the following raw error payload to one of our defined failure taxonomy categories.
        
        Taxonomy Categories: {list(TAXONOMY.keys())}
        
        Error Payload:
        {json.dumps(error_payload)}
        
        Output valid JSON exactly like this:
        {{"category": "matched_category_name", "confidence": 0.85}}
        
        If it does not match any category, use "unknown".
        """
        
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        text = response.choices[0].message.content
        # Clean markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()
            
        data = json.loads(text)
        category = data.get("category", "unknown")
        confidence = float(data.get("confidence", 0.0))
        
        if category not in TAXONOMY:
            category = "unknown"
            
        return category, confidence
        
    except Exception as e:
        print(f"LLM Classification failed: {e}")
        return "unknown", 0.0


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
