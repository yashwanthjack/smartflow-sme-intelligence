import sys
import os
import random
import json
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.counterparty import Counterparty
from app.models.ledger_entry import LedgerEntry
from app.models.invoice import Invoice
from app.models.gst_summary import GSTSummary
from app.models.audit_log import AuditLog
from app.auth import get_password_hash

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Use Indian locale for realistic names
fake = Faker('en_IN')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_demo(email="admin@gmail.com", password="admin"):
    print(f"Starting FULL DEMO seed for user: {email}")
    db = SessionLocal()
    
    try:
        # 1. Create User & Entity if missing
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating user {email}...")
            entity = Entity(
                id=str(uuid.uuid4()),
                name="SmartFlow Demo Corp",
                gstin="27AAEcs1234F1Z5",
                entity_type="sme"
            )
            db.add(entity)
            db.commit() # Get ID
            
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                hashed_password=get_password_hash(password),
                full_name="Demo Admin",
                role=UserRole.ADMIN,
                entity_id=entity.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            print("User created.")
        else:
            if not user.entity_id:
                print("User exists but has no entity. Fix manually.")
                return
            entity = db.query(Entity).filter(Entity.id == user.entity_id).first()
            print(f"Using existing Entity: {entity.name}")

        entity_id = entity.id

        # 2. Clear EXISTING data for this entity
        print("Clearing old data...")
        db.query(AuditLog).filter(AuditLog.entity_id == entity_id).delete()
        db.query(GSTSummary).filter(GSTSummary.entity_id == entity_id).delete()
        db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).delete()
        db.query(Invoice).filter(Invoice.entity_id == entity_id).delete()
        db.query(Counterparty).filter(Counterparty.entity_id == entity_id).delete()
        db.commit()

        # 3. Create Counterparties
        print("Creating Counterparties...")
        customers = []
        vendors = []
        
        # Customers
        for _ in range(15):
            c = Counterparty(
                entity_id=entity_id,
                name=fake.company(),
                counterparty_type="customer",
                contact_email=fake.company_email(),
                gstin=f"29{fake.bothify(text='?????####?')}1Z{fake.random_digit()}",
                avg_payment_delay=random.randint(0, 45)
            )
            db.add(c)
            customers.append(c)

        # Vendors
        vendor_names = ["AWS Web Services", "WeWork India", "MacBook Vendor", "Google Workspace", "Slack", "Office Pantry", "Legal Firm", "Recruiting Agency"]
        for name in vendor_names:
            v = Counterparty(
                entity_id=entity_id,
                name=name,
                counterparty_type="vendor",
                contact_email=f"billing@{name.lower().replace(' ', '')}.com", 
                gstin=f"27{fake.bothify(text='?????####?')}1Z{fake.random_digit()}"
            )
            db.add(v)
            vendors.append(v)
            
        db.commit()
        # Custom Maps for ID lookup to avoid session issues
        cust_list = [{'id': c.id, 'name': c.name} for c in customers]
        vend_list = [{'id': v.id, 'name': v.name} for v in vendors]

        # Create lookups based on partial name match
        vendor_map = {}
        for v in vend_list:
            if "AWS" in v['name']: vendor_map["AWS"] = v['id']
            elif "WeWork" in v['name']: vendor_map["WeWork"] = v['id']
            else: vendor_map[v['name']] = v['id']
            
        # Also map standard names for fallback
        if "AWS" not in vendor_map and vend_list: vendor_map["AWS"] = vend_list[0]['id']
        if "WeWork" not in vendor_map and vend_list: vendor_map["WeWork"] = vend_list[0]['id']

        # 4. Generate Financial History (Last 6 Months)
        print("Generating 6 months of financial history...")
        start_date = datetime.now() - timedelta(days=180)
        current_date = start_date
        
        # Seed Funding
        db.add(LedgerEntry(
            entity_id=entity_id,
            ledger_date=start_date,
            amount=5000000.0,
            category="equity",
            description="Seed Funding Round",
            source_type="manual"
        ))

        while current_date <= datetime.now():
            # Monthly Recurring
            if current_date.day == 1:
                db.add(LedgerEntry(entity_id=entity_id, ledger_date=current_date, amount=-150000, category="rent", description="Office Rent", counterparty_id=vendor_map.get("WeWork")))
                db.add(LedgerEntry(entity_id=entity_id, ledger_date=current_date, amount=-850000, category="salary", description="Monthly Payroll"))
                db.add(LedgerEntry(entity_id=entity_id, ledger_date=current_date, amount=-45000, category="software", description="AWS Invoice", counterparty_id=vendor_map.get("AWS")))

            # Random Sales
            if random.random() > 0.4:
                amt = random.randint(5000, 35000)
                db.add(LedgerEntry(entity_id=entity_id, ledger_date=current_date, amount=amt, category="revenue", subcategory="online", description="Stripe Payout"))

            # Invoices (Receivables)
            if random.random() > 0.85:
                start_cust = random.choice(cust_list)
                amt = random.randint(50000, 400000)
                inv_date = current_date
                due_date = inv_date + timedelta(days=30)
                
                status = "paid"
                if inv_date > datetime.now() - timedelta(days=20): status = "pending"
                if inv_date < datetime.now() - timedelta(days=40) and random.random() > 0.7: status = "overdue"

                inv = Invoice(
                    entity_id=entity_id, counterparty_id=start_cust['id'],
                    invoice_number=f"INV-{random.randint(1000, 9999)}",
                    invoice_type="receivable", invoice_date=inv_date, due_date=due_date,
                    amount=amt, total_amount=amt*1.18, status=status
                )
                db.add(inv)
                db.flush() 
                
                if status == "paid":
                    pay_date = inv_date + timedelta(days=random.randint(5, 40))
                    if pay_date <= datetime.now():
                        inv.paid_amount = inv.total_amount
                        db.add(LedgerEntry(
                            entity_id=entity_id, ledger_date=pay_date, amount=inv.total_amount,
                            category="revenue", subcategory="invoice", invoice_id=inv.id, counterparty_id=start_cust['id'],
                            description=f"Payment from {start_cust['name']}"
                        ))
            
            # Audit Logs (Activity Feed)
            if random.random() > 0.7:
                agent = random.choice(["CollectionsAgent", "GSTAgent", "PaymentsAgent", "DecisionAdvisorAgent"])
                action = ""
                details = {}
                if agent == "CollectionsAgent":
                    action = "sent_reminder"
                    details = {"customer": random.choice(cust_list)['name'], "invoice": f"INV-{random.randint(1000,9999)}"}
                elif agent == "GSTAgent":
                    action = "compliance_check"
                    details = {"status": "compliant", "mismatch_count": 0}
                elif agent == "PaymentsAgent":
                    action = "scheduled_payment"
                    details = {"vendor": random.choice(vend_list)['name'], "amount": random.randint(10000, 50000)}
                elif agent == "DecisionAdvisorAgent":
                    action = "analyzed_burn"
                    details = {"burn_rate": "stable"}

                db.add(AuditLog(
                    entity_id=entity_id,
                    agent_name=agent,
                    action=action,
                    details=json.dumps(details),
                    created_at=current_date + timedelta(hours=random.randint(9, 18))
                ))

            current_date += timedelta(days=1)

        # 5. Generate GST Summary
        print("Generating GST Records...")
        # Helper to get start/end dates
        def get_period_dates(period_str):
            # period_str "YYYY-MM"
            dt = datetime.strptime(period_str, "%Y-%m")
            start = dt.date()
            # End is last day of month
            next_month = dt.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
            return start, end

        months = ["2024-10", "2024-11", "2024-12", "2025-01", "2025-02"]
        for m in months:
            start, end = get_period_dates(m)
            
            # GSTR-1
            db.add(GSTSummary(
                entity_id=entity_id,
                return_type="GSTR-1",
                period=m,
                period_start=start,
                period_end=end,
                output_tax=random.randint(50000, 150000),
                filing_status="filed",
                filed_on=datetime.now() - timedelta(days=random.randint(1, 10))
            ))
            # GSTR-3B
            db.add(GSTSummary(
                entity_id=entity_id,
                return_type="GSTR-3B",
                period=m,
                period_start=start,
                period_end=end,
                tax_paid=random.randint(40000, 120000),
                input_credit=random.randint(10000, 30000),
                filing_status="filed",
                filed_on=datetime.now() - timedelta(days=random.randint(1, 5))
            ))

        # Add a pending one
        start_p, end_p = get_period_dates("2025-03")
        db.add(GSTSummary(
            entity_id=entity_id,
            return_type="GSTR-3B",
            period="2025-03",
            period_start=start_p,
            period_end=end_p,
            tax_paid=0,
            filing_status="pending"
        ))
        
        # Add some ITC Mismatches (GSTR-2B not 2A usually, but model says 2A context)
        # Using GSTR-2B logic as per model logic? Model has return_type string.
        start_m, end_m = get_period_dates("2025-02")
        db.add(GSTSummary(
             entity_id=entity_id,
             return_type="GSTR-2A",
             period="2025-02",
             period_start=start_m,
             period_end=end_m,
             input_credit=10000,
             filing_status="checked",
             mismatch_score=12450.0 
        ))

        db.commit()
        print("FULL DEMO SEED COMPLETE for admin@gmail.com")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo()
