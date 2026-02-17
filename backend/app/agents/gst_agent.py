# GST Agent - Automated Compliance and Reconciliation
from typing import Dict, Any


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
        """Execute the GST agent using direct tool invocation and LLM synthesis."""
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        import json
        from langchain_core.messages import HumanMessage, SystemMessage
        
        db = SessionLocal()
        set_db_session(db)
        
        try:
            # Step 1: Check compliance status
            try:
                compliance_data = check_gst_compliance.invoke(self.entity_id)
            except Exception as e:
                compliance_data = {"error": str(e)}
            
            # Step 2: Get reconciliation
            try:
                reconciliation_data = get_gst_reconciliation.invoke(self.entity_id)
            except Exception as e:
                reconciliation_data = {"error": str(e)}
            
            # Step 3: Synthesis
            llm = get_llm()
            
            # SAFEGUARD: If using the weak local TinyLlama model, bypass generation to prevent hallucinations.
            # We check the class name to avoid importing optional dependencies.
            is_local_weak_model = type(llm).__name__ == "HuggingFacePipeline"
            
            if is_local_weak_model:
                # Deterministic Template for Local CPU/TinyLlama
                filing_status = compliance_data.get('filing_status', 'Unknown')
                itc_val = compliance_data.get('itc', {}).get('available', 0)
                mismatches = reconciliation_data.get('summary', {}).get('mismatches', 0)
                
                output = (
                    f"**GST Status Summary**\n"
                    f"- Filing Status: {filing_status}\n"
                    f"- ITC Available: ₹{itc_val:,}\n"
                    f"- Mismatches: {mismatches}\n\n"
                    f"Recommendation: {compliance_data.get('recommendation', 'check portal')}"
                )
            else:
                # Advanced LLM (vLLM, Ollama, OpenAI, Gemini) - Use Prompting
                compliance_text = (
                    f"Filing: {compliance_data.get('filing_status', 'Unknown')}\n"
                    f"ITC: {compliance_data.get('itc', {}).get('available', 0)}\n"
                )
                recon_summary = reconciliation_data.get('summary', {})
                recon_text = (
                    f"Mismatches: {recon_summary.get('mismatches', 0)}\n"
                )
                
                formatted_prompt = (
                    f"System: Summarize this GST data concisely.\n"
                    f"Data:\n{compliance_text}{recon_text}\n"
                    f"Summary:"
                )
                
                response = llm.invoke(formatted_prompt)
                if hasattr(response, 'content'):
                    output = response.content
                else:
                    output = str(response)

            self.log_action("gst_compliance_checked", {"status": "success"})
            return {"output": output, "agent": self.name}
            
        except Exception as e:
            output = f"I encountered an error while analyzing your GST data: {str(e)}"
            return {"output": output, "agent": self.name}
        finally:
            db.close()


def run_gst_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the GST agent."""
    agent = GSTAgent(entity_id)
    return agent.run(task or "Check GST compliance status and identify any issues")
