import os
import httpx
import asyncio
from dotenv import load_dotenv
import urllib.parse

load_dotenv()
key_id = os.getenv('RAZORPAY_KEY_ID')
BASE_URL = "http://127.0.0.1:8000"

async def main():
    print("1️⃣ Calling CheckoutGuard API to create order...")
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
        if res.status_code != 200:
            print("Failed to create order:", res.text)
            return
            
        order_data = res.json()
        order_id = order_data["order_id"]
        print(f"✅ Order created successfully: {order_id}")
        
        cwd = os.getcwd().replace("\\", "/")
        html_path = f"file:///{cwd}/checkout_test.html"
        query_params = urllib.parse.urlencode({
            'key_id': key_id,
            'order_id': order_id,
            'amount': 1000
        })
        
        full_url = f"{html_path}?{query_params}"
        print("\n2️⃣ To test the payment end-to-end, open this URL in your browser:")
        print(f"\n{full_url}\n")
        print("3️⃣ Use the test card: 4100 2800 0000 1007")
        print("4️⃣ Watch the terminal where the FastAPI server is running to see the transaction logged!")

if __name__ == "__main__":
    asyncio.run(main())
