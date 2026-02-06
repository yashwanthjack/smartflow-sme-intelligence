# Payments Agent - Optimizes Days Payable Outstanding (DPO)
from typing import Dict, Any
from langchain.agents import create_agent

from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    get_cash_forecast,
    get_pending_payables,
    schedule_payment
)


PAYMENTS_SYSTEM_PROMPT = """You are a Payments Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to optimize Days Payable Outstanding (DPO) by:
1. Analyzing cash flow forecasts to identify payment windows
2. Prioritizing vendor payments based on criticality
3. Scheduling payments to maximize cash retention while maintaining vendor relationships

Important Constraints:
- ALWAYS maintain minimum cash balance of ₹50,000
- Critical vendors MUST be paid within 3 days of due date
- Low priority payments can be delayed if cash is tight
- Consider forecasted receivables when scheduling payments

Create an optimized payment schedule with dates and reasoning."""


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
        return [get_cash_forecast, get_pending_payables, schedule_payment]
    
    def run(self, task: str = "Create an optimized payment schedule for the next 30 days") -> Dict[str, Any]:
        """Execute the payments agent."""
        llm = get_llm()
        
        agent = create_agent(
            llm, 
            self.tools, 
            system_prompt=PAYMENTS_SYSTEM_PROMPT
        )
        
        result = agent.invoke({
            "messages": [{"role": "user", "content": f"Entity ID: {self.entity_id}. Task: {task}"}]
        })
        
        self.log_action("payment_schedule_generated", {"result": result})
        
        if hasattr(result, 'get'):
            output = result.get("output", str(result))
        else:
            output = str(result)
            
        return {"output": output, "agent": self.name}


def run_payments_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the payments agent."""
    agent = PaymentsAgent(entity_id)
    return agent.run(task or "Create an optimized payment schedule for the next 30 days")
