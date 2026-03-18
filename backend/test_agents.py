#!/usr/bin/env python3
"""
Test script for SmartFlow Multi-Agent System
Tests the core agents (Collections and Payments) with Groq LLM
"""

import asyncio
import os
from app.agents.supervisor_agent import run_supervisor

async def test_multi_agent_system():
    """Test the multi-agent system with sample queries."""

    # Test entity ID (you may need to update this based on your database)
    test_entity_id = "test-entity-001"

    print("🤖 Testing SmartFlow Multi-Agent System with Groq LLM")
    print("=" * 60)

    # Test queries that should trigger different agent combinations
    test_queries = [
        "Who should I pay first?",
        "How is my business doing?",
        "What are my biggest risks?",
        "Am I safe to pay all vendors?"
    ]

    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 40)

        try:
            result = await run_supervisor(test_entity_id, query)
            print(f"✅ Agent used: {result.get('agent_used', 'Unknown')}")
            print(f"📝 Intent: {result.get('intent', 'Unknown')}")
            print(f"📄 Response preview: {result.get('output', 'No output')[:200]}...")
            print("✅ Query processed successfully")

        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")

        print()

if __name__ == "__main__":
    # Set test environment
    os.environ["GROQ_API_KEY"] = "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"

    asyncio.run(test_multi_agent_system())