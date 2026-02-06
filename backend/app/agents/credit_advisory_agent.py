# Credit Advisory Agent - CFO-level financial guidance
from typing import Dict, Any
from langchain.agents import create_agent

from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    get_entity_credit_score,
    calculate_cash_runway,
    get_cash_forecast
)


CREDIT_ADVISORY_SYSTEM_PROMPT = """You are a Credit Advisory Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

You act as a fractional CFO, providing strategic financial guidance by:
1. Assessing the entity's creditworthiness
2. Analyzing cash runway and working capital needs
3. Recommending financing options (internal vs external)
4. Suggesting capital restructuring when needed

Financial Advisory Guidelines:
- Cash runway < 15 days: URGENT action needed
- Cash runway 15-30 days: Proactive measures recommended
- Cash runway > 30 days: Focus on optimization
- Always consider cost of capital when recommending external financing
- Invoice discounting is cheaper than term loans for short-term needs

Provide strategic financial recommendations with specific action items."""


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
    
    def run(self, task: str = "Provide a comprehensive financial health assessment and recommendations") -> Dict[str, Any]:
        """Execute the credit advisory agent."""
        llm = get_llm()
        
        agent = create_agent(
            llm, 
            self.tools, 
            system_prompt=CREDIT_ADVISORY_SYSTEM_PROMPT
        )
        
        result = agent.invoke({
            "messages": [{"role": "user", "content": f"Entity ID: {self.entity_id}. Task: {task}"}]
        })
        
        self.log_action("financial_advice_generated", {"result": result})
        
        if hasattr(result, 'get'):
            output = result.get("output", str(result))
        else:
            output = str(result)
            
        return {"output": output, "agent": self.name}


def run_credit_advisory_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the credit advisory agent."""
    agent = CreditAdvisoryAgent(entity_id)
    return agent.run(task or "Provide a comprehensive financial health assessment and recommendations")
