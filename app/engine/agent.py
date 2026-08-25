import httpx
from typing import Dict, Any, Optional
from app.engine.decision import classify_error, decide_action
from app.db.audit import log_attempt
from app.engine.rate_limit import check_rate_limit

import os
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://127.0.0.1:{PORT}"

class AgentRunner:
    """
    The AI Buyer Agent Execution Loop.
    Wraps the payment API call with autonomous classification and retry logic.
    """
    
    def __init__(self):
        pass
        
    async def execute_payment(self, order_id: str, initial_scenario: str, persistent_failure: bool = False) -> Dict[str, Any]:
        """
        Attempts a payment. If it fails, uses the decision engine to retry or escalate.
        `persistent_failure` flag is used for testing max-retry limits (keeps failing).
        """
        
        current_retry_count = 0
        current_scenario = initial_scenario
        last_action = "initial_attempt"
        
        async with httpx.AsyncClient() as client:
            while True:
                if check_rate_limit(order_id):
                    print(f"  [Agent]  ESCALATING: Rate limit exceeded for order '{order_id}'.")
                    log_attempt(order_id, current_retry_count, "rate_limited", "escalate", "escalated", "Max attempts reached for this order.", 1.0)
                    return {"status": "escalated", "reason": "Rate limit exceeded. Too many attempts."}
                    
                print(f"  [Agent]  Attempting payment for order '{order_id}' (scenario='{current_scenario}', retry={current_retry_count})...")
                
                # 1. Execute the API Call
                res = await client.post(
                    f"{BASE_URL}/api/simulate/pay",
                    json={"order_id": order_id, "scenario": current_scenario}
                )
                
                if res.status_code != 200:
                    log_attempt(order_id, current_retry_count, "http_error", "escalate", "escalated", f"HTTP {res.status_code}", 1.0)
                    return {"status": "escalated", "reason": f"HTTP {res.status_code} Error"}
                    
                payload = res.json()
                
                # 2. Evaluate Success
                if "error" not in payload:
                    print(f"  [Agent]  Payment SUCCESS on attempt {current_retry_count + 1}!")
                    log_attempt(order_id, current_retry_count, None, last_action, "success", "Payment succeeded", 1.0)
                    return {"status": "success", "data": payload}
                    
                # 3. Classify Failure
                category, conf = classify_error(payload)
                print(f"  [Agent]  API returned error. Classified as: '{category}' (Confidence: {conf*100:.1f}%)")
                
                # 4. Decide Action
                decision = decide_action(category, current_retry_count)
                
                # 5. Act (Escalate)
                if decision.get("escalate"):
                    print(f"  [Agent]  ESCALATING: {decision.get('reason')}")
                    log_attempt(order_id, current_retry_count, category, "escalate", "escalated", decision.get('reason'), conf)
                    return {"status": "escalated", "reason": decision.get("reason")}
                    
                # 6. Act (Retry)
                action_to_take = decision.get("action")
                print(f"  [Agent] RETRYING: Action to take -> '{action_to_take}'")
                log_attempt(order_id, current_retry_count, category, action_to_take, "failed", f"Will retry (attempt {current_retry_count+1})", conf)
                current_retry_count += 1
                last_action = action_to_take
                
                if not persistent_failure:
                    if category == "consent_missing":
                        print("  [Agent] [CORRECTION] Applying REAL correction... (creating real Razorpay Payment Link for re-consent)")
                        try:
                            import os
                            from dotenv import load_dotenv
                            load_dotenv()
                            key = os.getenv("RAZORPAY_KEY_ID")
                            secret = os.getenv("RAZORPAY_KEY_SECRET")
                            
                            # Make a genuine, distinguishable API call to Payment Links
                            real_res = await client.post(
                                "https://api.razorpay.com/v1/payment_links",
                                auth=(key, secret),
                                json={
                                    "amount": 1000,
                                    "currency": "INR",
                                    "description": f"Re-consent for Order {order_id}",
                                    "customer": {
                                        "name": "AI Buyer",
                                        "email": "buyer@agent.com",
                                        "contact": "9876543210"
                                    },
                                    "notify": {"sms": False, "email": False}
                                }
                            )
                            
                            print(f"  [Agent] [REAL CALL] Razorpay Payment Link Response: HTTP {real_res.status_code}")
                            
                            if real_res.status_code in [200, 201]:
                                pl_data = real_res.json()
                                log_attempt(order_id, current_retry_count, category, action_to_take, "success", f"Real API Success: Created Payment Link {pl_data.get('id')}", conf)
                                return {"status": "success", "data": pl_data}
                            else:
                                err_msg = real_res.json().get("error", {}).get("description", "Unknown error")
                                log_attempt(order_id, current_retry_count, category, action_to_take, "failed", f"Real API Rejection: {err_msg}", conf)
                                return {"status": "escalated", "reason": f"Real API Rejection: {err_msg}"}
                                
                        except Exception as e:
                            log_attempt(order_id, current_retry_count, category, action_to_take, "failed", f"Exception: {str(e)}", conf)
                            return {"status": "escalated", "reason": str(e)}
                    else:
                        print("  [Agent] [CORRECTION] Applying correction... (setting scenario='success')")
                        current_scenario = "success"
                else:
                    print("  [Agent] [CORRECTION] Applying correction... (but failure is persistent for this test)")
