
import sys
import os
from datetime import date

# Add backend to path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.agents.tools import (
    get_pending_payables,
    get_overdue_invoices,
    check_gst_compliance,
    analyze_ledger_spending,
    set_db_session
)
from app.db.database import SessionLocal

def test_tools():
    print("Starting Tool Verification...")
    db = SessionLocal()
    set_db_session(db)
    
    entity_id = "test-entity" 
    # In the actual app, the entity_id is likely different. 
    # Let's try to query a real entity ID if possible, or use the one from previous context if known.
    # The user mentioned "yashadmin@gmail.com". Let's try to find their entity_id first.
    
    try:
        from app.models.user import User
        user = db.query(User).filter(User.email == "yashadmin@gmail.com").first()
        if user and user.entity_id:
            entity_id = user.entity_id
            print(f"Found Real Entity ID: {entity_id}")
        else:
            print("User not found, using 'test-entity'")
    except Exception as e:
        print(f"Could not fetch user: {e}")

    print("\n--- Testing get_pending_payables ---")
    payables = get_pending_payables.invoke(entity_id)
    # print(payables[:500]) # Commenting out to avoid potential encoding issues in output if descriptions have weird chars
    if "No pending payables found" in payables:
        print("PASS: Correctly reported no data.")
    else:
        print(f"FAIL: Still showing mock data? Output: {payables[:100]}")

    print("\n--- Testing get_overdue_invoices ---")
    overdue = get_overdue_invoices.invoke(entity_id)
    if "No overdue invoices found" in overdue:
        print("PASS: Correctly reported no data.")
    else:
        print(f"FAIL: Still showing mock data? Output: {overdue[:100]}")
        
    print("\n--- Testing check_gst_compliance ---")
    gst = check_gst_compliance.invoke(entity_id)
    if "No GST Data Uploaded" in str(gst) or "filing_status" in str(gst):
        # We check if it returns the new specific dict
        if isinstance(gst, dict) and gst.get('filing_status') == "No GST Data Uploaded":
            print("PASS: Correctly reported no data.")
        else:
             print(f"INFO: Returned data: {str(gst)[:100]}")

    print("\n--- Testing analyze_ledger_spending ---")
    spending = analyze_ledger_spending.invoke(entity_id)
    if "Highest Spending Month" in spending:
        print("PASS: Found spending data.")
        print(spending) # Print this to see the real data
    elif "No explicit expense entries" in spending:
        print("WARN: No expenses found (maybe all entries are income?).")
    else:
        print(f"FAIL: Error or unexpected output: {spending[:100]}")

    db.close()

if __name__ == "__main__":
    test_tools()
