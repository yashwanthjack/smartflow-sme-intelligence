# Playbook CRUD + Execution Router
# Manage and run multi-step agent workflows

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.models.playbook import Playbook, PlaybookRun

router = APIRouter(tags=["Playbooks"])


# ---- Schemas ----

class PlaybookStep(BaseModel):
    order: int
    instruction: str
    agent_hint: Optional[str] = None


class PlaybookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[PlaybookStep]


class PlaybookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[PlaybookStep]] = None
    is_active: Optional[bool] = None


class PlaybookResponse(BaseModel):
    id: str
    entity_id: str
    name: str
    description: Optional[str] = None
    steps: List[Any]
    is_active: bool
    is_template: bool
    created_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RunResponse(BaseModel):
    id: str
    playbook_id: str
    status: str
    step_results: List[Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Endpoints ----

@router.get("/{entity_id}", response_model=List[PlaybookResponse])
async def list_playbooks(
    entity_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all playbooks for an entity."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Seed templates on first access
    from app.agents.playbook_runner import seed_playbook_templates
    seed_playbook_templates(entity_id)

    playbooks = (
        db.query(Playbook)
        .filter(Playbook.entity_id == entity_id)
        .order_by(Playbook.created_at.desc())
        .all()
    )
    return [PlaybookResponse.model_validate(pb) for pb in playbooks]


@router.post("/{entity_id}", response_model=PlaybookResponse)
async def create_playbook(
    entity_id: str,
    payload: PlaybookCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new custom playbook."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    pb = Playbook(
        entity_id=entity_id,
        name=payload.name,
        description=payload.description,
        steps=[s.model_dump() for s in payload.steps],
        is_template=False,
        is_active=True,
    )
    db.add(pb)
    db.commit()
    db.refresh(pb)
    return PlaybookResponse.model_validate(pb)


@router.put("/{entity_id}/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    entity_id: str,
    playbook_id: str,
    payload: PlaybookUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an existing playbook."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    pb = db.query(Playbook).filter(
        Playbook.id == playbook_id,
        Playbook.entity_id == entity_id
    ).first()
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")

    if payload.name is not None:
        pb.name = payload.name
    if payload.description is not None:
        pb.description = payload.description
    if payload.steps is not None:
        pb.steps = [s.model_dump() for s in payload.steps]
    if payload.is_active is not None:
        pb.is_active = payload.is_active

    db.commit()
    db.refresh(pb)
    return PlaybookResponse.model_validate(pb)


@router.delete("/{entity_id}/{playbook_id}")
async def delete_playbook(
    entity_id: str,
    playbook_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a playbook."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    pb = db.query(Playbook).filter(
        Playbook.id == playbook_id,
        Playbook.entity_id == entity_id
    ).first()
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")

    db.delete(pb)
    db.commit()
    return {"detail": "Playbook deleted", "id": playbook_id}


@router.post("/{entity_id}/{playbook_id}/run")
async def execute_playbook(
    entity_id: str,
    playbook_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Execute a playbook now — runs all steps through the agent supervisor."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    from app.agents.playbook_runner import run_playbook
    result = await run_playbook(playbook_id, entity_id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Execution failed"))

    return result


@router.get("/{entity_id}/{playbook_id}/runs", response_model=List[RunResponse])
async def list_runs(
    entity_id: str,
    playbook_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List past runs for a playbook."""
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    runs = (
        db.query(PlaybookRun)
        .filter(
            PlaybookRun.playbook_id == playbook_id,
            PlaybookRun.entity_id == entity_id
        )
        .order_by(PlaybookRun.started_at.desc())
        .limit(20)
        .all()
    )
    return [RunResponse.model_validate(r) for r in runs]
