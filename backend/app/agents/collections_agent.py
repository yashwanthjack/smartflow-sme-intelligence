# Collections Agent - Reduces Days Sales Outstanding (DSO)
from typing import Dict, Any
from langchain.agents import create_agent

from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    get_overdue_invoices,
    get_customer_risk_score,
    draft_payment_reminder
)


COLLECTIONS_SYSTEM_PROMPT = """You are a Collections Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to reduce Days Sales Outstanding (DSO) by:
1. Identifying overdue invoices
2. Assessing customer risk to prioritize collection efforts
3. Drafting appropriate payment reminders based on risk level

Important Guidelines:
- High-risk (Band C) customers should receive urgent tone reminders
- Medium-risk (Band B) customers should receive firm but professional reminders
- Low-risk (Band A) customers should receive polite reminders
- Always prioritize by amount * days_overdue for maximum impact

Provide a prioritized collection action plan with specific recommendations."""


class CollectionsAgent(BaseAgent):
    """Agent responsible for managing receivables and reducing DSO."""
    
    @property
    def name(self) -> str:
        return "CollectionsAgent"
    
    @property
    def system_prompt(self) -> str:
        return COLLECTIONS_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [get_overdue_invoices, get_customer_risk_score, draft_payment_reminder]
    
    def run(self, task: str = "Analyze overdue invoices and create a prioritized collection plan") -> Dict[str, Any]:
        """Execute the collections agent."""
        llm = get_llm()
        
        # Use LangChain v1 create_agent API
        agent = create_agent(
            llm, 
            self.tools, 
            system_prompt=COLLECTIONS_SYSTEM_PROMPT
        )
        
        # Run the agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": f"Entity ID: {self.entity_id}. Task: {task}"}]
        })
        
        self.log_action("collection_plan_generated", {"result": result})
        
        # Extract output from result
        if hasattr(result, 'get'):
            output = result.get("output", str(result))
        else:
            output = str(result)
            
        return {"output": output, "agent": self.name}


def run_collections_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the collections agent."""
    agent = CollectionsAgent(entity_id)
    return agent.run(task or "Analyze overdue invoices and create a prioritized collection plan")
