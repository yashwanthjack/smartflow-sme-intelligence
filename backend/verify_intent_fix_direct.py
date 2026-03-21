import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append(os.path.abspath("."))

from app.agents.supervisor_agent import run_supervisor

async def test():
    entity_id = "93307096-1e07-4110-b1b6-819413de90ab"
    queries = [
        "whats the highest payment done?",
        "who gave me the highest income?"
    ]

    for query in queries:
        print(f"\nTesting Query: '{query}'")
        try:
            result = await run_supervisor(entity_id, query)
            print(f"Agent Used: {result.get('agent_used')}")
            print(f"Intent Subtype: {result.get('intent')}")
            print(f"Output: {result.get('output')}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
