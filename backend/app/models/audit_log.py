# AuditLog model - decision audit trail
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)

    # ---- Actor Info ----
    agent_name = Column(String, nullable=False)
    event_type = Column(String, default="SYSTEM")  
    # SYSTEM | HUMAN | HYBRID

    user_id = Column(String)  
    # Who triggered / approved (if human)

    # ---- Action Info ----
    action = Column(String, nullable=False)
    severity = Column(String, default="INFO")  
    # INFO | WARNING | CRITICAL

    # ---- Target Entity ----
    entity_type = Column(String)

    # ---- Decision Context ----
    details = Column(JSON)  
    # JSON snapshot at time of decision
    reasoning = Column(Text)  
    # Human-readable explanation

    trace_id = Column(String)  
    # Correlates multi-step agent actions

    # ---- Audit ----
    created_at = Column(DateTime, default=datetime.utcnow)