from app.db.database import SessionLocal
from app.models.ledger_entry import LedgerEntry
from datetime import datetime
import uuid

def seed_anomaly():
    db = SessionLocal()
    # Using the standard test entity ID
    entity_id = "04e12fbc-4784-4c46-83ed-4b35123863d2"
    
    # 1. Seed a massive transaction to test Anomaly Sensing
    tx_massive = LedgerEntry(
        id=str(uuid.uuid4()),
        entity_id=entity_id,
        ledger_date=datetime.now(),
        description="Massive Server Hardware Purchase",
        category="Equipment",
        amount=-550000.0,
        currency="INR"
    )
    
    # 2. Seed some personal-sounding transactions to trigger "PERSONAL" account auto-sense
    personal_txs = [
        LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=datetime.now(),
            description="Zomato Food Delivery",
            category="Dining",
            amount=-850.0,
            currency="INR"
        ),
        LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=datetime.now(),
            description="Netflix Subscription",
            category="Entertainment",
            amount=-649.0,
            currency="INR"
        ),
        LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=datetime.now(),
            description="Amazon Shopping - Groceries",
            category="Shopping",
            amount=-3200.0,
            currency="INR"
        ),
        LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=datetime.now(),
            description="Uber Ride - Downtown",
            category="Travel",
            amount=-450.0,
            currency="INR"
        )
    ]
    
    try:
        db.add(tx_massive)
        for tx in personal_txs:
            db.add(tx)
        db.commit()
        print("Successfully seeded anomalous & personal test transactions.")
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_anomaly()
