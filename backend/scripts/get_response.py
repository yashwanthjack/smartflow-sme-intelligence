import json
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog

db = SessionLocal()
log = db.query(AuditLog).filter(
    AuditLog.agent_name=='SupervisorAgent',
    AuditLog.action=='MULTI_AGENT_SYNTHESIS'
).order_by(AuditLog.created_at.desc()).first()

if log:
    if isinstance(log.details, str):
        try:
            data = json.loads(log.details)
        except Exception:
            data = {"output": log.details}
    print("\n--- AGENT RESPONSE ---\n")
    print(data.get('query_or_output', data.get('output', str(data))))
db.close()
