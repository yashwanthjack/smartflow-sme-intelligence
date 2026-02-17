from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/{entity_id}", response_model=List[dict])
async def get_audit_logs(
    entity_id: str,
    limit: int = 50,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get audit trail for an entity.
    Shows all AI decisions, actions, and alerts.
    """
    if current_user.entity_id != entity_id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Unauthorized")

    query = db.query(AuditLog).filter(AuditLog.entity_id == entity_id)
    
    if severity:
        query = query.filter(AuditLog.severity == severity)
        
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "agent": log.agent_name,
            "action": log.action,
            "severity": log.severity,
            "timestamp": log.created_at,
            "summary": log.reasoning,
            "details": log.details,
            "trace_id": log.trace_id
        }
        for log in logs
    ]
