import os
import asyncio
import httpx
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
key_id = os.getenv('RAZORPAY_KEY_ID')
BASE_URL = "http://127.0.0.1:8000"

async def run():
    print("🤖 AI Buyer Agent starting simulation...")
    
    async with httpx.AsyncClient() as client:
        print("1️⃣ Creating Order via CheckoutGuard API...")
        res = await client.post(f"{BASE_URL}/api/payments/orders", json={"amount": 1000})
        if res.status_code != 200:
            print("Failed to create order:", res.text)
            return
            
        order_data = res.json()
        order_id = order_data["order_id"]
        print(f"✅ Order created: {order_id}")
        
        print("2️⃣ Opening Checkout UI (Headless) to attempt payment...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Load the local HTML file to trigger Razorpay checkout
            cwd = os.getcwd()
            html_path = f"file:///{cwd}/checkout_test.html?key_id={key_id}&order_id={order_id}&amount=1000"
            html_path = html_path.replace("\\", "/")
            
            await page.goto(html_path)
            await page.click("button#rzp-button1")
            
            # Wait for Razorpay iframe
            print("3️⃣ Filling test card details (4111 1111 1111 1111)...")
            await page.wait_for_selector("iframe.razorpay-checkout-frame")
            frame = page.frame_locator("iframe.razorpay-checkout-frame")
            
            # Note: Razorpay test checkout sometimes updates its DOM. This is a common test flow:
            # Click "Pay with Card" or sometimes just fill if it's open.
            
            # Wait for contact input just to ensure it's loaded
            await frame.locator("#contact").wait_for(state="visible", timeout=10000)
            
            # We don't necessarily have to fill contact if prefilled, but let's click 'Proceed' if there is one
            proceed_btn = frame.locator("button#redesign-v15-cta")
            if await proceed_btn.is_visible():
                await proceed_btn.click()
            
            # In test mode, clicking 'Success' directly via Razorpay mock UI might be possible,
            # or we might need to fill the card.
            # Actually, Razorpay has a "Test Bank" and "Test Cards" UI in test mode!
            # It usually asks "Select Bank" or "Card".
            # Let's wait for the "Card" method and click it
            try:
                card_btn = frame.locator("button[method='card']")
                await card_btn.wait_for(state="visible", timeout=5000)
                await card_btn.click()
                
                # Fill card details
                await frame.locator("#card_number").fill("4111111111111111")
                await frame.locator("#card_expiry").fill("12/26")
                await frame.locator("#card_name").fill("Test User")
                await frame.locator("#card_cvv").fill("123")
                
                # Click Pay
                await frame.locator("#footer-cta").click()
                
                # Test mode often shows a "Success / Failure" simulation screen.
                success_btn = frame.locator("button.success")
                await success_btn.wait_for(state="visible", timeout=5000)
                await success_btn.click()
                
            except Exception as e:
                # If the UI flow is slightly different, we might just look for the success button directly
                print("Could not fill card, trying to click success simulation directly...", e)
                try:
                    # Sometimes in test mode, clicking "Netbanking" -> "Success" is faster
                    await frame.locator("button[method='netbanking']").click()
                    await frame.locator("label[for='bank-radio-HDFC']").click()
                    await frame.locator("#footer-cta").click()
                    success_btn = frame.locator("button.success")
                    await success_btn.wait_for(state="visible", timeout=5000)
                    await success_btn.click()
                except Exception as e2:
                    print("Failed UI automation:", e2)
                    await browser.close()
                    return

            print("4️⃣ Waiting for Payment response...")
            # We put the status in our div
            await page.wait_for_function("document.getElementById('status').innerText !== ''", timeout=15000)
            status_text = await page.evaluate("document.getElementById('status').innerText")
            await browser.close()
            
            if status_text.startswith("SUCCESS:"):
                _, pay_id, ord_id, sig = status_text.split(":")
                print(f"✅ Payment captured! Razorpay Payment ID: {pay_id}")
                
                print("5️⃣ Verifying payment with CheckoutGuard API...")
                v_res = await client.post(f"{BASE_URL}/api/payments/verify", json={
                    "razorpay_order_id": ord_id,
                    "razorpay_payment_id": pay_id,
                    "razorpay_signature": sig
                })
                
                if v_res.status_code == 200:
                    print("🎉 Verification Successful! Payment Logged.")
                else:
                    print("❌ Verification Failed:", v_res.text)
            else:
                print("❌ Payment Failed in UI:", status_text)

if __name__ == "__main__":
    asyncio.run(run())
