# Collections Agent - Reduces Days Sales Outstanding (DSO)
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    get_overdue_invoices,
    get_customer_risk_score,
    draft_payment_reminder,
    update_invoice_status
)


COLLECTIONS_SYSTEM_PROMPT = """You are a Collections Agent for SmartFlow, an AI-powered financial operating system for Indian SMEs.

Your primary goal is to reduce Days Sales Outstanding (DSO) by:
1. Identifying overdue invoices
2. Assessing customer risk to prioritize collection efforts
3. Drafting appropriate payment reminders based on risk level

Important Guidelines:
- High-risk (Band C) customers should receive urgent tone reminders
- Medium-risk (Band B) customers should receive firm but professional reminders
- Low-risk (Band A) customers should receive polite reminders
- Always prioritize by amount * days_overdue for maximum impact

Provide a prioritized collection action plan with specific recommendations."""


class CollectionsAgent(BaseAgent):
    """Agent responsible for managing receivables and reducing DSO."""
    
    @property
    def name(self) -> str:
        return "CollectionsAgent"
    
    @property
    def system_prompt(self) -> str:
        return COLLECTIONS_SYSTEM_PROMPT
    
    @property
    def tools(self) -> list:
        return [get_overdue_invoices, get_customer_risk_score, draft_payment_reminder, update_invoice_status]
    
    async def run(self, task: str = "Analyze overdue invoices and create a prioritized collection plan") -> Dict[str, Any]:
        """Execute the collections agent using direct tool invocation."""
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        set_db_session(db)
        self.llm = get_llm()
        
        try:
            # Step 1: Get overdue invoices
            # Tools are typically synchronous, but we can wrap them if needed. 
            # For now, let's assume tool execution is fast enough or use run_in_executor if totally blocking.
            # But the MAIN blocker is LLM.
            invoices_report = get_overdue_invoices.invoke(self.entity_id)
            
            # Step 2: Get risk scores for key customers
            risk_reports = []
            # In a real scenario, we'd extract names from invoices_report
            # For now, we'll try a few common ones or rely on the LLM to ask for them in future iterations
            # Simplified: Just feed the invoice report to the LLM
            
            # Step 3: Compose Prompt
            prompt = f"""
            {self.system_prompt}
            
            TASK: {task}
            
            DATA AVAILABLE:
            {invoices_report}
            
            Please provide a detailed Collections Analysis and Action Plan.
            """
            
            # Step 4: Invoke LLM
            print(f"🤖 CollectionsAgent invoking LLM...")
            try:
                response = await self.llm.ainvoke(prompt)
                output = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"❌ LLM generation failed: {e}")
                output = f"Error generating analysis: {e}\n\nFallback Data:\n{invoices_report}"

            self.log_action("collection_plan_generated", {"result": output[:500]})
            return {"output": output, "agent": self.name}
        except Exception as e:
            output = f"Agent Error: {str(e)}"
            return {"output": output, "agent": self.name}
        finally:
            db.close()
            
        return {"output": output, "agent": self.name}


async def run_collections_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the collections agent."""
    agent = CollectionsAgent(entity_id)
    return await agent.run(task or "Analyze overdue invoices and create a prioritized collection plan")
