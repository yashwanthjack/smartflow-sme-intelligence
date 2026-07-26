# Memory CRUD Router
# Endpoints for managing persistent agent memories

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.models.memory import Memory

router = APIRouter(tags=["Memory"])


class MemoryCreate(BaseModel):
    content: str
    category: str = Field(default="insight", description="preference | rule | insight | fact")
    importance: int = Field(default=3, ge=1, le=5)
    source_agent: str = "user"


class MemoryResponse(BaseModel):
    id: str
    entity_id: str
    category: str
    content: str
    source_agent: Optional[str] = None
    importance: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int


@router.get("/{entity_id}", response_model=MemoryListResponse)
async def list_memories(
    entity_id: str,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all memories for an entity, optionally filtered."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(Memory).filter(Memory.entity_id == entity_id)

    if category:
        query = query.filter(Memory.category == category)

    if search:
        query = query.filter(Memory.content.ilike(f"%{search}%"))

    # Order by importance desc, then most recent
    query = query.order_by(Memory.importance.desc(), Memory.created_at.desc())
    memories = query.all()

    return MemoryListResponse(
        memories=[MemoryResponse.model_validate(m) for m in memories],
        total=len(memories),
    )


@router.post("/{entity_id}", response_model=MemoryResponse)
async def create_memory(
    entity_id: str,
    payload: MemoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Manually add a memory."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    mem = Memory(
        entity_id=entity_id,
        content=payload.content,
        category=payload.category,
        importance=payload.importance,
        source_agent=payload.source_agent,
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return MemoryResponse.model_validate(mem)


@router.delete("/{entity_id}/{memory_id}")
async def delete_memory(
    entity_id: str,
    memory_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete (forget) a memory."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    mem = db.query(Memory).filter(Memory.id == memory_id, Memory.entity_id == entity_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")

    db.delete(mem)
    db.commit()
    return {"detail": "Memory deleted", "id": memory_id}
