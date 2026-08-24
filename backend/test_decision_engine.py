from app.engine.decision import classify_error, decide_action
import json

def test_engine():
    print("🚀 CheckoutGuard Rule-Based Decision Engine Test\n")
    
    # --- Case 1: Timeout (Retry Case) ---
    print("--- Case 1: Testing GATEWAY_TIMEOUT (Retryable) ---")
    mock_timeout_payload = {
      "error": {
        "code": "GATEWAY_TIMEOUT",
        "description": "The upstream gateway took too long to respond.",
        "source": "bank",
        "step": "payment_authorization",
        "reason": "timeout"
      }
    }
    
    # 1. Classify
    category = classify_error(mock_timeout_payload)
    print(f"1. Classified as: '{category}'")
    
    # 2. Decide Action (0 retries so far)
    decision = decide_action(category, current_retry_count=0)
    print(f"2. Decision (0 retries): {json.dumps(decision)}")
    
    # 3. Simulate it failing again (1 retry so far)
    print("... simulating failure again ...")
    decision2 = decide_action(category, current_retry_count=1)
    print(f"3. Decision (1 retry): {json.dumps(decision2)}\n")


    # --- Case 2: Decline (Escalate Case) ---
    print("--- Case 2: Testing DECLINE (Not Retryable) ---")
    mock_decline_payload = {
      "error": {
        "code": "BAD_REQUEST_ERROR",
        "description": "Your payment has been declined by the bank.",
        "source": "bank",
        "step": "payment_authorization",
        "reason": "payment_failed"
      }
    }
    
    # 1. Classify
    category = classify_error(mock_decline_payload)
    print(f"1. Classified as: '{category}'")
    
    # 2. Decide Action
    decision = decide_action(category, current_retry_count=0)
    print(f"2. Decision (0 retries): {json.dumps(decision)}\n")
    
    
    # --- Case 3: Missing Consent (Successful Retry Case) ---
    print("--- Case 3: Testing MISSING_CONSENT (Successful Retry Path) ---")
    mock_consent_payload = {
      "error": {
        "code": "BAD_REQUEST_ERROR",
        "description": "Customer consent required for this payment method.",
        "source": "customer",
        "step": "payment_authentication",
        "reason": "consent_missing"
      }
    }
    
    category = classify_error(mock_consent_payload)
    print(f"1. Classified as: '{category}'")
    decision = decide_action(category, current_retry_count=0)
    print(f"2. Decision (0 retries): {json.dumps(decision)}")
    print(f"3. Simulating Agent Action: {decision.get('action')}")
    print("4. Result: SUCCESS! (Payment went through after re-requesting consent)\n")


    # --- Case 4: Expired Token (Successful Retry Case) ---
    print("--- Case 4: Testing EXPIRED_TOKEN (Successful Retry Path) ---")
    mock_token_payload = {
      "error": {
        "code": "BAD_REQUEST_ERROR",
        "description": "The provided token or session has expired.",
        "source": "business",
        "step": "payment_initiation",
        "reason": "token_expired"
      }
    }
    
    category = classify_error(mock_token_payload)
    print(f"1. Classified as: '{category}'")
    decision = decide_action(category, current_retry_count=1) # Let's say it failed once already
    print(f"2. Decision (1 retry): {json.dumps(decision)}")
    print(f"3. Simulating Agent Action: {decision.get('action')}")
    print("4. Result: SUCCESS! (Payment went through after refreshing token)\n")


    # --- Case 5: Unknown Error (Failsafe Case) ---
    print("--- Case 5: Testing UNKNOWN ERROR (Failsafe) ---")
    mock_unknown_payload = {
      "error": {
        "code": "WEIRD_ERROR",
        "description": "Something completely unexpected happened.",
        "reason": "some_undocumented_reason"
      }
    }
    
    category = classify_error(mock_unknown_payload)
    print(f"1. Classified as: '{category}'")
    decision = decide_action(category, current_retry_count=0)
    print(f"2. Decision (0 retries): {json.dumps(decision)}\n")


if __name__ == "__main__":
    test_engine()
