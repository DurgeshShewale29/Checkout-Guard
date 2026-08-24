import asyncio
import httpx
import json
from app.engine.agent import AgentRunner, BASE_URL
from app.db.audit import get_audit_trail

async def get_test_order() -> str:
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
        return res.json().get("order_id")

def print_audit_trail(order_id: str):
    print(f"\n📋 Audit Trail for {order_id}:")
    trail = get_audit_trail(order_id)
    for record in trail:
        print(f"  [{record['timestamp']}] Attempt {record['attempt_number']} | "
              f"FailType: {record['failure_type']} | "
              f"Action: {record['action_taken']} | "
              f"Outcome: {record['outcome']} | "
              f"Reason: {record['reasoning']}")
    print("-" * 60 + "\n")

async def test_audit_loop():
    print("🚀 CheckoutGuard Audit Logging Test\n")
    agent = AgentRunner()
    
    # --- Case 1: Recoverable Failure (Consent Missing -> Retry -> Success) ---
    print("--- Case 1: Recoverable Failure (MISSING_CONSENT) ---")
    order_id_1 = await get_test_order()
    await agent.execute_payment(order_id_1, initial_scenario="missing_consent")
    print_audit_trail(order_id_1)
    
    # --- Case 2: Unrecoverable Failure (Decline -> Instant Escalate) ---
    print("--- Case 2: Unrecoverable Failure (DECLINE) ---")
    order_id_2 = await get_test_order()
    await agent.execute_payment(order_id_2, initial_scenario="decline")
    print_audit_trail(order_id_2)
    
    # --- Case 3: Max Retries Failure (Persistent Timeout -> Escalate) ---
    print("--- Case 3: Max Retries Enforced (Persistent TIMEOUT) ---")
    order_id_3 = await get_test_order()
    await agent.execute_payment(order_id_3, initial_scenario="timeout", persistent_failure=True)
    print_audit_trail(order_id_3)

if __name__ == "__main__":
    asyncio.run(test_audit_loop())
