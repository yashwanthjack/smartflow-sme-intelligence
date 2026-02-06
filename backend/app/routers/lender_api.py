from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import secrets
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.models.entity import Entity
from app.models.user import User
from app.auth import get_current_active_user
from app.routers.data import get_dashboard_kpis

# We reuse the KPI logic but packaged for public consumption
# Ideally we'd move the logic to a service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Temporary in-memory store for tokens (Use Redis/DB in prod)
# Format: { "token": { "entity_id": "...", "expires": datetime } }
LENDER_TOKENS = {}

@router.post("/access-token")
async def generate_lender_token(
    current_user: User = Depends(get_current_active_user),
    valid_hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Generate a temporary, shareable link/token for a lender.
    User must own the entity.
    """
    if not current_user.entity_id:
        raise HTTPException(status_code=400, detail="User has no entity")
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=valid_hours)
    
    LENDER_TOKENS[token] = {
        "entity_id": current_user.entity_id,
        "expires": expires
    }
    
    # Also ensure public profile is enabled? 
    # For now, we assume the token grants specific access regardless of public flag
    
    return {
        "share_token": token,
        "expires_at": expires,
        "share_url": f"/lender/view/{token}" # Frontend route
    }

@router.get("/report/{share_token}")
async def get_lender_report(share_token: str, db: Session = Depends(get_db)):
    """
    Public (token-protected) endpoint for lenders.
    Returns sanitized financial health report.
    """
    token_data = LENDER_TOKENS.get(share_token)
    if not token_data:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
        
    if datetime.now() > token_data["expires"]:
        del LENDER_TOKENS[share_token]
        raise HTTPException(status_code=403, detail="Token expired")
        
    entity_id = token_data["entity_id"]
    
    # reuse dashboard KPIs logic
    # In a real app, refactor logic to a service function: `get_entity_kpis(entity_id, db)`
    # Here we mock calling the router function or just implementing the logic again
    # Simplest: Copy logic (MVP style)
    
    # Fetch Entity
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    
    # Fetch KPIs (Simplified)
    kpis = await get_dashboard_kpis(entity_id, db) 
    
    return {
        "entity_name": entity.name,
        "industry": entity.industry,
        "report_generated_at": datetime.now(),
        "financials": kpis["financials"],
        "credit_score": kpis["credit"],
        "risk_assessment": {
            "summary": "This entity shows strong growth but moderate burn.",
            "flags": [] 
        }
    }
