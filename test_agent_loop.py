import asyncio
import httpx
from app.engine.agent import AgentRunner, BASE_URL

async def get_test_order() -> str:
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
        return res.json().get("order_id")

async def test_agent_loop():
    print("🚀 CheckoutGuard Autonomous Agent Loop Test\n")
    agent = AgentRunner()
    
    # --- Case 1: Recoverable Failure (Consent Missing -> Retry -> Success) ---
    print("--- Case 1: Recoverable Failure (MISSING_CONSENT) ---")
    order_id_1 = await get_test_order()
    res = await agent.execute_payment(order_id_1, initial_scenario="missing_consent")
    print(f"Final Agent Result: {res}\n")
    
    # --- Case 2: Unrecoverable Failure (Decline -> Instant Escalate) ---
    print("--- Case 2: Unrecoverable Failure (DECLINE) ---")
    order_id_2 = await get_test_order()
    res = await agent.execute_payment(order_id_2, initial_scenario="decline")
    print(f"Final Agent Result: {res}\n")
    
    # --- Case 3: Max Retries Failure (Persistent Timeout -> Escalate) ---
    print("--- Case 3: Max Retries Enforced (Persistent TIMEOUT) ---")
    order_id_3 = await get_test_order()
    res = await agent.execute_payment(order_id_3, initial_scenario="timeout", persistent_failure=True)
    print(f"Final Agent Result: {res}\n")

if __name__ == "__main__":
    asyncio.run(test_agent_loop())
