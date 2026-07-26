import asyncio
import uuid
from datetime import date, timedelta
from app.db.database import SessionLocal
from app.models.entity import Entity
from app.models.ledger_entry import LedgerEntry
from app.services.agent_workforce import AgentWorkforceService
from app.models.audit_log import AuditLog

async def run_test():
    db = SessionLocal()
    try:
        # Get entity
        entity = db.query(Entity).first()
        if not entity:
            print("No entity found.")
            return

        print(f"Testing for Entity: {entity.name} ({entity.id})")
        
        # 1. Insert a normal average baseline
        for i in range(5):
            entry = LedgerEntry(
                id=str(uuid.uuid4()),
                entity_id=entity.id,
                amount=-1000.0,
                ledger_date=date.today() - timedelta(days=10),
                description="Regular Expense"
            )
            db.add(entry)
            
        # 2. Insert a massive anomalous transaction specifically yesterday
        huge_amount = -150000.0  # Must be >3x avg and >50,000 threshold
        anomaly = LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            amount=huge_amount,
            ledger_date=date.today() - timedelta(days=1),
            description="UNEXPECTED MASSIVE WITHDRAWAL"
        )
        db.add(anomaly)
        db.commit()

        print(f"Inserted baseline and anomaly ({huge_amount}) into Ledger.")

        # 3. Clear old test logs to isolate
        db.query(AuditLog).filter(AuditLog.agent_name == "CashFlowGuard", AuditLog.action == "ANOMALOUS_TRANSACTION").delete()
        db.commit()

        # 4. Trigger Workforce Service
        print("Triggering AgentWorkforceService...")
        svc = AgentWorkforceService(db)
        await svc.run_background_cycle(entity.id)
        
        # 5. Check if log was created
        logs = db.query(AuditLog).filter(
            AuditLog.entity_id == entity.id,
            AuditLog.agent_name == "CashFlowGuard",
            AuditLog.action == "ANOMALOUS_TRANSACTION"
        ).all()
        
        if logs:
            print(f"✅ SUCCESS: Anomaly detected! {len(logs)} log(s) found.")
            for log in logs:
                print(f"   Log: {log.severity} | {log.reasoning}")
        else:
            print("❌ FAILED: No anomaly detected.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
