# Credit Advisory Agent - CFO-level financial guidance
import re
from typing import Dict, Any


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


def _parse_query_context(query: str) -> Dict[str, Any]:
    """
    Parse the user's query to understand WHAT they want and for WHAT time period.
    Returns: {"focus": score|runway|eligibility|full, "days": int, "raw_period": str}
    """
    q = query.lower().strip()
    
    # Determine focus area
    focus = "full"
    if any(w in q for w in ["revenue", "forecast", "dip", "predict", "projection", "trend", "growth", "decline", "expected", "sales"]):
        focus = "forecast"
    elif any(w in q for w in ["runway", "burn", "how long", "months left", "cash position", "cash flow"]):
        focus = "runway"
    elif any(w in q for w in ["score", "credit score", "rating", "creditworth"]):
        focus = "score"
    elif any(w in q for w in ["loan", "eligib", "lender", "financing", "borrow"]):
        focus = "eligibility"
    
    # Parse time period
    days = 30  # default
    raw_period = "30 days"
    
    # Match "X months"
    m = re.search(r'(\d+)\s*months?', q)
    if m:
        months = int(m.group(1))
        days = months * 30
        raw_period = f"{months} months"
    
    # Match "X days"  
    m = re.search(r'(\d+)\s*days?', q)
    if m:
        days = int(m.group(1))
        raw_period = f"{days} days"
    
    # Match "X weeks"
    m = re.search(r'(\d+)\s*weeks?', q)
    if m:
        weeks = int(m.group(1))
        days = weeks * 7
        raw_period = f"{weeks} weeks"
    
    # Match "X years"
    m = re.search(r'(\d+)\s*years?', q)
    if m:
        years = int(m.group(1))
        days = years * 365
        raw_period = f"{years} years"
    
    # "next quarter"
    if "quarter" in q:
        days = 90
        raw_period = "1 quarter (90 days)"
    
    # "next year" / "annual"
    if "next year" in q or "annual" in q:
        days = 365
        raw_period = "1 year"
    
    return {"focus": focus, "days": days, "raw_period": raw_period}


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
        """Execute the credit advisory agent — query-aware."""
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        set_db_session(db)
        
        # Parse what the user is actually asking
        ctx = _parse_query_context(task)
        
        try:
            if ctx["focus"] == "forecast":
                return self._answer_forecast(ctx)
            elif ctx["focus"] == "score":
                return self._answer_score(ctx)
            elif ctx["focus"] == "runway":
                return self._answer_runway(ctx)
            elif ctx["focus"] == "eligibility":
                return self._answer_eligibility(ctx)
            else:
                return self._answer_full(ctx)
        except Exception as e:
            output = f"Agent Error: {str(e)}"
            return {"output": output, "agent": self.name}
        finally:
            db.close()
    
    def _answer_score(self, ctx) -> Dict[str, Any]:
        """Answer specifically about credit score."""
        credit_report = get_entity_credit_score.invoke(self.entity_id)
        self.log_action("credit_score_queried", {"focus": "score"})
        return {"output": credit_report, "agent": self.name}
    
    def _answer_runway(self, ctx) -> Dict[str, Any]:
        """Answer specifically about cash runway with the requested time period."""
        from app.services.forecasting_service import ForecastingService
        from app.agents.tools import get_db_session
        from app.models.ledger_entry import LedgerEntry
        from sqlalchemy import func
        
        days = min(ctx["days"], 365)  # Cap at 1 year
        raw_period = ctx["raw_period"]
        
        db = get_db_session()
        service = ForecastingService(db)
        
        try:
            forecast = service.forecast(self.entity_id, days)
        except Exception:
            forecast = {}
        
        # Get actual balance
        initial_balance = 450000  # default
        if db:
            bal = db.query(func.sum(LedgerEntry.amount)).filter(
                LedgerEntry.entity_id == self.entity_id
            ).scalar()
            if bal:
                initial_balance = abs(float(bal))
        
        daily_forecasts = forecast.get('daily_forecast', [])
        net_flow = forecast.get('summary', {}).get('net_cash_flow', 0)
        
        # Calculate runway
        if daily_forecasts:
            cumulative = 0
            runway_days = len(daily_forecasts)
            out_of_cash = False
            
            for i, day in enumerate(daily_forecasts):
                cumulative += day['predicted']
                if initial_balance + cumulative <= 50000:
                    runway_days = i + 1
                    out_of_cash = True
                    break
            
            if not out_of_cash:
                # If we didn't run out of cash in the forecast period, extrapolate
                if cumulative < 0:
                    # Burning cash: Estimate remaining runway
                    avg_daily_burn = abs(cumulative / len(daily_forecasts))
                    remaining_balance = initial_balance + cumulative
                    if avg_daily_burn > 0:
                        extra_days = int((remaining_balance - 50000) / avg_daily_burn)
                        runway_days += extra_days
                else:
                    # Cash positive/growing
                    runway_days = 999
            
            projected_balance = initial_balance + net_flow
        else:
            # Estimate based on avg daily burn
            avg_daily_burn = initial_balance / 30 if initial_balance else 15000
            runway_days = int(initial_balance / avg_daily_burn) if avg_daily_burn > 0 else 30
            projected_balance = initial_balance - (avg_daily_burn * days)
        
        # Determine status and display text
        if runway_days >= 365:
            display_runway = "> 1 Year"
            status = "✅ Healthy"
        elif runway_days >= 999:
             display_runway = "Infinite (Cash Positive)"
             status = "✅ Healthy"
        else:
            display_runway = f"{runway_days} days"
            status = "✅ Healthy" if runway_days >= 30 else ("⚠️ Attention Needed" if runway_days >= 15 else "🔴 Critical")
        
        output = f"""🏃 **Cash Runway — {raw_period} Projection**

**Current**: ₹{initial_balance:,.0f} cash balance
**Runway**: {display_runway} {status}
**{raw_period} Outlook**: Net flow ₹{net_flow:,.0f} → Projected balance ₹{projected_balance:,.0f}

"""
        if runway_days < 15:
            output += "⚠️ **Action Required**: Accelerate collections and delay non-critical payments."
        elif runway_days < days:
            output += f"📋 Cash may run low before {raw_period}. Consider invoice discounting."
        else:
            output += f"✅ Cash position looks healthy for the next {raw_period}."
        
        self.log_action("runway_queried", {"days": days, "runway": runway_days})
        return {"output": output, "agent": self.name}
    
    def _answer_eligibility(self, ctx) -> Dict[str, Any]:
        """Answer specifically about loan eligibility."""
        credit_report = get_entity_credit_score.invoke(self.entity_id)
        
        # Extract just the lender eligibility section
        sections = credit_report.split("**Lender Eligibility**")
        if len(sections) > 1:
            output = "🏦 **Lender Eligibility**" + sections[1]
        else:
            output = credit_report
        
        self.log_action("eligibility_queried", {"focus": "eligibility"})
        return {"output": output, "agent": self.name}
    
    def _answer_full(self, ctx) -> Dict[str, Any]:
        """Full credit + runway report."""
        credit_report = get_entity_credit_score.invoke(self.entity_id)
        
        try:
            runway_report = calculate_cash_runway.invoke(self.entity_id)
        except Exception:
            runway_report = "Cash runway analysis unavailable."
        
        output = f"""📈 **Financial Health Report**

{credit_report}

---

{runway_report}
"""
        self.log_action("financial_advice_generated", {"focus": "full"})
        return {"output": output, "agent": self.name}


def run_credit_advisory_agent(entity_id: str, task: str = None) -> Dict[str, Any]:
    """Convenience function to run the credit advisory agent."""
    agent = CreditAdvisoryAgent(entity_id)
    return agent.run(task or "Provide a comprehensive financial health assessment and recommendations")
