# Ingestion service - handles file uploads
from sqlalchemy.orm import Session
from typing import Dict, List
from dateutil import parser as date_parser
from app.models.ledger_entry import LedgerEntry
from app.models.entity import Entity
from app.models.gst_summary import GSTSummary
from app.parsers.bank_parser import BankParser
from app.parsers.ledger_parser import LedgerParser
from app.parsers.gst_parser import GSTParser
class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.bank_parser = BankParser()
        self.ledger_parser = LedgerParser()
        self.gst_parser = GSTParser()
    def ingest_bank_statement(self, file_path: str, entity_id: str):
        """
        1. Parse the bank file
        2. Convert each row to a LedgerEntry
        3. Save to database
        """
        # Step 1: Parse
        transactions = self.bank_parser.parse(file_path)
        print(f"Parsed {len(transactions)} transactions")
        
        # Step 2: Save loop (we will write this next)
        for txn in transactions:
            pass  # placeholder

    def ingest_ledger(self, file_path: str, entity_id: str):
        """Parse Tally/Zoho ledger and save to DB."""
        entries = self.ledger_parser.parse(file_path)
        print(f"Parsed {len(entries)} ledger entries")
        
        saved_count = 0
        for row in entries:
            try:
                txn_date = date_parser.parse(row['date'], dayfirst=True).date()
                
                # Determine amount (+ve for receipt, -ve for payment)
                amt = 0
                if row['credit'] > 0:
                    amt = row['credit']  # Money IN (Revenue)
                elif row['debit'] > 0:
                    amt = -row['debit']  # Money OUT (Expense)
                
                if amt == 0: continue
                
                entry = LedgerEntry(
                    entity_id=entity_id,
                    ledger_date=txn_date,
                    amount=amt,
                    description=row['particulars'],
                    source_type='tally',
                    source_record_id=row.get('voucher_no'),
                    category=row.get('voucher_type', 'uncategorized')
                )
                
                self.db.add(entry)
                saved_count += 1
            except Exception as e:
                print(f"Skipping ledger row: {e}")
        
        self.db.commit()
        print(f"Saved {saved_count} ledger entries!")
        return saved_count
    def ingest_gst(self, file_path: str, entity_id: str):
        """Parse GST file and save to DB."""
        data = self.gst_parser.parse(file_path)
        if data['type'] == 'GSTR-3B':
            # Calculate dummy period dates if not available
            p_start = date_parser.parse(f"01-{data['period'][:2]}-{data['period'][2:]}").date()
            p_end = p_start  # Simplified

            summary = GSTSummary(
                case_id=entity_id,  # Map entity_id to case_id
                return_type='GSTR-3B',
                period=data['period'],
                period_start=p_start,
                period_end=p_end,
                turnover=data['outward_taxable'],
                output_tax=data['output_tax'],
                input_credit=data['itc_available'],
                tax_paid=0
            )
            self.db.add(summary)
            self.db.commit()
            print("Saved GSTR-3B summary")
            return 1
        return 0