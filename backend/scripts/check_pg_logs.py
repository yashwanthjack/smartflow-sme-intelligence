import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from app.models.user import User

def main():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "yash@gmail.com").first()
    if not user:
        print("User yash@gmail.com not found in PostgreSQL DB!")
        db.close()
        return

    logs = db.query(AuditLog).filter(AuditLog.entity_id == user.entity_id).order_by(AuditLog.created_at.desc()).limit(10).all()
    print("--- LATEST POSTGRESQL AUDIT LOGS FOR YASH@GMAIL.COM ---")
    for log in reversed(logs):  # Print oldest to newest of the last 10
        print(f"[{log.created_at}] {log.agent_name} - {log.action}: {log.reasoning}")
        print(f"  > Summary: {str(log.details)[:100]}...\n")
    db.close()

if __name__ == "__main__":
    main()
