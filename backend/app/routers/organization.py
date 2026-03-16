from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.auth import get_current_active_user

router = APIRouter()

class OrgUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

@router.get("/")
def get_my_organization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of the user's organization."""
    if not current_user.entity_id:
        raise HTTPException(status_code=404, detail="User is not linked to any organization")
    
    entity = db.query(Entity).filter(Entity.id == current_user.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return entity

@router.put("/")
def update_organization(
    org_update: OrgUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update organization details. Any authenticated user can update their linked org."""
        
    if not current_user.entity_id:
        raise HTTPException(status_code=404, detail="User is not linked to any organization")

    entity = db.query(Entity).filter(Entity.id == current_user.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org_update.name is not None:
        entity.name = org_update.name
    if org_update.gstin is not None:
        entity.gstin = org_update.gstin
    if org_update.industry is not None:
        entity.industry = org_update.industry
    if org_update.city is not None:
        entity.city = org_update.city
    if org_update.state is not None:
        entity.state = org_update.state

    db.commit()
    db.refresh(entity)
    return entity
