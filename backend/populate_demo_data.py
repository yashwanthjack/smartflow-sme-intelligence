#!/usr/bin/env python
"""
Populate SQLite database with realistic financial data for demo user
User: yash@gmail.com / yash@1234
"""

import os
import sys
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List
import hashlib

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import all models to register them with Base
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.invoice import Invoice
from app.models.account import Account
from app.models.counterparty import Counterparty
from app.models.cash_flow import CashFlow
from app.models.case import Case
from app.models.audit_log import AuditLog
from app.models.credit_feature import CreditFeature
from app.models.gst_summary import GSTSummary
from app.models.ledger_entry import LedgerEntry

from app.db.database import Base
from app.config import settings

# Hash password function
def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_user(session: Session) -> User:
    """Create demo user account"""
    print("Creating user: yash@gmail.com...")
    
    user = User(
        id=str(uuid.uuid4()),
        email="yash@gmail.com",
        hashed_password=hash_password("yash@1234"),
        full_name="Yash Sharma",
        role=UserRole.ADMIN,
        is_active=True
    )
    
    session.add(user)
    session.commit()
    print(f"✓ User created: {user.email} (ID: {user.id})")
    return user

def create_demo_entity(session: Session, user: User) -> Entity:
    """Create demo SME entity"""
    print("\nCreating SME entity...")
    
    entity = Entity(
        id=str(uuid.uuid4()),
        name="TechFlow Solutions Pvt Ltd",
        entity_type="sme",
        gstin="27AABCR5055K1Z0",
        pan="AABCR5055K",
        industry="Software & IT Services",
        city="Bangalore",
        state="Karnataka",
        is_public_profile=True,
        public_profile_slug="techflow-solutions"
    )
    
    session.add(entity)
    session.commit()
    print(f"✓ Entity created: {entity.name} (ID: {entity.id})")
    return entity

def create_counterparties(session: Session, entity: Entity) -> List[Counterparty]:
    """Create realistic counterparties (customers & vendors)"""
    print("\nCreating counterparties...")
    
    counterparties_data = [
        # Customers
        {
            "name": "Global Finance Solutions",
            "type": "customer",
            "gstin": "27AABCU9603R1Z5",
            "avg_delay": 5,
            "risk_score": 0.3,
            "credit_limit": 500000
        },
        {
            "name": "Digital Innovations Ltd",
            "type": "customer",
            "gstin": "27AABCQ5678R1Z0",
            "avg_delay": 8,
            "risk_score": 0.4,
            "credit_limit": 750000
        },
        # Vendors
        {
            "name": "CloudServe Infrastructure",
            "type": "vendor",
            "gstin": "27AABCX1234R1Z0",
            "avg_delay": 0,
            "risk_score": 0.2,
            "credit_limit": 200000
        },
        {
            "name": "Talent Nexus HR Services",
            "type": "vendor",
            "gstin": "27AABCZ5789R1Z0",
            "avg_delay": 2,
            "risk_score": 0.25,
            "credit_limit": 150000
        },
        {
            "name": "QuickSupply Materials",
            "type": "vendor",
            "gstin": "27AABCY9012R1Z0",
            "avg_delay": 3,
            "risk_score": 0.35,
            "credit_limit": 300000
        }
    ]
    
    counterparties = []
    for cp_data in counterparties_data:
        cp = Counterparty(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            name=cp_data["name"],
            counterparty_type=cp_data["type"],
            gstin=cp_data["gstin"],
            contact_email=f"contact@{cp_data['name'].lower().replace(' ', '')}.com",
            contact_phone=f"+91 {9000 + len(counterparties)}000000",
            avg_payment_delay=cp_data["avg_delay"],
            risk_score=cp_data["risk_score"],
            credit_limit=cp_data["credit_limit"]
        )
        session.add(cp)
        counterparties.append(cp)
    
    session.commit()
    print(f"✓ Created {len(counterparties)} counterparties")
    return counterparties

def create_bank_accounts(session: Session, entity: Entity) -> List[Account]:
    """Create realistic bank accounts"""
    print("\nCreating bank accounts...")
    
    accounts_data = [
        {
            "bank": "HDFC Bank",
            "type": "current",
            "balance": 450000,
            "od_limit": 1000000,
            "cc_limit": 0,
            "ifsc": "HDFC0000001"
        },
        {
            "bank": "ICICI Bank",
            "type": "current",
            "balance": 250000,
            "od_limit": 500000,
            "cc_limit": 0,
            "ifsc": "ICIC0000012"
        },
        {
            "bank": "Axis Bank",
            "type": "savings",
            "balance": 100000,
            "od_limit": 0,
            "cc_limit": 0,
            "ifsc": "UTIB0000014"
        }
    ]
    
    accounts = []
    for idx, acc_data in enumerate(accounts_data):
        acc = Account(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            bank_name=acc_data["bank"],
            account_number=f"1234567890{idx + 1}",
            ifsc_code=acc_data["ifsc"],
            account_type=acc_data["type"],
            current_balance=acc_data["balance"],
            od_limit=acc_data["od_limit"],
            cc_limit=acc_data["cc_limit"],
            is_primary=idx == 0,
            status="active"
        )
        session.add(acc)
        accounts.append(acc)
    
    session.commit()
    print(f"✓ Created {len(accounts)} bank accounts")
    print(f"  Total balance: ₹{sum(a.current_balance for a in accounts):,.0f}")
    return accounts

