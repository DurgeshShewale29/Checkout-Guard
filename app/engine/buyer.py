import json
import os
from typing import Dict, Any, Tuple
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Load catalog
CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "catalog.json")
with open(CATALOG_PATH, "r") as f:
    CATALOG = json.load(f)

def select_product_for_intent(intent: str) -> Tuple[Dict[str, Any], str]:
    """
    Uses Gemini LLM to select the single best-matching product for a given intent.
    Returns a tuple of (selected_product_dict, reasoning_string).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in .env")
        
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an AI Buyer Agent. Your task is to select the single best product from our catalog that matches the user's intent.
    
    User Intent: "{intent}"
    
    Product Catalog:
    {json.dumps(CATALOG, indent=2)}
    
    Output valid JSON exactly like this:
    {{
        "product_id": "matched_product_id",
        "reasoning": "A short, one-line explanation of why this product fits the intent."
    }}
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
        
    try:
        data = json.loads(text)
        product_id = data.get("product_id")
        reasoning = data.get("reasoning", "No reasoning provided.")
        
        # Find product in catalog
        selected_product = next((p for p in CATALOG if p["id"] == product_id), None)
        
        if not selected_product:
            selected_product = CATALOG[0]
            reasoning = f"Fallback selected because LLM returned unknown ID '{product_id}'."
            
        return selected_product, reasoning
    except Exception as e:
        return CATALOG[0], f"Failed to parse LLM response: {e}"

if __name__ == "__main__":
    test_intent = "buy a birthday gift under ₹1000 for my sister"
    try:
        print(f"Intent: {test_intent}")
        product, reasoning = select_product_for_intent(test_intent)
        print(f"\nSelected Product: {product['name']} (₹{product['price_inr']})")
        print(f"Reasoning: {reasoning}")
    except Exception as e:
        print(f"Error: {e}")
