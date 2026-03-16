# Base Agent class for SmartFlow agents
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAgent(ABC):
    """Abstract base class for all SmartFlow agents."""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.actions: List[Dict[str, Any]] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging and identification."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining the agent's role and behavior."""
        pass
    
    @property
    @abstractmethod
    def tools(self) -> list:
        """List of tools available to this agent."""
        pass
    
    @abstractmethod
    def run(self, task: str) -> Dict[str, Any]:
        """Execute the agent with a specific task."""
        pass
    
    def log_action(self, action_type: str, details: Dict[str, Any]):
        """Log an action taken by the agent."""
        self.actions.append({
            "agent": self.name,
            "entity_id": self.entity_id,
            "action_type": action_type,
            "details": details
        })
        self.persist_audit_log(action_type, details)

    def persist_audit_log(self, action_type: str, details: Dict[str, Any]):
        """Write audit log to database."""
        try:
            from app.db.database import SessionLocal
            from app.models.audit_log import AuditLog
            import json
            
            db = SessionLocal()
            try:
                # Determine severity based on action
                severity = "INFO"
                if "error" in str(details).lower():
                    severity = "ERROR"
                elif "urgent" in str(details).lower() or "critical" in str(details).lower():
                    severity = "WARNING"
                
                log = AuditLog(
                    agent_name=self.name,
                    event_type="AI_AGENT",
                    action=action_type,
                    severity=severity,
                    entity_id=self.entity_id,
                    details=json.dumps(details, default=str),
                    reasoning=details.get("output", "")[:500] if isinstance(details, dict) else str(details)[:500]
                )
                db.add(log)
                db.commit()
            except Exception as e:
                print(f"Failed to persist audit log: {e}")
            finally:
                db.close()
        except ImportError:
            pass # functional even if DB not available
