import os
import sys

# Add the current directory (root) to the Python path
sys.path.append(os.getcwd())

from backend.app.db.database import SessionLocal
from backend.app.models.ledger_entry import LedgerEntry
from sqlalchemy import func

def check():
    db = SessionLocal()
    entity_id = "cb8263ab-2463-4468-a16a-e340c006ccd6"
    h = db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).order_by(func.abs(LedgerEntry.amount).desc()).first()
    if h:
        print(f"HIGHEST: {h.amount} on {h.ledger_date} ({h.description})")
    else:
        print("NO DATA")
    db.close()

if __name__ == "__main__":
    check()
