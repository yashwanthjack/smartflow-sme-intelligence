# Credit Advisory Agent - CFO-level financial guidance
# Autonomous tool-calling agent powered by LangChain
import re
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.tools import (
    get_entity_credit_score,
    calculate_cash_runway,
    get_cash_forecast
)


CREDIT_ADVISORY_SYSTEM_PROMPT = """You are a Credit Advisory Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

You act as a fractional CFO, providing strategic financial guidance by:
1. Assessing the entity's creditworthiness using get_entity_credit_score
2. Analyzing cash runway using calculate_cash_runway
3. Forecasting cash flow using get_cash_forecast
4. Recommending financing options (internal vs external)

Financial Advisory Guidelines:
- Cash runway < 15 days: URGENT action needed
- Cash runway 15-30 days: Proactive measures recommended
- Cash runway > 30 days: Focus on optimization
- Always consider cost of capital when recommending external financing
- Invoice discounting is cheaper than term loans for short-term needs

WORKFLOW:
1. Call get_entity_credit_score with entity_id to assess creditworthiness
2. Call calculate_cash_runway with entity_id to understand survival time
3. If the user asks about forecasts, call get_cash_forecast with entity_id and appropriate days
4. Synthesize the data into strategic financial recommendations with specific action items

When answering questions about specific topics:
- "credit score" / "rating" → focus on get_entity_credit_score results
- "runway" / "cash position" / "how long" → focus on calculate_cash_runway results
- "forecast" / "prediction" / "revenue dip" → focus on get_cash_forecast results
- "loan" / "eligibility" / "lender" → use credit score data + lender eligibility section
- General questions → use all tools for comprehensive analysis"""


class CreditAdvisoryAgent(BaseAgent):
    """Agent responsible for CFO-level financial advisory."""
    
    @property
    def name(self) -> str:
        return "CreditAdvisoryAgent"
    
    @property
    def system_prompt(self) -> str:
        return CREDIT_ADVISORY_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [get_entity_credit_score, calculate_cash_runway, get_cash_forecast]
    
    async def run(self, task: str = "Provide a comprehensive financial health assessment and recommendations") -> Dict[str, Any]:
        """Execute the credit advisory agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_credit_advisory_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the credit advisory agent."""
    agent = CreditAdvisoryAgent(entity_id)
    return await agent.run(task or "Provide a comprehensive financial health assessment and recommendations")
