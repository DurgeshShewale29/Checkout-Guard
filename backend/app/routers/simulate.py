from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import time

router = APIRouter(prefix="/api/simulate", tags=["simulation"])

class SimulatePaymentRequest(BaseModel):
    order_id: str
    scenario: Optional[str] = "success"  # success, decline, timeout, missing_consent, expired_token

@router.post("/pay")
async def simulate_payment(req: SimulatePaymentRequest):
    """
    Simulates a payment attempt. In a real environment, the AI Agent would interact 
    with the Razorpay UI or the S2S API. Here, we mock the responses to cleanly test 
    failure recovery logic.
    """
    
    # 1. Simulate Timeout
    if req.scenario == "timeout":
        # We can either sleep to literally timeout, or immediately return a 504 representation.
        # Returning a 504 equivalent payload is better for automated testing without hanging.
        await asyncio.sleep(1) # Small delay for realism
        return {
            "error": {
                "code": "GATEWAY_TIMEOUT",
                "description": "The upstream gateway took too long to respond.",
                "source": "bank",
                "step": "payment_authorization",
                "reason": "timeout"
            }
        }
        
    # 2. Simulate Decline (Hard/Soft)
    if req.scenario == "decline":
        return {
            "error": {
                "code": "BAD_REQUEST_ERROR",
                "description": "Your payment has been declined by the bank. Please try again or use a different method.",
                "source": "bank",
                "step": "payment_authorization",
                "reason": "payment_failed"
            }
        }
        
    # 3. Simulate Missing Consent
    if req.scenario == "missing_consent":
        return {
            "error": {
                "code": "BAD_REQUEST_ERROR",
                "description": "Customer consent required for this payment method.",
                "source": "customer",
                "step": "payment_authentication",
                "reason": "consent_missing"
            }
        }
        
    # 4. Simulate Expired Token
    if req.scenario == "expired_token":
        return {
            "error": {
                "code": "BAD_REQUEST_ERROR",
                "description": "The provided token or session has expired.",
                "source": "business",
                "step": "payment_initiation",
                "reason": "token_expired"
            }
        }
        
    # 5. Success (Happy Path)
    # Generate a fake razorpay payment ID and a mock signature for the agent to verify
    return {
        "status": "success",
        "razorpay_payment_id": f"pay_sim_{int(time.time())}",
        "razorpay_order_id": req.order_id,
        "razorpay_signature": "simulated_signature_12345"
    }
