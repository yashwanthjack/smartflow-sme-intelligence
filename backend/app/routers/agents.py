# Agent API Router
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.agents.collections_agent import run_collections_agent
from app.agents.payments_agent import run_payments_agent
from app.agents.gst_agent import run_gst_agent
from app.agents.credit_advisory_agent import run_credit_advisory_agent
from app.agents.supervisor_agent import run_supervisor, run_full_analysis, classify_intent

router = APIRouter()


class AgentRequest(BaseModel):
    task: Optional[str] = None


class AgentResponse(BaseModel):
    agent: str
    entity_id: str
    output: str
    success: bool


@router.post("/collections/{entity_id}", response_model=AgentResponse)
async def run_collections(entity_id: str, request: AgentRequest = None):
    """Run the Collections Agent to analyze overdue invoices and create collection plans."""
    try:
        task = request.task if request else None
        result = run_collections_agent(entity_id, task)
        return AgentResponse(
            agent="CollectionsAgent",
            entity_id=entity_id,
            output=result.get("output", str(result)),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/{entity_id}", response_model=AgentResponse)
async def run_payments(entity_id: str, request: AgentRequest = None):
    """Run the Payments Agent to create optimized payment schedules."""
    try:
        task = request.task if request else None
        result = run_payments_agent(entity_id, task)
        return AgentResponse(
            agent="PaymentsAgent",
            entity_id=entity_id,
            output=result.get("output", str(result)),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gst/{entity_id}", response_model=AgentResponse)
async def run_gst(entity_id: str, request: AgentRequest = None):
    """Run the GST Agent to check compliance and reconciliation."""
    try:
        task = request.task if request else None
        result = run_gst_agent(entity_id, task)
        return AgentResponse(
            agent="GSTAgent",
            entity_id=entity_id,
            output=result.get("output", str(result)),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit-advisory/{entity_id}", response_model=AgentResponse)
async def run_credit_advisory(entity_id: str, request: AgentRequest = None):
    """Run the Credit Advisory Agent for financial health assessment."""
    try:
        task = request.task if request else None
        result = run_credit_advisory_agent(entity_id, task)
        return AgentResponse(
            agent="CreditAdvisoryAgent",
            entity_id=entity_id,
            output=result.get("output", str(result)),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_agents():
    """List all available agents and their descriptions."""
    return {
        "agents": [
            {
                "name": "CollectionsAgent",
                "endpoint": "/api/agents/collections/{entity_id}",
                "description": "Reduces Days Sales Outstanding (DSO) by managing receivables"
            },
            {
                "name": "PaymentsAgent", 
                "endpoint": "/api/agents/payments/{entity_id}",
                "description": "Optimizes Days Payable Outstanding (DPO) by scheduling payments"
            },
            {
                "name": "GSTAgent",
                "endpoint": "/api/agents/gst/{entity_id}",
                "description": "Monitors GST compliance and reconciliation"
            },
            {
                "name": "CreditAdvisoryAgent",
                "endpoint": "/api/agents/credit-advisory/{entity_id}",
                "description": "Provides CFO-level financial guidance and recommendations"
            },
            {
                "name": "SupervisorAgent",
                "endpoint": "/api/agents/query/{entity_id}",
                "description": "Unified endpoint that routes queries to the appropriate agent automatically"
            }
        ]
    }


class QueryRequest(BaseModel):
    query: str


class SupervisorResponse(BaseModel):
    agent_used: str
    intent: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    fallback_output: Optional[str] = None


@router.post("/query/{entity_id}", response_model=SupervisorResponse)
async def query_supervisor(entity_id: str, request: QueryRequest):
    """
    Unified query endpoint - automatically routes to the best agent.
    The supervisor classifies your query and delegates to Collections, Payments, GST, or Credit agents.
    """
    try:
        result = run_supervisor(entity_id, request.query)
        return SupervisorResponse(**result)
    except Exception as e:
        return SupervisorResponse(
            agent_used="supervisor",
            intent="error",
            success=False,
            error=str(e)
        )


@router.post("/full-analysis/{entity_id}")
async def full_analysis(entity_id: str):
    """
    Run comprehensive analysis using all agents.
    Returns insights on collections, payments, GST, and credit all at once.
    """
    try:
        result = run_full_analysis(entity_id)
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-intent")
async def classify_query_intent(request: QueryRequest):
    """
    Classify a query to see which agent would handle it.
    Useful for frontend to show appropriate UI before running agent.
    """
    intent = classify_intent(request.query)
    return {
        "query": request.query,
        "classified_intent": intent,
        "recommended_agent": f"{intent.title()}Agent"
    }

