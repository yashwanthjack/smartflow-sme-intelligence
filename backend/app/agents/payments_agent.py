# Payments Agent - Optimizes Days Payable Outstanding (DPO)
from typing import Dict, Any


from app.agents.base_agent import BaseAgent
from app.agents.llm import get_llm
from app.agents.tools import (
    get_cash_forecast,
    get_pending_payables,
    schedule_payment,
    add_ledger_transaction,
    analyze_ledger_spending
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
        return [get_cash_forecast, get_pending_payables, schedule_payment, add_ledger_transaction, analyze_ledger_spending]
    
    async def run(self, task: str = "Create an optimized payment schedule for the next 30 days") -> Dict[str, Any]:
        """Execute the payments agent using direct tool invocation."""
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        set_db_session(db)
        
        try:
            # Step 1: Get pending payables
            payables_report = get_pending_payables.invoke(self.entity_id)
            
            # Step 2: Get cash forecast
            try:
                forecast_report = get_cash_forecast.invoke({"entity_id": self.entity_id, "days": 30})
            except Exception:
                forecast_report = "Cash forecast unavailable."
            
            # Step 3: Analyze historical spending
            try:
                spending_analysis = analyze_ledger_spending.invoke(self.entity_id)
            except Exception:
                spending_analysis = "Spending analysis unavailable."
            
            # Step 4: Compose analysis
            output = f"""💰 **Payments Agent Analysis**

{payables_report}

---

{spending_analysis}

---

**Cash Flow Outlook:**
{forecast_report}

---

**Payment Strategy:**
1. 🔴 **Critical payments** (due within 3 days): Pay immediately to avoid penalties
2. 🟡 **Medium priority** (due within 7 days): Schedule for day before due date
3. 🟢 **Low priority** (due in 10+ days): Can be delayed if cash is tight
4. 💡 Maintain minimum balance of ₹50,000 as safety buffer
"""
            self.log_action("payment_schedule_generated", {"result": output[:500]})
            return {"output": output, "agent": self.name}
        except Exception as e:
            output = f"Agent Error: {str(e)}"
            return {"output": output, "agent": self.name}
        finally:
            db.close()


async def run_payments_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the payments agent."""
    agent = PaymentsAgent(entity_id)
    return await agent.run(task or "Create an optimized payment schedule for the next 30 days")
