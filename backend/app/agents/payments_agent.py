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
    query_ledger_entries
)


PAYMENTS_SYSTEM_PROMPT = """You are a Payments Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to optimize Days Payable Outstanding (DPO) by:
4. **Historical Analysis**: Use `get_highest_transaction` or `query_ledger_entries` to answer factual questions about past transactions. DO NOT GUESS amounts.
5. Scheduling payments using schedule_payment to maximize cash retention while maintaining vendor relationships

Important Constraints:
- ALWAYS maintain minimum cash balance of ₹50,000
- Critical vendors MUST be paid within 3 days of due date
- Low priority payments can be delayed if cash is tight
- If asked about "highest" or "biggest" transactions, ALWAYS use `get_highest_transaction`.

WORKFLOW:
1. First, call get_pending_payables with entity_id to see all bills due
2. Call get_cash_forecast with entity_id to understand cash position
3. Use `get_highest_transaction` or `query_ledger_entries` for historical queries
4. Create an optimized payment schedule with dates and reasoning
5. For approved payments, use schedule_payment to queue them"""


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
        return [get_cash_forecast, get_pending_payables, schedule_payment, add_ledger_transaction, analyze_ledger_spending, get_highest_transaction, query_ledger_entries]
    
    async def run(self, task: str = "Create an optimized payment schedule for the next 30 days") -> Dict[str, Any]:
        """Execute the payments agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_payments_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the payments agent."""
    agent = PaymentsAgent(entity_id)
    return await agent.run(task or "Create an optimized payment schedule for the next 30 days")
