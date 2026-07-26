from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List

from app.db.database import SessionLocal
from app.agents.tools import set_db_session
from app.services.scoring_service import ScoringService
from app.services.forecasting_service import ForecastingService
from app.models.invoice import Invoice
from app.models.counterparty import Counterparty
from app.models.ledger_entry import LedgerEntry
from app.models.gst_summary import GSTSummary
from sqlalchemy import func
from datetime import date, timedelta

# Initialize FastMCP Server
mcp = FastMCP("SmartFlow-Tools-Server")

# Dependency hook for DB session
def get_db():
    db = SessionLocal()
    try:
        set_db_session(db) # Make tools.py compatible if needed
        yield db
    finally:
        db.close()


@mcp.tool()
def get_overdue_invoices(entity_id: str) -> str:
    """Get list of overdue invoices for an entity."""
    db = SessionLocal()
    try:
        today = date.today()
        overdue = (
            db.query(Invoice)
            .filter(Invoice.entity_id == entity_id)
            .filter(Invoice.invoice_type == "receivable")
            .filter(Invoice.status.in_(["pending", "partial", "overdue"]))
            .filter(Invoice.due_date < today)
            .order_by(Invoice.balance_due.desc())
            .limit(10)
            .all()
        )
        
        if not overdue:
            return "✅ **No overdue invoices found.** Great job on collections!"
            
        result = "📋 **Overdue Invoices Report**\n\n"
        total = 0
        for inv in overdue:
            days_overdue = (today - inv.due_date).days
            cp_name = "Unknown Customer"
            if inv.counterparty_id:
                cp = db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                if cp:
                    cp_name = cp.name
            
            result += f"- **{inv.invoice_number}**: ₹{inv.balance_due:,.0f} from {cp_name} ({days_overdue} days overdue)\n"
            total += inv.balance_due
        
        result += f"\n**Total Overdue**: ₹{total:,.0f}"
        return result
    finally:
        db.close()

@mcp.tool()
def get_cash_forecast(entity_id: str, days: int = 30) -> str:
    """Get cash flow forecast for the next N days using ML model."""
    db = SessionLocal()
    try:
        service = ForecastingService(db)
        forecast = service.forecast(entity_id, days)
        
        result = f"📈 **Cash Flow Forecast** (Method: {forecast.get('method', 'unknown')})\n\n"
        
        daily = forecast.get('daily_forecast', [])
        key_days = [6, 13, 20, 29]
        
        for idx in key_days:
            if idx < len(daily):
                day = daily[idx]
                day_num = idx + 1
                result += f"- **Day {day_num}** ({day['date']}): ₹{day['predicted']:,.0f} "
                result += f"(Range: ₹{day['lower_bound']:,.0f} - ₹{day['upper_bound']:,.0f})\n"
        
        summary = forecast.get('summary', {})
        result += f"\n**Net Cash Flow**: ₹{summary.get('net_cash_flow', 0):,.0f}"
        
        alerts = forecast.get('alerts', [])
        if alerts:
            result += "\n\n**⚠️ Alerts:**\n"
            for alert in alerts:
                result += f"- [{alert['severity']}] {alert['message']}\n"
        
        return result
    finally:
        db.close()

@mcp.tool()
def check_gst_compliance(entity_id: str) -> str:
    """Check GST filing status and ITC constraints."""
    db = SessionLocal()
    try:
        latest = (
            db.query(GSTSummary)
            .filter(GSTSummary.entity_id == entity_id)
            .order_by(GSTSummary.period.desc())
            .first()
        )
        
        if latest:
            output_tax = latest.output_tax or 0
            input_credit = latest.input_credit or 0
            net_payable = output_tax - input_credit
            return f"GST Status: {latest.filing_status} for {latest.period}. Net Payable: ₹{net_payable:,.2f}"
            
        return "No GST Data Uploaded"
    finally:
        db.close()

@mcp.tool()
def query_ledger(entity_id: str, limit: int = 5) -> str:
    """Search for recent ledger entries."""
    db = SessionLocal()
    try:
        entries = db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id).order_by(LedgerEntry.ledger_date.desc()).limit(limit).all()
        if not entries:
            return "No ledger entries found."
            
        result = "📒 **Recent Ledger Entries**\n\n"
        for entry in entries:
            result += f"- {entry.ledger_date}: ₹{entry.amount:,.0f} | {entry.category} | {entry.description}\n"
        return result
    finally:
        db.close()

# Ensure standard FastMCP entry point if run directly
if __name__ == "__main__":
    mcp.run()
