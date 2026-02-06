from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.auth import get_current_active_user
from app.models.user import User
from app.agents.decision_advisor_agent import DecisionAdvisorAgent

router = APIRouter()

class DecisionRequest(BaseModel):
    question: str

class InsightResponse(BaseModel):
    summary: str
    action_items: List[str]

@router.get("/{entity_id}/summary")
async def get_financial_summary(
    entity_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a concise AI-generated summary of the entity's financial health.
    Uses DecisionAdvisorAgent in 'summary' mode.
    """
    # Security check: ensure user belongs to entity
    if current_user.entity_id != entity_id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Unauthorized access to entity data")

    agent = DecisionAdvisorAgent(entity_id)
    # We ask a specific prompt for summary
    result = agent.run("Give me a 3-bullet point executive summary of my financial health and 1 key risk.")
    
    return {
        "summary": result["output"],
        "timestamp": "now" # In real app, consider caching
    }

@router.post("/decision/{entity_id}")
async def ask_decision_advisor(
    entity_id: str,
    request: DecisionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Ask the 'Fractional CFO' a strategic question.
    e.g. 'Should I hire multiple devs?'
    """
    if current_user.entity_id != entity_id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Unauthorized access")

    agent = DecisionAdvisorAgent(entity_id)
    result = agent.run(request.question)
    
    return {
        "answer": result["output"],
        "agent": "DecisionAdvisor"
    }
