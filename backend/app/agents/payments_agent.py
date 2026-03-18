# Payments Agent - Optimizes Days Payable Outstanding (DPO)
# Autonomous tool-calling agent powered by LangChain
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.tools import (
    get_cash_forecast,
    get_pending_payables,
    schedule_payment,
    add_ledger_transaction,
    analyze_ledger_spending
)


PAYMENTS_SYSTEM_PROMPT = """You are a Payments Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to optimize Days Payable Outstanding (DPO) by:
1. Analyzing pending payables using get_pending_payables
2. Checking cash flow forecasts using get_cash_forecast to identify payment windows
3. Reviewing historical spending using analyze_ledger_spending for context
4. Scheduling payments using schedule_payment to maximize cash retention while maintaining vendor relationships

Important Constraints:
- ALWAYS maintain minimum cash balance of ₹50,000
- Critical vendors MUST be paid within 3 days of due date
- Low priority payments can be delayed if cash is tight
- Consider forecasted receivables when scheduling payments

WORKFLOW:
1. First, call get_pending_payables with entity_id to see all bills due
2. Call get_cash_forecast with entity_id to understand cash position
3. Optionally call analyze_ledger_spending to see historical patterns
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
        return [get_cash_forecast, get_pending_payables, schedule_payment, add_ledger_transaction, analyze_ledger_spending]
    
    async def run(self, task: str = "Create an optimized payment schedule for the next 30 days") -> Dict[str, Any]:
        """Execute the payments agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_payments_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the payments agent."""
    agent = PaymentsAgent(entity_id)
    return await agent.run(task or "Create an optimized payment schedule for the next 30 days")
