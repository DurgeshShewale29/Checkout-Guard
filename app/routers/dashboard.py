import httpx
from fastapi import APIRouter
from app.db.audit import get_all_transactions, get_audit_trail
from app.engine.agent import AgentRunner, BASE_URL

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
agent = AgentRunner()

@router.get("/transactions")
def list_transactions():
    return get_all_transactions()

@router.get("/transactions/{transaction_id}")
def transaction_detail(transaction_id: str):
    return get_audit_trail(transaction_id)

@router.post("/trigger")
async def trigger_demo(scenario: str):
    """
    Triggers a demo run by creating an order and running the agent loop against it.
    """
    # 1. Create a dummy order
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
            
            if res.status_code != 200:
                return {"status": "error", "reason": f"Failed to create dummy order: {res.text}"}
                
            order_id = res.json().get("order_id")
            if not order_id:
                return {"status": "error", "reason": "Order ID missing from payment response"}
                
    except httpx.RequestError as e:
        return {"status": "error", "reason": f"HTTP Request failed for dummy order. Ensure BASE_URL ({BASE_URL}) is reachable: {str(e)}"}
        
    # 2. Run the agent against it
    # We pass persistent_failure=True only if we want to show the max-retry timeout escalation
    is_persistent = (scenario == "timeout")
    await agent.execute_payment(order_id, initial_scenario=scenario, persistent_failure=is_persistent)
    
    return {"status": "triggered", "order_id": order_id}
