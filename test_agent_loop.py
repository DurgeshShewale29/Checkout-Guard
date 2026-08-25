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
    print("\n--- Case 3: Max Retries Enforced (Persistent TIMEOUT) ---")
    order_id_3 = await get_test_order()
    res_3 = await agent.execute_payment(order_id_3, "timeout", persistent_failure=True)
    print("Final Agent Result:", res_3)
    
    print("\n--- Case 4: LLM Fallback (Ambiguous Error) ---")
    order_id_4 = await get_test_order()
    res_4 = await agent.execute_payment(order_id_4, "ambiguous", persistent_failure=True)
    print("Final Agent Result:", res_4)
    
    print("\n--- Case 5: Rate Limiter Enforced ---")
    # Using the same order_id_4 to trigger rate limits since we already failed a few times
    # and rate limit is global per order. Wait, rate limit is 5 attempts. We can just loop it.
    order_id_5 = await get_test_order()
    for i in range(6):
        res_5 = await agent.execute_payment(order_id_5, "decline")
    print("Final Agent Result after 6 attempts:", res_5)

if __name__ == "__main__":
    asyncio.run(test_agent_loop())
