import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

def test_gst_agent():
    print("Initializing GST Agent...")
    try:
        from app.agents.gst_agent import GSTAgent
        agent = GSTAgent(entity_id="test-entity")
        
        print("\nRunning GST Check Task...")
        result = agent.run("Review my GST ITC data")
        
        print("\n--- FINAL AGENT OUTPUT ---")
        print(result.get("output"))
        print("--------------------------")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gst_agent()
