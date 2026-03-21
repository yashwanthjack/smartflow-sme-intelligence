# Decision Advisor Agent - Fractional CFO for strategic decisions
# Autonomous tool-calling agent powered by LangChain
from typing import Dict, Any
from langchain.tools import tool

from app.agents.base_agent import BaseAgent
from app.agents.tools import add_ledger_transaction


# ---- Tools specific to this agent ----

@tool
def get_financial_context(entity_id: str) -> str:
    """Get current cash balance, monthly burn rate, and runway for the entity.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Financial context with cash, burn rate, and runway
    """
    from app.db.database import SessionLocal
    from app.models.ledger_entry import LedgerEntry
    from sqlalchemy import func
    from datetime import date, timedelta
    
    db = SessionLocal()
    try:
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        
        cash = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id
        ).scalar() or 0
        
        expenses = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id, 
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= six_months_ago
        ).scalar() or 0
        
        avg_burn = (abs(expenses) / 6) if expenses else 0
        runway = (cash / avg_burn) if avg_burn > 0 else 999
        
        return (
            f"📊 **Financial Context**\n"
            f"- Cash Balance: ₹{cash:,.0f}\n"
            f"- Monthly Burn Rate: ₹{avg_burn:,.0f}\n"
            f"- Runway: {runway:.1f} months\n"
        )
    finally:
        db.close()


@tool
def simulate_expense(entity_id: str, monthly_cost: float, one_time_cost: float = 0) -> str:
    """Simulate the impact of a new recurring expense on cash runway.
    
    Args:
        entity_id: The unique identifier of the business entity
        monthly_cost: Monthly recurring cost of the new expense in INR
        one_time_cost: One-time upfront cost in INR (default 0)
        
    Returns:
        Simulation showing old vs new burn rate and runway
    """
    from app.db.database import SessionLocal
    from app.models.ledger_entry import LedgerEntry
    from sqlalchemy import func
    from datetime import date, timedelta
    
    db = SessionLocal()
    try:
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        
        cash = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id
        ).scalar() or 0
        
        expenses = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id,
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= six_months_ago
        ).scalar() or 0
        
        current_burn = (abs(expenses) / 6) if expenses else 0
        current_runway = (cash / current_burn) if current_burn > 0 else 999
        
        adjusted_cash = cash - one_time_cost
        new_burn = current_burn + monthly_cost
        new_runway = (adjusted_cash / new_burn) if new_burn > 0 else 0
        
        status = "✅ Safe" if new_runway >= 6 else ("⚠️ Tight" if new_runway >= 3 else "🔴 Risky")
        
        return (
            f"📊 **Expense Simulation**\n"
            f"- Current Burn: ₹{current_burn:,.0f}/mo → New Burn: ₹{new_burn:,.0f}/mo\n"
            f"- Current Runway: {current_runway:.1f} months → New Runway: {new_runway:.1f} months {status}\n"
            f"- One-time cost impact: ₹{one_time_cost:,.0f}\n"
        )
    finally:
        db.close()


DECISION_ADVISOR_SYSTEM_PROMPT = """You are the 'Fractional CFO' AI for an Indian SME. 
Your goal is to help the founder make strategic financial decisions (Hiring, Investing, Cost Cutting).

You have access to tools to check real-time financials:
- get_financial_context: Gets current cash balance, burn rate, and runway
- simulate_expense: Simulates impact of a new expense on runway
- add_ledger_transaction: Records a transaction (use only when approved)

**Guidelines:**
1. **Conservative & Safety-First**: If runway < 6 months, advise caution.
2. **Context-Aware**: If they ask "Can I hire?", use simulate_expense to calculate the impact.
3. **Actionable**: Don't just say "maybe". Give specific numbers.
4. **Indian SME Context**: Mention GST compliance or cyclicality if relevant.

WORKFLOW:
1. Call get_financial_context with entity_id to understand current position
2. If user asks about hiring/investing, call simulate_expense with estimated monthly cost
3. Provide clear recommendation with numbers: "Yes, if..." or "No, because..."
"""


class DecisionAdvisorAgent(BaseAgent):
    """Fractional CFO agent for strategic financial decisions."""
    
    @property
    def name(self) -> str:
        return "DecisionAdvisorAgent"
    
    @property
    def system_prompt(self) -> str:
        return DECISION_ADVISOR_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [get_financial_context, simulate_expense, add_ledger_transaction]

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute the decision advisor using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_decision_advisor_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the decision advisor agent."""
    agent = DecisionAdvisorAgent(entity_id)
    return await agent.run(task or "Provide a strategic financial assessment and recommendations")
