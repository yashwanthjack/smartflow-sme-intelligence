# GST Agent - Automated Compliance and Reconciliation
# Autonomous tool-calling agent powered by LangChain
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.tools import (
    check_gst_compliance,
    get_gst_reconciliation
)


GST_SYSTEM_PROMPT = """You are a GST Compliance Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to ensure GST compliance by:
1. Monitoring GST filing status (GSTR-1, GSTR-3B) using check_gst_compliance
2. Reconciling purchase register with GSTR-2A using get_gst_reconciliation
3. Identifying blocked Input Tax Credit (ITC)
4. Flagging vendors who haven't filed their returns

Important GST Rules:
- ITC can only be claimed if vendor has filed their GSTR-1
- Mismatches between purchase register and GSTR-2A must be resolved
- All returns must be filed by due dates to avoid penalties
- Vendors with blocked ITC should be notified to file their returns

WORKFLOW:
1. Call check_gst_compliance with entity_id to get filing status and ITC data
2. Call get_gst_reconciliation with entity_id to find mismatches
3. Analyze the results and provide:
   - Filing status summary
   - ITC availability and blocked amounts
   - Mismatch details and recommended actions
   - Compliance risk assessment"""


class GSTAgent(BaseAgent):
    """Agent responsible for GST compliance and reconciliation."""
    
    @property
    def name(self) -> str:
        return "GSTAgent"
    
    @property
    def system_prompt(self) -> str:
        return GST_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [check_gst_compliance, get_gst_reconciliation]
    
    async def run(self, task: str = "Check GST compliance status and identify any issues") -> Dict[str, Any]:
        """Execute the GST agent using autonomous tool calling."""
        return await self.run_with_tools(task)


async def run_gst_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the GST agent."""
    agent = GSTAgent(entity_id)
    return await agent.run(task or "Check GST compliance status and identify any issues")
