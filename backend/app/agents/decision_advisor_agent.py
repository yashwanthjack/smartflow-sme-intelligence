from typing import Dict, Any, List

from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.services.forecasting_service import ForecastingService
from app.db.database import SessionLocal
from app.models.ledger_entry import LedgerEntry
from sqlalchemy import func
from datetime import date, timedelta
from app.agents.tools import add_ledger_transaction

# --- System Prompt ---
DECISION_ADVISOR_SYSTEM_PROMPT = """You are the 'Fractional CFO' AI for an Indian SME. 
Your goal is to help the founder make strategic financial decisions (Hiring, Investing, Cost Cutting).

You have access to the company's real-time financials:
- Current Cash Balance
- Monthly Burn Rate
- Runway (Months left)

**Guidelines:**
1. **Conservative & Safety-First**: If runway < 6 months, advise caution against new massive expenses.
2. **Context-Aware**: If they ask "Can I hire?", calculate the new burn and new runway.
3. **Actionable**: Don't just say "maybe". Say "Yes, if you can increase revenue by X" or "No, it drops runway to 2 months."
4. **Indian SME Context**: Mention GST compliance or cyclicality if relevant.

**When user asks about "Hiring" or "Investing":**
- approximate the monthly cost (e.g., Junior Dev ~40k/mo, Senior ~1L/mo).
- subtract this from current cash flow projections.
- tell them the *New Runway*.
"""

# --- Tools ---

def get_financial_context(entity_id: str) -> Dict[str, float]:
    """Get current burn, cash, runway."""
    db = SessionLocal()
    try:
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        
        cash = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.entity_id == entity_id).scalar() or 0
        expenses = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id, 
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= six_months_ago
        ).scalar() or 0
        
        avg_burn = (abs(expenses) / 6) if expenses else 0
        runway = (cash / avg_burn) if avg_burn > 0 else 999
        
        return {
            "cash_balance": cash,
            "monthly_burn_rate": avg_burn,
            "runway_months": runway
        }
    finally:
        db.close()

def simulate_expense(entity_id: str, monthly_cost: float, one_time_cost: float = 0) -> str:
    """Simulates impact of a new expense on runway."""
    context = get_financial_context(entity_id)
    current_cash = context["cash_balance"] - one_time_cost
    current_burn = context["monthly_burn_rate"]
    new_burn = current_burn + monthly_cost
    
    new_runway = (current_cash / new_burn) if new_burn > 0 else 0
    
    return f"""
    Simulation Results:
    - Current Burn: ₹{current_burn:,.2f} -> New Burn: ₹{new_burn:,.2f}
    - Current Runway: {context['runway_months']:.1f} months -> New Runway: {new_runway:.1f} months
    """

class DecisionAdvisorAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "DecisionAdvisorAgent"
    
    @property
    def system_prompt(self) -> str:
        return DECISION_ADVISOR_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [get_financial_context, simulate_expense, add_ledger_transaction]

    def run(self, task: str) -> Dict[str, Any]:
        llm = get_llm()
        
        # 1. Gather Context Manually (RAG-lite)
        context = get_financial_context(self.entity_id)
        context_str = f"Current Financials: Cash=₹{context['cash_balance']:.2f}, Burn=₹{context['monthly_burn_rate']:.2f}/mo, Runway={context['runway_months']:.1f} months."
        
        # 2. Use New Agent API
        from langchain.agents import create_agent
        
        # Inject context into system prompt if possible, or just append to user message
        
        combined_prompt = f"""{self.system_prompt}

FINANCIAL CONTEXT:
{context_str}
"""

        agent = create_agent(
            model=llm, 
            tools=self.tools, 
            system_prompt=combined_prompt
        )
        
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": task}]})
            if isinstance(result, dict) and "messages" in result:
                 last_msg = result["messages"][-1]
                 output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            else:
                 output = str(result)
        except Exception as e:
            output = f"Agent Error: {str(e)}"
        
        self.log_action("decision_advice", {"task": task, "response": output})
        return {"output": output, "agent": self.name}
