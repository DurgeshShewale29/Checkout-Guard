import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=None) as client:
        res = await client.post("http://127.0.0.1:8000/api/dashboard/trigger_ai_buyer", json={"intent": "buy a birthday gift for my sister", "scenario": "missing_consent"})
        print(res.status_code)
        print(res.json())
        
asyncio.run(test())
