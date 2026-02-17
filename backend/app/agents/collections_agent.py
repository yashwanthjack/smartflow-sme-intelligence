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
    
    def run(self, task: str = "Analyze overdue invoices and create a prioritized collection plan") -> Dict[str, Any]:
        """Execute the collections agent using direct tool invocation."""
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        set_db_session(db)
        
        try:
            # Step 1: Get overdue invoices
            invoices_report = get_overdue_invoices.invoke(self.entity_id)
            
            # Step 2: Get risk scores for key customers
            risk_reports = []
            for customer in ["ABC Corp", "XYZ Ltd", "Tech Solutions"]:
                try:
                    risk_reports.append(get_customer_risk_score.invoke(customer))
                except Exception:
                    pass
            
            # Step 3: Compose final analysis
            output = f"""📋 **Collections Agent Analysis**

{invoices_report}

---

**Customer Risk Assessment:**
{''.join(risk_reports) if risk_reports else 'No customer risk data available.'}

---

**Recommended Actions:**
1. 🔴 Prioritize collection from high-risk customers (Band C) with largest overdue amounts
2. 🟡 Send firm reminders to medium-risk customers (Band B) 
3. 🟢 Send gentle reminders to low-risk customers (Band A)
4. 📊 Monitor DSO trend and escalate if it exceeds 45 days
"""
            self.log_action("collection_plan_generated", {"result": output[:500]})
            return {"output": output, "agent": self.name}
        except Exception as e:
            output = f"Agent Error: {str(e)}"
            return {"output": output, "agent": self.name}
        finally:
            db.close()
            
        return {"output": output, "agent": self.name}


def run_collections_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the collections agent."""
    agent = CollectionsAgent(entity_id)
    return agent.run(task or "Analyze overdue invoices and create a prioritized collection plan")
