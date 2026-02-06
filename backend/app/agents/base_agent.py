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
