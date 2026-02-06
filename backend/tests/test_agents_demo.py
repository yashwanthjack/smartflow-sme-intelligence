# Test script for SmartFlow Agents
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def test_collections_agent():
    """Test the Collections Agent."""
    print("\n" + "="*60)
    print("🔍 Testing Collections Agent")
    print("="*60)
    
    from app.agents.collections_agent import run_collections_agent
    
    result = run_collections_agent("test-entity-001")
    print("\n📋 Result:")
    print(result.get("output", result))
    return result

def test_payments_agent():
    """Test the Payments Agent."""
    print("\n" + "="*60)
    print("💰 Testing Payments Agent")
    print("="*60)
    
    from app.agents.payments_agent import run_payments_agent
    
    result = run_payments_agent("test-entity-001")
    print("\n📋 Result:")
    print(result.get("output", result))
    return result

def test_gst_agent():
    """Test the GST Agent."""
    print("\n" + "="*60)
    print("📊 Testing GST Agent")
    print("="*60)
    
    from app.agents.gst_agent import run_gst_agent
    
    result = run_gst_agent("test-entity-001")
    print("\n📋 Result:")
    print(result.get("output", result))
    return result

def test_credit_advisory_agent():
    """Test the Credit Advisory Agent."""
    print("\n" + "="*60)
    print("💡 Testing Credit Advisory Agent")
    print("="*60)
    
    from app.agents.credit_advisory_agent import run_credit_advisory_agent
    
    result = run_credit_advisory_agent("test-entity-001")
    print("\n📋 Result:")
    print(result.get("output", result))
    return result

def test_llm_connection():
    """Test basic LLM connection."""
    print("\n" + "="*60)
    print("🔌 Testing LLM Connection")
    print("="*60)
    
    from app.agents.llm import get_llm
    
    llm = get_llm()
    response = llm.invoke("Say 'SmartFlow is ready!' in one line.")
    print(f"LLM Response: {response.content}")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SmartFlow Agents")
    parser.add_argument("--agent", type=str, choices=["collections", "payments", "gst", "credit", "llm", "all"],
                        default="llm", help="Which agent to test")
    
    args = parser.parse_args()
    
    print("\n🚀 SmartFlow Agent Test Suite")
    print("="*60)
    
    if args.agent == "llm" or args.agent == "all":
        test_llm_connection()
    
    if args.agent == "collections" or args.agent == "all":
        test_collections_agent()
    
    if args.agent == "payments" or args.agent == "all":
        test_payments_agent()
    
    if args.agent == "gst" or args.agent == "all":
        test_gst_agent()
    
    if args.agent == "credit" or args.agent == "all":
        test_credit_advisory_agent()
    
    print("\n✅ Test complete!")
