import sys
import os
import requests
import json
import random
from datetime import timedelta, date
from sqlalchemy.orm import Session

# Add backend directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.db.database import SessionLocal
from app.models.entity import Entity
from app.models.user import User
from app.models.ledger_entry import LedgerEntry
from scripts.seed_database import seed_counterparties, seed_ledger_from_tally, seed_invoices_from_gst

BASE_URL = "http://localhost:8000/api"

def seed_bank_data(db: Session, entity: Entity):
    """Generate synthetic bank statement data."""
    print("   Seeding Synthetic Bank Statement Data...")
    
    # Check if bank data already exists
    existing = db.query(LedgerEntry).filter(
        LedgerEntry.entity_id == entity.id,
        LedgerEntry.source_type == "bank_statement"
    ).first()
    
    if existing:
        print("   ✅ Bank data already exists, skipping...")
        return

    entries = []
    base_date = date.today() - timedelta(days=90)
    
    # Sample transaction descriptions
    descriptions = [
        ("UPI-PAYTM-123456", "expense", "utilities", -1500),
        ("NEFT-KOTAK-SALARY", "expense", "payroll", -250000),
        ("ACH-DEBIT-AWS", "expense", "software", -5000),
        ("POS-SWIPE-MCD", "expense", "meals", -800),
        ("UPI-PHONEPE-CLIENT", "revenue", "sales", 15000),
        ("NEFT-HDFC-VENDOR", "expense", "inventory", -45000),
        ("RTGS-INWARD-BIGCLIENT", "revenue", "sales", 500000),
        ("ATM-CASH-WD", "expense", "petty_cash", -10000),
        ("CHQ-DEP-CLEARING", "revenue", "sales", 85000),
        ("RENT-AUTO-DEBIT", "expense", "rent", -75000)
    ]
    
    for i in range(50):
        txn_date = base_date + timedelta(days=random.randint(0, 90))
        desc, cat, subcat, approx_amt = random.choice(descriptions)
        
        # Randomize amount slightly
        amount = approx_amt * random.uniform(0.9, 1.1)
        
        entry = LedgerEntry(
            entity_id=entity.id,
            ledger_date=txn_date,
            amount=amount,
            currency="INR",
            category=cat,
            subcategory=subcat,
            source_type="bank_statement",
            source_record_id=f"BANK-TXN-{i}",
            description=f"{desc} - {txn_date.strftime('%b')}"
        )
        entries.append(entry)
    
    db.add_all(entries)
    db.commit()
    print(f"   ✅ Created {len(entries)} bank transactions")

def populate_demo_user():
    print("🚀 Starting Demo Population Script")
    print("===================================")

    email = "yashwanth@gmail.com"
    password = "Rryg@2005"
    full_name = "Yashwanth Demo"

    db = SessionLocal()

    # 1. Register User (or get existing)
    print(f"\n1. checking User: {email}")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("   User not found, registering via API...")
        # (API call logic removed for simplicity since we have DB access)
        # Verify via API for completeness or just create directly? 
        # Using DB directly to ensure Entity creation logic handles re-runs properly
        
        # Need to re-implement creation logic here or call API?
        # Let's stick to API for Registration to test it, but fallback to manual fix
        try:
             reg_payload = {"email": email, "password": password, "full_name": full_name}
             requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
             print("   User registered via API")
        except:
             pass
        user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print("❌ Failed to create/find user")
        return

    # 2. Fix Entity Linkage
    print(f"\n2. Ensuring Entity Linkage for {user.email}...")
    
    if not user.entity_id:
        print("   User missing entity_id. Creating one now...")
        org_name = "SmartFlow Demo Textiles"
        
        # Check if entity exists but isn't linked
        existing_entity = db.query(Entity).filter(Entity.gstin == "33AABCU9603R1ZM").first()
        
        if existing_entity:
            entity = existing_entity
            print(f"   Found existing entity: {entity.name}")
        else:
            entity = Entity(
                name=org_name,
                gstin="33AABCU9603R1ZM",
                pan="AABCU9603R", 
                state="Tamil Nadu",
                city="Chennai",
                industry="Textiles",
                entity_type="sme"
            )
            db.add(entity)
            db.commit()
            db.refresh(entity)
            print(f"   Created new entity: {entity.name}")
            
        user.entity_id = entity.id
        db.commit()
        print(f"   ✅ User linked to Entity: {entity.id}")
        
    entity_id = user.entity_id

    # 3. Login to get token (for verification steps)
    print(f"\n3. Logging in to verify API access...")
    try:
        token_res = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
        if token_res.status_code == 200:
            token = token_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Login successful")
        else:
            print(f"   ⚠️ Login failed (check password?): {token_res.text}")
            # Continue anyway as we have DB access
    except Exception as e:
        print(f"   ⚠️ API Login check failed: {e}")

    # 4. Seed Data
    print(f"\n4. Seeding Data for Entity...")
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if entity.name != "SmartFlow Demo Textiles":
             entity.name = "SmartFlow Demo Textiles"
             db.commit()

        # Run Standard Seeding
        counterparties = seed_counterparties(db, entity)
        seed_ledger_from_tally(db, entity, counterparties)
        seed_invoices_from_gst(db, entity, counterparties)
        
        # RUN BANK SEEDING
        seed_bank_data(db, entity)
        
        print("\n✅ Data Population Complete!")
        
    except Exception as e:
        print(f"❌ Seeding Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    # 5. Verify Metrics
    if 'headers' in locals():
        print(f"\n5. Verifying Dashboard Metrics via API...")
        try:
            metrics_res = requests.get(f"{BASE_URL}/data/entities/{entity_id}/financial-metrics", headers=headers)
            if metrics_res.status_code == 200:
                print("✅ Dashboard Metrics API: OK")
                print(json.dumps(metrics_res.json(), indent=2))
            else:
                print(f"❌ Dashboard Metrics API Failed: {metrics_res.status_code}")
        except Exception as e:
            print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    populate_demo_user()
