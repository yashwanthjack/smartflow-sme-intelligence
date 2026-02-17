import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.config import settings

def check_audit_logs():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print(f"Checking database: {settings.DATABASE_URL}")
        
        # Count logs
        result = db.execute(text("SELECT count(*) FROM audit_logs"))
        count = result.scalar()
        print(f"Total Audit Logs: {count}")
        
        # Show last 5 logs
        result = db.execute(text("SELECT id, entity_id, action, agent_name FROM audit_logs ORDER BY created_at DESC LIMIT 5"))
        rows = result.fetchall()
        
        if rows:
            print("\nLast 5 Logs:")
            for row in rows:
                print(f"- [{row.agent_name}] {row.action} (Entity: {row.entity_id})")
        else:
            print("\nNo logs found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_audit_logs()
