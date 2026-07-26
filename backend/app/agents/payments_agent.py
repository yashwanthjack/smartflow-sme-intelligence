# Payments Agent - Optimizes Days Payable Outstanding (DPO)
# Autonomous tool-calling agent powered by LangChain
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.tools import (
    get_cash_forecast,
    get_pending_payables,
    schedule_payment,
    add_ledger_transaction,
    analyze_ledger_spending,
    get_highest_transaction,
    query_ledger_entries,
    get_top_spending_recipients
)


PAYMENTS_SYSTEM_PROMPT = """You are a Payments Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to handle payments, analyze historical spending, and optimize cash retention. 

GUIDELINES FOR TOOL USAGE:
- ONLY invoke tools that are directly relevant to the user's explicit question. DO NOT run a standard workflow or sequence of tools unless specifically asked to.
- For historical questions like "who paid me highest?" or "did X pay me?", skip all forecasting and payable checks, and immediately use `get_highest_received_payment`, `get_highest_transaction`, `query_ledger_entries`, or `get_top_spending_recipients`.
- ONLY call `get_cash_forecast` if the user explicitly asks for a cash forecast, runway projection, or to schedule a future payment, as forecasting is computationally heavy.
- DO NOT GUESS amounts. Use the tools.

Important Constraints:
- ALWAYS maintain minimum cash balance of ₹50,000
- Critical vendors MUST be paid within 3 days of due date
- Low priority payments can be delayed if cash is tight"""


class PaymentsAgent(BaseAgent):
    """Agent responsible for optimizing payment scheduling."""
    
    @property
    def name(self) -> str:
        return "PaymentsAgent"
    
    @property
    def system_prompt(self) -> str:
        return PAYMENTS_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        from app.agents.tools import get_highest_received_payment
        return [get_cash_forecast, get_pending_payables, schedule_payment, add_ledger_transaction, analyze_ledger_spending, get_highest_transaction, query_ledger_entries, get_top_spending_recipients, get_highest_received_payment]
    
    async def run(self, task: str = "Create an optimized payment schedule for the next 30 days") -> Dict[str, Any]:
        """Execute the payments agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_payments_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the payments agent."""
    agent = PaymentsAgent(entity_id)
    return await agent.run(task or "Create an optimized payment schedule for the next 30 days")
