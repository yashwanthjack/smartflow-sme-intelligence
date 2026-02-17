import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text

def drop():
    print("Dropping tables...", flush=True)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS gst_summaries CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS audit_logs CASCADE"))
        conn.commit()
    print("Dropped.", flush=True)

if __name__ == "__main__":
    drop()