def create_invoices(session: Session, entity: Entity, counterparties: List[Counterparty]) -> List[Invoice]:
    """Create realistic invoices (AR & AP)"""
    print("\nCreating invoices...")
    
    invoices = []
    today = date.today()
    
    # Customer invoices (Receivables)
    customers = [cp for cp in counterparties if cp.counterparty_type == "customer"]
    ar_invoices = [
        {
            "customer": customers[0],
            "number": "SO-2024-001",
            "date": today - timedelta(days=45),
            "due_date": today - timedelta(days=15),
            "amount": 250000,
            "tax": 45000,
            "status": "overdue",
            "paid": 0
        },
        {
            "customer": customers[0],
            "number": "SO-2024-002",
            "date": today - timedelta(days=30),
            "due_date": today - timedelta(days=5),
            "amount": 150000,
            "tax": 27000,
            "status": "overdue",
            "paid": 0
        },
        {
            "customer": customers[1],
            "number": "SO-2024-003",
            "date": today - timedelta(days=20),
            "due_date": today + timedelta(days=10),
            "amount": 400000,
            "tax": 72000,
            "status": "pending",
            "paid": 0
        },
        {
            "customer": customers[1],
            "number": "SO-2024-004",
            "date": today - timedelta(days=10),
            "due_date": today + timedelta(days=20),
            "amount": 200000,
            "tax": 36000,
            "status": "pending",
            "paid": 0
        },
        {
            "customer": customers[0],
            "number": "SO-2024-005",
            "date": today - timedelta(days=5),
            "due_date": today + timedelta(days=25),
            "amount": 300000,
            "tax": 54000,
            "status": "partial",
            "paid": 150000
        }
    ]
    
    # Vendor invoices (Payables)
    vendors = [cp for cp in counterparties if cp.counterparty_type == "vendor"]
    ap_invoices = [
        {
            "vendor": vendors[0],
            "number": "PO-2024-101",
            "date": today - timedelta(days=30),
            "due_date": today - timedelta(days=5),
            "amount": 100000,
            "tax": 18000,
            "status": "overdue",
            "paid": 0
        },
        {
            "vendor": vendors[1],
            "number": "PO-2024-102",
            "date": today - timedelta(days=20),
            "due_date": today + timedelta(days=10),
            "amount": 75000,
            "tax": 13500,
            "status": "pending",
            "paid": 0
        },
        {
            "vendor": vendors[2],
            "number": "PO-2024-103",
            "date": today - timedelta(days=10),
            "due_date": today + timedelta(days=20),
            "amount": 120000,
            "tax": 21600,
            "status": "pending",
            "paid": 0
        },
        {
            "vendor": vendors[0],
            "number": "PO-2024-104",
            "date": today - timedelta(days=5),
            "due_date": today + timedelta(days=25),
            "amount": 50000,
            "tax": 9000,
            "status": "paid",
            "paid": 59000
        }
    ]
    
    # Create AR invoices
    for inv_data in ar_invoices:
        total = inv_data["amount"] + inv_data["tax"]
        inv = Invoice(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            counterparty_id=inv_data["customer"].id,
            invoice_number=inv_data["number"],
            invoice_type="receivable",
            invoice_date=inv_data["date"],
            due_date=inv_data["due_date"],
            amount=inv_data["amount"],
            tax_amount=inv_data["tax"],
            total_amount=total,
            paid_amount=inv_data["paid"],
            balance_due=total - inv_data["paid"],
            status=inv_data["status"],
            days_overdue=max(0, (today - inv_data["due_date"]).days)
        )
        session.add(inv)
        invoices.append(inv)
    
    # Create AP invoices
    for inv_data in ap_invoices:
        total = inv_data["amount"] + inv_data["tax"]
        inv = Invoice(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            counterparty_id=inv_data["vendor"].id,
            invoice_number=inv_data["number"],
            invoice_type="payable",
            invoice_date=inv_data["date"],
            due_date=inv_data["due_date"],
            amount=inv_data["amount"],
            tax_amount=inv_data["tax"],
            total_amount=total,
            paid_amount=inv_data["paid"],
            balance_due=total - inv_data["paid"],
            status=inv_data["status"],
            days_overdue=max(0, (today - inv_data["due_date"]).days)
        )
        session.add(inv)
        invoices.append(inv)
    
    session.commit()
    print(f"✓ Created {len(invoices)} invoices")
    
    # Summary
    ar = [i for i in invoices if i.invoice_type == "receivable"]
    ap = [i for i in invoices if i.invoice_type == "payable"]
    print(f"  - Accounts Receivable: {len(ar)} invoices, Total: ₹{sum(i.total_amount for i in ar):,.0f}")
    print(f"  - Accounts Payable: {len(ap)} invoices, Total: ₹{sum(i.total_amount for i in ap):,.0f}")
    
    return invoices

