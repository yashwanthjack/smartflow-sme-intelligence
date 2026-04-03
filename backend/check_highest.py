import os
import sys
from sqlalchemy import func

# Ensure we can import from 'app'
sys.path.append(os.getcwd())

try:
    from app.db.database import SessionLocal
    from app.models.ledger_entry import LedgerEntry
    
    db = SessionLocal()
    entity_id = "98659f3b-1fcd-469f-b4f3-ca0398b28461"
    h = db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).order_by(func.abs(LedgerEntry.amount).desc()).first()
    if h:
        print(f"SUCCESS_DB_VALUE: {h.amount} | {h.description} | {h.ledger_date}")
    else:
        print("ERROR: No data found for entity.")
    db.close()
except Exception as e:
    print(f"ERROR: {str(e)}")
