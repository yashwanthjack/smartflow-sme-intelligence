# GST Agent - Automated Compliance and Reconciliation
from typing import Dict, Any
from langchain.agents import create_agent

from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    check_gst_compliance,
    get_gst_reconciliation
)


GST_SYSTEM_PROMPT = """You are a GST Compliance Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to ensure GST compliance by:
1. Monitoring GST filing status (GSTR-1, GSTR-3B)
2. Reconciling purchase register with GSTR-2A
3. Identifying blocked Input Tax Credit (ITC)
4. Flagging vendors who haven't filed their returns

Important GST Rules:
- ITC can only be claimed if vendor has filed their GSTR-1
- Mismatches between purchase register and GSTR-2A must be resolved
- All returns must be filed by due dates to avoid penalties
- Vendors with blocked ITC should be notified to file their returns

Provide a comprehensive GST compliance report with action items."""


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
    
    def run(self, task: str = "Check GST compliance status and identify any issues") -> Dict[str, Any]:
        """Execute the GST agent."""
        llm = get_llm()
        
        agent = create_agent(
            llm, 
            self.tools, 
            system_prompt=GST_SYSTEM_PROMPT
        )
        
        result = agent.invoke({
            "messages": [{"role": "user", "content": f"Entity ID: {self.entity_id}. Task: {task}"}]
        })
        
        self.log_action("gst_compliance_checked", {"result": result})
        
        if hasattr(result, 'get'):
            output = result.get("output", str(result))
        else:
            output = str(result)
            
        return {"output": output, "agent": self.name}


def run_gst_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the GST agent."""
    agent = GSTAgent(entity_id)
    return agent.run(task or "Check GST compliance status and identify any issues")
