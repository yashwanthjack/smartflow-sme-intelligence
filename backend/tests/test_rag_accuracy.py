import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import SessionLocal
from app.models.ledger_entry import LedgerEntry
from sqlalchemy import func
from app.agents.langgraph_supervisor import run_langgraph_supervisor
from app.agents.tools import set_db_session

async def verify_accuracy():
    db = SessionLocal()
    set_db_session(db)
    
    entity_id = "cb8263ab-2463-4468-a16a-e340c006ccd6" # Judge Entity
    
    # 1. Get ground truth from DB
    highest_record = (
        db.query(LedgerEntry)
        .filter(LedgerEntry.entity_id == entity_id)
        .order_by(func.abs(LedgerEntry.amount).desc())
        .first()
    )
    
    if not highest_record:
        print("❌ No data found in DB for this entity.")
        return

    ground_truth_amt = abs(highest_record.amount)
    ground_truth_desc = highest_record.description
    
    print(f"✅ Ground Truth (DB): ₹{ground_truth_amt:,.0f} | {ground_truth_desc}")

    # 2. Query the Agent
    query = "whats the highest transaction done?"
    print(f"🤖 Querying Agent: '{query}'...")
    
    result = await run_langgraph_supervisor(entity_id, query)
    
    agent_output = result["output"]
    print(f"📄 Agent Output: {agent_output}")
    
    # 3. Validation
    amt_str = f"{ground_truth_amt:,.0f}".replace(",", "") # Simple check
    if amt_str in agent_output.replace(",", ""):
        print("🌟 SUCCESS: Agent correctly identified the highest transaction from DB!")
    else:
        print("❌ FAILURE: Agent output does not match database ground truth.")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(verify_accuracy())