def create_cash_flows(session: Session, entity_id: str) -> List[CashFlow]:
    """Create realistic cash flow records"""
    print("\nCreating cash flow records...")
    
    cash_flows = []
    today = date.today()
    
    # Simulate 30 days of cash flows
    for i in range(30):
        cf_date = today - timedelta(days=30 - i)
        
        # Inflows (customer payments)
        if i % 5 == 0:
            cf_in = CashFlow(
                case_id=entity_id,
                transaction_date=cf_date,
                description=f"Customer Payment - Invoice SO-2024-{i%5+1:03d}",
                inflow=50000 + (i * 5000),
                outflow=0,
                category="sales",
                counterparty="Global Finance Solutions",
                status="completed",
                notes="Received"
            )
            session.add(cf_in)
            cash_flows.append(cf_in)
        
        # Outflows (vendor payments, operations)
        if i % 3 == 0:
            cf_out = CashFlow(
                case_id=entity_id,
                transaction_date=cf_date,
                description=f"Vendor Payment - Invoice PO-2024-{i%3+101:03d}",
                inflow=0,
                outflow=30000 + (i * 2000),
                category="operations",
                counterparty="CloudServe Infrastructure",
                status="completed",
                notes="Paid"
            )
            session.add(cf_out)
            cash_flows.append(cf_out)
        
        # Payroll
        if i % 7 == 0:
            cf_payroll = CashFlow(
                case_id=entity_id,
                transaction_date=cf_date,
                description="Payroll - Monthly salary & benefits",
                inflow=0,
                outflow=150000,
                category="payroll",
                counterparty="Internal",
                status="completed",
                notes="Processed"
            )
            session.add(cf_payroll)
            cash_flows.append(cf_payroll)
    
    session.commit()
    print(f"✓ Created {len(cash_flows)} cash flow records")
    total_in = sum(cf.inflow for cf in cash_flows)
    total_out = sum(cf.outflow for cf in cash_flows)
    print(f"  - Total Inflows: ₹{total_in:,.0f}")
    print(f"  - Total Outflows: ₹{total_out:,.0f}")
    print(f"  - Net Cash Flow: ₹{total_in - total_out:,.0f}")
    
    return cash_flows

def main():
    """Run complete data population"""
    print("=" * 60)
    print("SmartFlow Demo Database Population")
    print("=" * 60)
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == "yash@gmail.com").first()
        if existing_user:
            print("\n⚠ User yash@gmail.com already exists!")
            print("Clearing existing data...")
            # Delete existing data
            session.query(CashFlow).delete()
            session.query(Invoice).delete()
            session.query(Account).delete()
            session.query(Counterparty).delete()
            session.query(Entity).delete()
            session.query(User).delete()
            session.commit()
            print("✓ Cleared existing data")
        
        # Create user
        user = create_demo_user(session)
        
        # Create entity
        entity = create_demo_entity(session, user)
        
        # Create counterparties
        counterparties = create_counterparties(session, entity)
        
        # Create bank accounts
        accounts = create_bank_accounts(session, entity)
        
        # Create invoices
        invoices = create_invoices(session, entity, counterparties)
        
        # Create cash flows
        cash_flows = create_cash_flows(session, entity.id)
        
        print("\n" + "=" * 60)
        print("Demo Data Population Complete!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print(f"  Email: yash@gmail.com")
        print(f"  Password: yash@1234")
        print("\nDatabase Summary:")
        print(f"  Users: {session.query(User).count()}")
        print(f"  Entities: {session.query(Entity).count()}")
        print(f"  Counterparties: {session.query(Counterparty).count()}")
        print(f"  Bank Accounts: {session.query(Account).count()}")
        print(f"  Invoices: {session.query(Invoice).count()}")
        print(f"  Cash Flows: {session.query(CashFlow).count()}")
        print("\n✓ Ready to use!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
