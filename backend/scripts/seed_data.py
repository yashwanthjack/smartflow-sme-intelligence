import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.entity import Entity
from app.models.counterparty import Counterparty
from app.models.ledger_entry import LedgerEntry
from app.models.invoice import Invoice
from sqlalchemy import text

fake = Faker('en_IN')  # Use Indian locale for realistic names

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed(email="admin@gmail.com"):
    print(f"🌱 Starting seed for user: {email}")
    db = SessionLocal()
    
    try:
        # 1. Get User & Entity
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.entity_id:
            print("❌ User not found or has no entity linked. Run seed_admin.py first.")
            return

        entity_id = user.entity_id
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        print(f"🏢 Seeding data for Entity: {entity.name} (ID: {entity_id})")

        # 2. Clear EXISTING data for this entity only
        print("🧹 Clearing old data for this entity...")
        db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).delete()
        db.query(Invoice).filter(Invoice.entity_id == entity_id).delete()
        db.query(Counterparty).filter(Counterparty.entity_id == entity_id).delete()
        db.commit()

        # 3. Create Counterparties (Customers & Vendors)
        print("👥 Creating Counterparties...")
        customers = []
        vendors = []
        
        # 20 Customers (SaaS/Tech)
        for _ in range(20):
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

        # 10 Vendors (AWS, Rent, etc)
        vendor_names = ["AWS Web Services", "WeWork India", "MacBook Vendor", "Google Workspace", "Slack", "HubSpot", "Office Pantry", "Legal Firm", "Recruiting Agency", "Zoom"]
        for name in vendor_names:
            v = Counterparty(
                entity_id=entity_id,
                name=name,
                counterparty_type="vendor",
                gstin=f"27{fake.bothify(text='?????####?')}1Z{fake.random_digit()}"
            )
            db.add(v)
            vendors.append(v)
            
        db.commit()
        
        # Reload to get IDs
        customers = db.query(Counterparty).filter(Counterparty.entity_id == entity_id, Counterparty.counterparty_type == "customer").all()
        vendors = db.query(Counterparty).filter(Counterparty.entity_id == entity_id, Counterparty.counterparty_type == "vendor").all()

        # 4. Generate Financial History (Last 6 Months)
        print("📅 Generating 6 months of financial history...")
        
        start_date = datetime.now() - timedelta(days=180)
        current_date = start_date
        
        # Initial Funding
        initial_balance = 5000000.0  # ₹50 Lakhs
        db.add(LedgerEntry(
            entity_id=entity_id,
            ledger_date=start_date,
            amount=initial_balance,
            category="equity",
            description="Seed Funding Tranche 1",
            source_type="manual"
        ))

        total_transactions = 0
        
        while current_date <= datetime.now():
            # A. Monthly Fixed Costs (Rent, Salaries, SaaS)
            if current_date.day == 1:
                # Rent
                db.add(LedgerEntry(
                    entity_id=entity_id,
                    ledger_date=current_date,
                    amount=-150000,
                    category="rent",
                    counterparty_id=next(v.id for v in vendors if "WeWork" in v.name),
                    description="Office Rent"
                ))
                # Salaries (Bulk)
                db.add(LedgerEntry(
                    entity_id=entity_id,
                    ledger_date=current_date,
                    amount=-850000, # ₹8.5L payroll
                    category="salary",
                    description="Monthly Payroll"
                ))
            
            # B. Random Daily Sales (Stripe/Online)
            if random.random() > 0.3: # 70% chance of sales
                daily_sales = random.randint(5000, 50000)
                db.add(LedgerEntry(
                    entity_id=entity_id,
                    ledger_date=current_date,
                    amount=daily_sales,
                    category="revenue",
                    subcategory="online",
                    description=f"Stripe Payout {current_date.strftime('%Y-%m-%d')}"
                ))
                total_transactions += 1

            # C. Invoices (B2B Deals) - Every few days
            if random.random() > 0.8:
                customer = random.choice(customers)
                amount = random.randint(50000, 500000)
                invoice_date = current_date
                due_date = invoice_date + timedelta(days=30)
                
                # Create Invoice
                inv = Invoice(
                    entity_id=entity_id,
                    counterparty_id=customer.id,
                    invoice_number=f"INV-{current_date.strftime('%Y')}-{random.randint(100, 999)}",
                    invoice_type="receivable",
                    invoice_date=invoice_date,
                    due_date=due_date,
                    amount=amount,
                    total_amount=amount * 1.18, # 18% GST
                    status="paid" if current_date < datetime.now() - timedelta(days=15) else "pending"
                )
                db.add(inv)
                db.flush() # get ID
                
                # If paid, add Ledger Entry
                if inv.status == "paid":
                    payment_date = invoice_date + timedelta(days=random.randint(5, 45))
                    if payment_date <= datetime.now():
                        inv.paid_amount = inv.total_amount
                        db.add(LedgerEntry(
                            entity_id=entity_id,
                            ledger_date=payment_date,
                            amount=inv.total_amount,
                            category="revenue",
                            subcategory="invoice",
                            invoice_id=inv.id,
                            counterparty_id=customer.id,
                            description=f"Payment for {inv.invoice_number}"
                        ))

            # D. Random Expenses (AWS, Travel, Food)
            if random.random() > 0.7:
                expense = random.randint(1000, 25000)
                vendor = random.choice(vendors)
                db.add(LedgerEntry(
                    entity_id=entity_id,
                    ledger_date=current_date,
                    amount=-expense,
                    category="expense",
                    subcategory="software" if "AWS" in vendor.name else "travel",
                    counterparty_id=vendor.id,
                    description=f"Payment to {vendor.name}"
                ))

            current_date += timedelta(days=1)
            
        db.commit()
        print(f"✅ Seed complete! Added {total_transactions} transactions.")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
