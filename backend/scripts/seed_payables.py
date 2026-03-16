import sys
import os
sys.path.append(os.getcwd())

from app.db.database import SessionLocal
from app.models.invoice import Invoice
from app.models.counterparty import Counterparty
from datetime import date, timedelta
import uuid

ENTITY_ID = "27104ef2-cb12-46fa-b930-88697712a90b"

def seed_payables():
    db = SessionLocal()
    try:
        # Check if payables exist
        count = db.query(Invoice).filter(
            Invoice.entity_id == ENTITY_ID,
            Invoice.invoice_type == "payable"
        ).count()
        
        print(f"Current Payable Invoices: {count}")
        
        if count > 0:
            print("Payables already exist. No need to seed.")
            return

        print("Seeding realistic payable invoices...")
        
        # Create vendors if needed
        vendors = [
            {"name": "AWS Cloud Services", "gstin": "29AAACS1234A1Z5"},
            {"name": "WeWork India", "gstin": "27AABCW5678B1Z2"},
            {"name": "Salesforce CRM", "gstin": "07AAACS9876C1Z8"},
            {"name": "Upwork Global Inc.", "gstin": "99AAACU4321D1Z0"}
        ]
        
        vendor_ids = []
        for v in vendors:
            cp = db.query(Counterparty).filter(
                Counterparty.entity_id == ENTITY_ID,
                Counterparty.name == v["name"]
            ).first()
            
            if not cp:
                cp = Counterparty(
                    id=str(uuid.uuid4()),
                    entity_id=ENTITY_ID,
                    name=v["name"],
                    gstin=v["gstin"],
                    counterparty_type="vendor",
                    contact_email=f"billing@{v['name'].split()[0].lower()}.com"
                )
                db.add(cp)
                db.commit()
                db.refresh(cp)
            vendor_ids.append(cp.id)
            
        # Create Invoices
        today = date.today()
        
        invoices_data = [
            {"vendor_idx": 0, "amount": 45000, "due": today + timedelta(days=2), "desc": "AWS Hosting Feb 2026"},
            {"vendor_idx": 1, "amount": 125000, "due": today + timedelta(days=5), "desc": "Office Rent Feb 2026"},
            {"vendor_idx": 2, "amount": 35000, "due": today + timedelta(days=10), "desc": "Salesforce License Q1"},
            {"vendor_idx": 3, "amount": 80000, "due": today + timedelta(days=1), "desc": "Freelance Developers Jan 2026"}
        ]
        
        for inv in invoices_data:
            new_inv = Invoice(
                id=str(uuid.uuid4()),
                entity_id=ENTITY_ID,
                counterparty_id=vendor_ids[inv["vendor_idx"]],
                invoice_number=f"INV-{uuid.uuid4().hex[:6].upper()}",
                invoice_date=today - timedelta(days=15),
                due_date=inv["due"],
                amount=inv["amount"],
                total_amount=inv["amount"],
                paid_amount=0,
                balance_due=inv["amount"],
                status="pending",
                invoice_type="payable"
            )
            db.add(new_inv)
            
        db.commit()
        print("Successfully seeded 4 payable invoices.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_payables()
