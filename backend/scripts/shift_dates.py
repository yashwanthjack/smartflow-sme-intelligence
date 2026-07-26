from app.db.database import SessionLocal
from app.models.ledger_entry import LedgerEntry
from datetime import datetime, timedelta

db = SessionLocal()
entity_id = 'c081546d-d064-4aa7-8df6-655785e488c9'
entries = db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).order_by(LedgerEntry.ledger_date.desc()).all()

if not entries:
    print("No entries found!")
else:
    # Find the maximum valid date (ignoring 2368 outliers)
    valid_entries = [e for e in entries if e.ledger_date.year < 2100]
    
    if not valid_entries:
        max_date = entries[0].ledger_date
    else:
        max_date = valid_entries[0].ledger_date
        
    print(f'Original max date (valid): {max_date}')
    
    today = datetime.now().date()
    # Let's shift the max valid date to be 'today'
    delta = today - max_date
    
    print(f'Shifting {len(entries)} entries by {delta.days} days')
    
    for e in entries:
        if e.ledger_date.year > 2100:
            # Fix severe outliers from csv bugs to just be 1 day ago
            e.ledger_date = today - timedelta(days=1)
        else:
            e.ledger_date = e.ledger_date + delta
            
    db.commit()
    print('Done shifting dates!')
