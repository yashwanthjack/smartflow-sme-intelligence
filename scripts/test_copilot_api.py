import httpx
import asyncio
import sys

async def test_copilot():
    print("Sending request to Copilot...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/agents/query/test-entity",
                json={"query": "Who should I pay first?"},
                timeout=60.0
            )
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_copilot())
