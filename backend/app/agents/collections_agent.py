# Collections Agent - Reduces Days Sales Outstanding (DSO)
# Autonomous tool-calling agent powered by LangChain
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.tools import (
    get_overdue_invoices,
    get_customer_risk_score,
    draft_payment_reminder,
    update_invoice_status
)


COLLECTIONS_SYSTEM_PROMPT = """You are a Collections Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to reduce Days Sales Outstanding (DSO) by:
1. Identifying overdue invoices using the get_overdue_invoices tool
2. Assessing customer risk using get_customer_risk_score to prioritize collection efforts
3. Drafting appropriate payment reminders using draft_payment_reminder based on risk level

Important Guidelines:
- High-risk (Band C) customers should receive urgent tone reminders
- Medium-risk (Band B) customers should receive firm but professional reminders
- Low-risk (Band A) customers should receive polite reminders
- Always prioritize by amount * days_overdue for maximum impact

WORKFLOW:
1. First, call get_overdue_invoices with the entity_id to see all pending receivables
2. For each significant overdue invoice, call get_customer_risk_score with the customer name
3. Based on risk band, draft a reminder using draft_payment_reminder with the appropriate tone
4. Provide a prioritized collection action plan with specific recommendations"""


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
        return [get_overdue_invoices, get_customer_risk_score, draft_payment_reminder, update_invoice_status]
    
    async def run(self, task: str = "Analyze overdue invoices and create a prioritized collection plan") -> Dict[str, Any]:
        """Execute the collections agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_collections_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the collections agent."""
    agent = CollectionsAgent(entity_id)
    return await agent.run(task or "Analyze overdue invoices and create a prioritized collection plan")
