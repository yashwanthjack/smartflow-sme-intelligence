
import sys
import os
from sqlalchemy import text

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.entity import Entity
from app.models.ledger_entry import LedgerEntry
from app.models.gst_summary import GSTSummary

def inspect_user_data(email):
    db = SessionLocal()
    try:
        print(f"--- Inspecting Data for {email} ---")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("User not found.")
            return

        print(f"User ID: {user.id}")
        print(f"Role: {user.role}")
        print(f"Entity ID: {user.entity_id}")

        if not user.entity_id:
            print("User has no entity assigned.")
            return

        entity = db.query(Entity).filter(Entity.id == user.entity_id).first()
        print(f"Entity Name: {entity.name}")
        print(f"Entity Type: {entity.entity_type}")

        # Check Ledger Entries
        ledger_count = db.query(LedgerEntry).filter(LedgerEntry.entity_id == user.entity_id).count()
        print(f"Ledger Entries: {ledger_count}")
        
        if ledger_count > 0:
            latest = db.query(LedgerEntry).filter(LedgerEntry.entity_id == user.entity_id).order_by(LedgerEntry.ledger_date.desc()).first()
            print(f"Latest Ledger Entry Date: {latest.ledger_date}")
            earliest = db.query(LedgerEntry).filter(LedgerEntry.entity_id == user.entity_id).order_by(LedgerEntry.ledger_date.asc()).first()
            print(f"Earliest Ledger Entry Date: {earliest.ledger_date}")

        # Check GST Data
        gst_count = db.query(GSTSummary).filter(GSTSummary.entity_id == user.entity_id).count()
        print(f"GST Summary Records: {gst_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_user_data("yashadmin@gmail.com")
