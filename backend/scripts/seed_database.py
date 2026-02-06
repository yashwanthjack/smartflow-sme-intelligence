# Database Seeding Script for SmartFlow
# Creates demo entity with sample transactions from Tally ledger and GST data

import sys
import os
import json
import csv
from datetime import datetime, date
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal

# Import ALL models to register with SQLAlchemy metadata (required for foreign keys)
from app.models.entity import Entity
from app.models.account import Account
from app.models.counterparty import Counterparty
from app.models.ledger_entry import LedgerEntry
from app.models.invoice import Invoice
from app.models.gst_summary import GSTSummary
from app.models.cash_flow import CashFlow
from app.models.credit_feature import CreditFeature
from app.models.audit_log import AuditLog
from app.models.case import Case


def parse_date(date_str: str, formats: list = None) -> date:
    """Parse date from various formats."""
    formats = formats or ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def seed_entity(db: Session) -> Entity:
    """Create demo SME entity."""
    entity = db.query(Entity).filter(Entity.gstin == "33AABCU9603R1ZM").first()
    if entity:
        print(f"✅ Entity already exists: {entity.name}")
        return entity
    
    entity = Entity(
        name="SmartFlow Demo Textiles",
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
    print(f"✅ Created entity: {entity.name}")
    return entity


def seed_counterparties(db: Session, entity: Entity) -> dict:
    """Create counterparties from ledger data."""
    counterparties = {}
    
    # Known counterparties from sample data
    cp_list = [
        {"name": "ABC Textiles", "gstin": "33AABCT1332L1ZZ", "type": "customer"},
        {"name": "Krishna Retail", "gstin": "33AABCK1111R1ZZ", "type": "customer"},
        {"name": "Gupta Sarees", "gstin": "33AABCG2222S1ZZ", "type": "customer"},
        {"name": "New Fashion Store", "gstin": "33AABCN3333F1ZZ", "type": "customer"},
        {"name": "Royal Garments", "gstin": "33AABCR4444G1ZZ", "type": "customer"},
        {"name": "City Fashions", "gstin": "33AABCC5555F1ZZ", "type": "customer"},
        {"name": "Metro Textiles", "gstin": "33AABCM5678N1ZP", "type": "customer"},
        {"name": "Elegant Wear", "gstin": "33AABCE6666W1ZZ", "type": "customer"},
        {"name": "Fashion Hub", "gstin": "33AABCF7777H1ZZ", "type": "customer"},
        {"name": "Trendy Collections", "gstin": "33AABCT8888C1ZZ", "type": "customer"},
        {"name": "Style Point", "gstin": "33AABCS9999P1ZZ", "type": "customer"},
        {"name": "Mehta Fabrics", "gstin": "33AABCM1234F1ZZ", "type": "vendor"},
        {"name": "Patel Threads", "gstin": "33AABCP2345T1ZZ", "type": "vendor"},
        {"name": "Sharma Dyes", "gstin": "33AABCS3456D1ZZ", "type": "vendor"},
        {"name": "Quality Fabrics", "gstin": "33AABCQ4567F1ZZ", "type": "vendor"},
        {"name": "Mumbai Threads", "gstin": "27AABCM5678T1ZZ", "type": "vendor"},
    ]
    
    for cp_data in cp_list:
        existing = db.query(Counterparty).filter(
            Counterparty.entity_id == entity.id,
            Counterparty.name == cp_data["name"]
        ).first()
        
        if existing:
            counterparties[cp_data["name"]] = existing
            continue
        
        cp = Counterparty(
            entity_id=entity.id,
            name=cp_data["name"],
            gstin=cp_data["gstin"],
            counterparty_type=cp_data["type"]
        )
        db.add(cp)
        counterparties[cp_data["name"]] = cp
    
    db.commit()
    print(f"✅ Created {len(counterparties)} counterparties")
    return counterparties


def seed_ledger_from_tally(db: Session, entity: Entity, counterparties: dict):
    """Ingest Tally ledger CSV into ledger_entries table."""
    csv_path = os.path.join(os.path.dirname(__file__), '../../sample_data/tally_ledger_sample.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Tally CSV not found: {csv_path}")
        return
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entries = []
        
        for row in reader:
            if not row.get('Date'):
                continue
            
            try:
                ledger_date = parse_date(row['Date'])
            except ValueError as e:
                print(f"⚠️ Skipping row with bad date: {row['Date']}")
                continue
            
            # Determine amount (positive for inflow, negative for outflow)
            debit = float(row.get('Debit') or 0)
            credit = float(row.get('Credit') or 0)
            
            if row['Voucher Type'] in ['Sales', 'Receipt']:
                amount = credit if credit else debit  # Inflow
            else:
                amount = -debit if debit else -credit  # Outflow
            
            # Find counterparty from particulars
            particulars = row.get('Particulars', '')
            cp_id = None
            for name, cp in counterparties.items():
                if name.lower() in particulars.lower():
                    cp_id = cp.id
                    break
            
            # Determine category
            voucher_type = row.get('Voucher Type', '')
            category_map = {
                'Sales': 'revenue',
                'Receipt': 'revenue',
                'Purchase': 'expense',
                'Payment': 'expense',
                'Expense': 'expense'
            }
            category = category_map.get(voucher_type, 'other')
            
            entry = LedgerEntry(
                entity_id=entity.id,
                ledger_date=ledger_date,
                amount=amount,
                currency="INR",
                counterparty_id=cp_id,
                category=category,
                subcategory=voucher_type.lower(),
                source_type="tally",
                source_record_id=row.get('Voucher No'),
                description=particulars
            )
            entries.append(entry)
        
        db.add_all(entries)
        db.commit()
        print(f"✅ Inserted {len(entries)} ledger entries from Tally")


def seed_invoices_from_gst(db: Session, entity: Entity, counterparties: dict):
    """Create invoices from GSTR1 sample data."""
    json_path = os.path.join(os.path.dirname(__file__), '../../sample_data/gstr1_sample.json')
    
    if not os.path.exists(json_path):
        print(f"❌ GSTR1 JSON not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        gst_data = json.load(f)
    
    invoices = []
    
    # Process B2B invoices
    for b2b in gst_data.get('b2b', []):
        ctin = b2b.get('ctin')
        
        # Find or create counterparty
        cp = db.query(Counterparty).filter(
            Counterparty.entity_id == entity.id,
            Counterparty.gstin == ctin
        ).first()
        
        if not cp:
            cp = Counterparty(
                entity_id=entity.id,
                name=f"Customer {ctin[:10]}",
                gstin=ctin,
                counterparty_type="customer"
            )
            db.add(cp)
            db.flush()
        
        for inv in b2b.get('inv', []):
            inv_date = parse_date(inv['idt'])
            total_tax = sum(
                itm['itm_det'].get('camt', 0) + itm['itm_det'].get('samt', 0) + itm['itm_det'].get('iamt', 0)
                for itm in inv.get('itms', [])
            )
            taxable_value = sum(itm['itm_det'].get('txval', 0) for itm in inv.get('itms', []))
            
            invoice = Invoice(
                entity_id=entity.id,
                counterparty_id=cp.id,
                invoice_number=inv['inum'],
                invoice_type="receivable",
                invoice_date=inv_date,
                due_date=inv_date,  # Same day for GST
                amount=taxable_value,
                tax_amount=total_tax,
                total_amount=inv['val'],
                paid_amount=0,
                balance_due=inv['val'],
                status="pending",
                gst_invoice_id=inv['inum']
            )
            invoices.append(invoice)
    
    db.add_all(invoices)
    db.commit()
    print(f"✅ Created {len(invoices)} invoices from GSTR1")


def seed_gst_summary(db: Session, entity: Entity):
    """Create GST summary records."""
    gst_records = [
        {
            "filing_period": "072025",
            "return_type": "GSTR-1",
            "filing_status": "filed",
            "filing_date": date(2025, 8, 11),
            "output_tax": 108000,
            "input_tax_credit": 85000,
            "net_tax_payable": 23000
        },
        {
            "filing_period": "072025",
            "return_type": "GSTR-3B",
            "filing_status": "filed",
            "filing_date": date(2025, 8, 20),
            "output_tax": 108000,
            "input_tax_credit": 85000,
            "net_tax_payable": 23000
        },
        {
            "filing_period": "082025",
            "return_type": "GSTR-1",
            "filing_status": "filed",
            "filing_date": date(2025, 9, 11),
            "output_tax": 125000,
            "input_tax_credit": 95000,
            "net_tax_payable": 30000
        },
        {
            "filing_period": "092025",
            "return_type": "GSTR-1",
            "filing_status": "pending",
            "filing_date": None,
            "output_tax": 0,
            "input_tax_credit": 0,
            "net_tax_payable": 0
        }
    ]
    
    for rec in gst_records:
        existing = db.query(GSTSummary).filter(
            GSTSummary.entity_id == entity.id,
            GSTSummary.filing_period == rec["filing_period"],
            GSTSummary.return_type == rec["return_type"]
        ).first()
        
        if not existing:
            gst = GSTSummary(
                entity_id=entity.id,
                **rec
            )
            db.add(gst)
    
    db.commit()
    print(f"✅ Created GST summary records")


def run_seed():
    """Main seeding function."""
    print("\n🌱 SmartFlow Database Seeding")
    print("=" * 50)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed in order
        entity = seed_entity(db)
        counterparties = seed_counterparties(db, entity)
        seed_ledger_from_tally(db, entity, counterparties)
        seed_invoices_from_gst(db, entity, counterparties)
        # NOTE: GST Summary model uses case_id, skipping for now
        # seed_gst_summary(db, entity)
        
        print("\n✅ Database seeding complete!")
        print(f"   Entity ID: {entity.id}")
        print(f"   GSTIN: {entity.gstin}")
        
        return entity
        
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
