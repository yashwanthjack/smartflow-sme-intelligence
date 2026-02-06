from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.routers.data import get_dashboard_kpis
from app.db.database import SessionLocal
from typing import Dict, Any

class LenderDecisionAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "LenderDecisionAgent"
    
    @property
    def system_prompt(self) -> str:
        return """You are an Underwriting AI for a Fintech Lender. 
        Your job is to evaluate SME loan applications based on their live data.
        
        Decision Criteria:
        - FUND: Runway > 6mo OR Revenue Growth > 20%
        - REJECT: Runway < 3mo AND Burning Cash
        - REVIEW: Everything else
        
        Output format:
        {
            "decision": "FUND" | "REJECT" | "REVIEW",
            "max_credit_limit": <amount_in_INR>,
            "reason": "<short_explanation>",
            "risk_factors": ["list", "of", "risks"]
        }
        """

    async def get_sme_data(self):
        db = SessionLocal()
        try:
             # Reuse the KPI logic directly
             # In production, we'd use a service layer
             # For now, we mock the retrieval or assume the agent context has data
             # Let's call the KPI function (it's async, might be tricky in sync agent run)
             # So we will implement a synchronous version or use the tools mechanism
             pass
        finally:
            db.close()

    def run(self, task: str) -> Dict[str, Any]:
        # This agent is meant to be called with enriched context (KPIs) passed in the prompt
        # because the 'task' here is likely "Evaluate this SME" + JSON Data
        
        llm = get_llm()
        full_prompt = f"""
        {self.system_prompt}
        
        {task} 
        """
        # Task here is expected to contain the Financial Data JSON
        
        response = llm.invoke(full_prompt)
        
        self.log_action("underwrite", {"task": "underwriting", "response": response.content})
        return {"output": response.content, "agent": self.name}
