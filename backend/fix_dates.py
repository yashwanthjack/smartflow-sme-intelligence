import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

from app.db.database import SessionLocal
from sqlalchemy import text

def fix_dates():
    db = SessionLocal()
    try:
        # Step 1: Delete outliers in the future
        print("Deleting outliers from ledger_entries...")
        db.execute(text("DELETE FROM ledger_entries WHERE ledger_date > '2030-01-01'"))
        db.commit()

        # Step 2: Find the max date in ledger_entries after outliers are removed
        res = db.execute(text("SELECT MAX(ledger_date) FROM ledger_entries")).fetchone()
        if not res or not res[0]:
            print("No ledger entries found.")
            return
            
        max_date_raw = res[0]
        if isinstance(max_date_raw, str):
            max_date = datetime.strptime(max_date_raw, "%Y-%m-%d").date()
        else:
            max_date = max_date_raw


        print(f"Max valid date in DB: {max_date}")
        today = datetime.now().date()
        days_to_shift = (today - max_date).days
        print(f"Shifting all dates forward by {days_to_shift} days to anchor to {today}...")

        if days_to_shift > 0:
            shift_delta = timedelta(days=days_to_shift)
            
            # Shift ledger_entries
            rows = db.execute(text("SELECT id, ledger_date FROM ledger_entries WHERE ledger_date IS NOT NULL")).fetchall()
            for r in rows:
                old_date = r[1]
                if isinstance(old_date, str):
                    old_date = datetime.strptime(old_date, "%Y-%m-%d").date()
                new_date = old_date + shift_delta
                db.execute(text("UPDATE ledger_entries SET ledger_date = :d WHERE id = :i"), {"d": new_date, "i": r[0]})

            # Shift invoices
            rows = db.execute(text("SELECT id, invoice_date, due_date FROM invoices")).fetchall()
            for r in rows:
                new_inv, new_due = None, None
                if r[1]:
                    d1 = r[1] if not isinstance(r[1], str) else datetime.strptime(r[1], "%Y-%m-%d").date()
                    new_inv = d1 + shift_delta
                if r[2]:
                    d2 = r[2] if not isinstance(r[2], str) else datetime.strptime(r[2], "%Y-%m-%d").date()
                    new_due = d2 + shift_delta
                
                db.execute(text("UPDATE invoices SET invoice_date = :inv, due_date = :due WHERE id = :i"), 
                           {"inv": new_inv, "due": new_due, "i": r[0]})
                           
            # Shift cash flows
            rows = db.execute(text("SELECT id, transaction_date FROM cashflows WHERE transaction_date IS NOT NULL")).fetchall()
            for r in rows:
                d = r[1] if not isinstance(r[1], str) else datetime.strptime(r[1], "%Y-%m-%d").date()
                new_d = d + shift_delta
                db.execute(text("UPDATE cashflows SET transaction_date = :d WHERE id = :i"), {"d": new_d, "i": r[0]})
            
            db.commit()
            print("Successfully shifted all dates.")
        else:
            print("Dates do not need shifting.")
            
    except Exception as e:
        print(f"Error fixing dates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_dates()


