# Playbook Runner — Executes multi-step playbooks through the LangGraph supervisor
# Each step is sent as a separate query to the agent orchestrator

from typing import Dict, Any, List
from datetime import datetime

from app.db.database import SessionLocal
from app.models.playbook import Playbook, PlaybookRun
from app.agents.langgraph_supervisor import run_langgraph_supervisor


async def run_playbook(playbook_id: str, entity_id: str) -> Dict[str, Any]:
    """
    Execute a playbook step-by-step.
    
    Each step's instruction is sent to the LangGraph supervisor.
    Results are collected into a PlaybookRun record.
    """
    db = SessionLocal()
    
    try:
        # Load the playbook
        playbook = db.query(Playbook).filter(
            Playbook.id == playbook_id,
            Playbook.entity_id == entity_id
        ).first()
        
        if not playbook:
            return {"success": False, "error": "Playbook not found"}
        
        steps = playbook.steps or []
        if not steps:
            return {"success": False, "error": "Playbook has no steps"}
        
        # Create a run record
        run = PlaybookRun(
            playbook_id=playbook_id,
            entity_id=entity_id,
            status="running",
            step_results=[]
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        
        # Execute each step sequentially
        step_results = []
        all_success = True
        
        for step in sorted(steps, key=lambda s: s.get("order", 0)):
            instruction = step.get("instruction", "")
            step_order = step.get("order", 0)
            agent_hint = step.get("agent_hint", None)
            
            if not instruction:
                step_results.append({
                    "step": step_order,
                    "instruction": "(empty)",
                    "output": "Skipped — no instruction provided",
                    "success": False
                })
                continue
            
            try:
                # Prepend agent hint context if provided
                query = instruction
                if agent_hint:
                    query = f"[Route to {agent_hint}] {instruction}"
                
                # Send to the LangGraph supervisor
                result = await run_langgraph_supervisor(entity_id, query)
                
                output = result.get("output", str(result))
                success = result.get("success", False)
                
                step_results.append({
                    "step": step_order,
                    "instruction": instruction,
                    "agent_hint": agent_hint,
                    "agent_used": result.get("agent_used", "unknown"),
                    "output": output,
                    "success": success
                })
                
                if not success:
                    all_success = False
                    
            except Exception as e:
                step_results.append({
                    "step": step_order,
                    "instruction": instruction,
                    "output": f"Error: {str(e)}",
                    "success": False
                })
                all_success = False
        
        # Update the run record
        run.step_results = step_results
        run.status = "completed" if all_success else "failed"
        run.completed_at = datetime.utcnow()
        
        # Update playbook's last_run_at
        playbook.last_run_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "run_id": run.id,
            "status": run.status,
            "step_count": len(steps),
            "steps_succeeded": sum(1 for s in step_results if s.get("success")),
            "step_results": step_results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# Pre-built playbook templates
BUILT_IN_TEMPLATES = [
    {
        "name": "End of Month Close",
        "description": "Monthly financial reconciliation and health check",
        "steps": [
            {"order": 1, "instruction": "Check GST compliance status and any pending filings", "agent_hint": "GSTAgent"},
            {"order": 2, "instruction": "List all overdue invoices and suggest collection actions", "agent_hint": "CollectionsAgent"},
            {"order": 3, "instruction": "Generate a cash runway report for the next 3 months", "agent_hint": "CreditAdvisoryAgent"},
        ]
    },
    {
        "name": "Weekly Cash Pulse",
        "description": "Quick weekly cash position and risk summary",
        "steps": [
            {"order": 1, "instruction": "Get cash flow forecast for the next 30 days", "agent_hint": "PaymentsAgent"},
            {"order": 2, "instruction": "List all pending vendor payables due this week", "agent_hint": "PaymentsAgent"},
            {"order": 3, "instruction": "Summarize the top financial risks right now", "agent_hint": "CreditAdvisoryAgent"},
        ]
    },
    {
        "name": "Investor Readiness Check",
        "description": "Comprehensive financial health assessment for investor meetings",
        "steps": [
            {"order": 1, "instruction": "Calculate our current credit score and risk band", "agent_hint": "CreditAdvisoryAgent"},
            {"order": 2, "instruction": "Provide a full financial health assessment including revenue trends", "agent_hint": "DecisionAdvisorAgent"},
            {"order": 3, "instruction": "Generate a 6-month revenue and cash flow forecast", "agent_hint": "PaymentsAgent"},
        ]
    },
]


def seed_playbook_templates(entity_id: str):
    """Create built-in playbook templates for a new entity (if they don't exist)."""
    db = SessionLocal()
    try:
        existing = db.query(Playbook).filter(
            Playbook.entity_id == entity_id,
            Playbook.is_template == True
        ).count()
        
        if existing > 0:
            return  # Templates already seeded
        
        for tmpl in BUILT_IN_TEMPLATES:
            pb = Playbook(
                entity_id=entity_id,
                name=tmpl["name"],
                description=tmpl["description"],
                steps=tmpl["steps"],
                is_template=True,
                is_active=True,
            )
            db.add(pb)
        
        db.commit()
        print(f"✅ Seeded {len(BUILT_IN_TEMPLATES)} playbook templates for entity {entity_id}")
    except Exception as e:
        print(f"Failed to seed playbook templates: {e}")
    finally:
        db.close()
