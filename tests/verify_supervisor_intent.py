
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.agents.supervisor_agent import classify_intent

def test_intent_classification():
    test_cases = [
        ("What is my cashflow forecast?", "credit"),
        ("Show me my future balance", "credit"),
        ("How long is my runway?", "credit"),
        ("What is my credit score?", "credit"),
        ("Who should I pay first?", "multi", "payment_priority"),
        ("Am I GST compliant?", "gst"),
    ]

    print("Running Supervisor Intent Classification Tests...")
    failed = False
    for query, expected_type, *expected_subtype in test_cases:
        result = classify_intent(query)
        
        # Check primary type/agent
        if expected_type in ["multi", "single"]:
             # This part of the test logic is a bit simplified, just checking if it hit the right bucket
             pass
        
        # Simplistic check: does the result point to the right agent or subtype?
        is_success = False
        if result["type"] == "single" and result["agent"] == expected_type:
             is_success = True
        elif result["type"] == "multi" and expected_subtype and result["subtype"] == expected_subtype[0]:
             is_success = True
        elif expected_type == "credit" and (
            (result["type"] == "single" and result["agent"] == "credit") or 
            (result["type"] == "multi" and "credit" in result.get("agents", []))
        ):
            # Credit queries might be single or multi depending on exact phrasing, 
            # but MUST include credit agent
            is_success = True

        status = "✅ PASS" if is_success else f"❌ FAIL (Got {result})"
        print(f"Query: '{query}' -> {status}")
        if not is_success:
            failed = True

    if failed:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    test_intent_classification()
