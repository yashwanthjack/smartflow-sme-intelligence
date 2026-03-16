import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.llm import get_llm

def test_llm():
    print("🧪 Testing LLM Integration...")
    try:
        llm = get_llm()
        print(f"✅ LLM Initialized: {llm}")
        
        print("📤 Sending test prompt...")
        response = llm.invoke("Hello, are you Llama 3.1? concisely answer yes or no.")
        print(f"📥 Response: {response}")
        print("✅ Integration Successful!")
    except Exception as e:
        print(f"❌ LLM Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm()
