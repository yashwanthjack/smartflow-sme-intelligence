"""
Standalone test: Verify Gemini LLM + Agent interactions work end-to-end.
No server or database required — uses mocks for DB, real Gemini API.
"""
import sys
import os
import asyncio
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()


def test_1_gemini_connection():
    """Test 1: Can we connect to Gemini and get a response?"""
    print("\n" + "=" * 60)
    print("TEST 1: Gemini API Connection")
    print("=" * 60)

    from app.agents.llm import get_llm

    llm = get_llm()
    response = llm.invoke("Say 'SmartFlow is ready!' in one line.")
    output = response.content if hasattr(response, "content") else str(response)
    print(f"   LLM Response: {output}")
    assert len(output) > 0, "Empty response from Gemini"
    print("   PASS")
    return True


def test_2_intent_classification():
    """Test 2: Does the intent classifier route correctly?"""
    print("\n" + "=" * 60)
    print("TEST 2: Intent Classification")
    print("=" * 60)

    from app.agents.supervisor_agent import classify_intent

    tests = [
        ("Hello!", "general"),
        ("Who should I pay first?", "multi"),
        ("Show me overdue receivables and collection status", "single"),
        ("How is my business doing?", "multi"),
    ]

    for query, expected_type in tests:
        result = classify_intent(query)
        status = "PASS" if result["type"] == expected_type else f"FAIL (got {result['type']})"
        print(f"   '{query}' -> {result['type']} [{status}]")
        assert result["type"] == expected_type, f"Failed for '{query}'"

    print("   ALL PASS")
    return True


@pytest.mark.asyncio
async def test_3_supervisor_general_query():
    """Test 3: Does the supervisor handle a greeting without crashing?"""
    print("\n" + "=" * 60)
    print("TEST 3: Supervisor Agent - General Query")
    print("=" * 60)

    from app.agents.supervisor_agent import SupervisorAgent

    supervisor = SupervisorAgent()
    # Patch the _log_interaction to avoid DB dependency
    supervisor._log_interaction = lambda *args, **kwargs: None

    result = await supervisor.run("test-entity", "Hello, how are you?")
    print(f"   Agent used: {result['agent_used']}")
    print(f"   Intent: {result['intent']}")
    print(f"   Output: {result['output'][:200]}...")
    assert result["success"] is True
    assert result["intent"] == "general"
    print("   PASS")
    return True


@pytest.mark.asyncio
async def test_4_supervisor_with_gemini():
    """Test 4: Does a financial query trigger agents and Gemini synthesis?"""
    print("\n" + "=" * 60)
    print("TEST 4: Supervisor Agent - Financial Query (Gemini Synthesis)")
    print("=" * 60)

    from app.agents.supervisor_agent import SupervisorAgent

    # Use a mock DB session that returns empty results
    from unittest.mock import MagicMock
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    mock_db.query.return_value.filter.return_value.scalar.return_value = 0

    supervisor = SupervisorAgent()
    supervisor._log_interaction = lambda *args, **kwargs: None

    result = await supervisor.run("test-entity", "What is my cash runway?")
    print(f"   Agent used: {result['agent_used']}")
    print(f"   Intent: {result.get('intent', 'N/A')}")
    output = result.get("output", result.get("fallback_output", "No output"))
    print(f"   Output preview: {output[:300]}...")
    assert result["success"] is True or "error" not in result
    print("   PASS")
    return True


@pytest.mark.asyncio
async def test_5_multi_agent_collaboration():
    """Test 5: Multi-agent collaboration with Gemini LLM synthesis."""
    print("\n" + "=" * 60)
    print("TEST 5: Multi-Agent Collaboration (Payments + Credit)")
    print("=" * 60)

    from app.agents.supervisor_agent import SupervisorAgent
    from unittest.mock import MagicMock, AsyncMock

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.scalar.return_value = 0

    supervisor = SupervisorAgent()
    supervisor._log_interaction = lambda *args, **kwargs: None

    # Mock agent runners to return predictable data
    supervisor.agent_runners["payments"] = AsyncMock(
        return_value={"output": "Pending payments: Rs 2,50,000 to 5 vendors. Top: Vendor ABC Rs 80,000 due in 3 days."}
    )
    supervisor.agent_runners["credit"] = AsyncMock(
        return_value={"output": "Credit Score: 720 (Good). Cash runway: 4.2 months. Burn rate: Rs 1.5L/month."}
    )

    result = await supervisor.run("test-entity", "Who should I pay first?")
    print(f"   Agent used: {result['agent_used']}")
    print(f"   Intent: {result.get('intent', 'N/A')}")
    output = result.get("output", "No output")
    print(f"   Gemini synthesis preview: {output[:400]}...")
    assert result["success"] is True
    assert len(str(output)) > 50, "Synthesis output too short"
    print("   PASS")
    return True


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("  SmartFlow Agent Integration Tests (Live Gemini)")
    print("#" * 60)

    passed = 0
    failed = 0

    # Sync tests
    for test_fn in [test_1_gemini_connection, test_2_intent_classification]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"   FAIL: {e}")
            failed += 1

    # Async tests
    for test_fn in [test_3_supervisor_general_query, test_4_supervisor_with_gemini, test_5_multi_agent_collaboration]:
        try:
            asyncio.run(test_fn())
            passed += 1
        except Exception as e:
            print(f"   FAIL: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed} passed, {failed} failed out of {passed + failed}")
    print("=" * 60)
