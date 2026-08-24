import httpx
import asyncio
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_failure_scenario(scenario: str):
    print(f"\n--- Testing Scenario: {scenario.upper()} ---")
    
    # In a real environment, the Agent creates an order first
    async with httpx.AsyncClient() as client:
        # Create a mock order just for the test
        order_res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
        if order_res.status_code != 200:
            print("Failed to create order. Is the server running?")
            return
            
        order_id = order_res.json().get("order_id")
        
        # Now hit the simulation endpoint
        print(f"Triggering /api/simulate/pay with scenario='{scenario}'...")
        res = await client.post(
            f"{BASE_URL}/api/simulate/pay",
            json={"order_id": order_id, "scenario": scenario}
        )
        
        print("\nResponse:")
        print(json.dumps(res.json(), indent=2))

async def main():
    print("🚀 CheckoutGuard Failure Simulator")
    print("Testing the 4 failure types for the AI Buyer Agent...\n")
    
    scenarios = ["decline", "timeout", "missing_consent", "expired_token"]
    
    for s in scenarios:
        await test_failure_scenario(s)
        await asyncio.sleep(1) # Small pause between tests
        
    print("\n✅ All simulated failures triggered successfully.")

if __name__ == "__main__":
    asyncio.run(main())
