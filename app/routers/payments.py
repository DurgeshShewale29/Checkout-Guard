import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import razorpay
from typing import Optional
import datetime
from app.config import settings

router = APIRouter(prefix="/api/payments", tags=["payments"])

client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

class OrderRequest(BaseModel):
    amount: int  # in paise
    currency: str = "INR"
    receipt: Optional[str] = None

class VerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/orders")
async def create_order(req: OrderRequest):
    try:
        order = client.order.create({
            "amount": req.amount,
            "currency": req.currency,
            "receipt": req.receipt or f"receipt_{int(datetime.datetime.now().timestamp())}"
        })
        return {"status": "success", "order_id": order["id"], "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
async def verify_payment(req: VerifyRequest):
    try:
        # Verify the signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': req.razorpay_order_id,
            'razorpay_payment_id': req.razorpay_payment_id,
            'razorpay_signature': req.razorpay_signature
        })
        
        # In Phase 5 this will be saved to SQLite. For now, print/log it.
        print(f"✅ SUCCESSFUL TRANSACTION LOGGED:")
        print(f"   Order ID:   {req.razorpay_order_id}")
        print(f"   Payment ID: {req.razorpay_payment_id}")
        print(f"   Status:     Verified")
        print(f"   Timestamp:  {datetime.datetime.now().isoformat()}")
        
        return {"status": "verified", "payment_id": req.razorpay_payment_id}
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
