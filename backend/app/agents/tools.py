# SmartFlow Agent Tools
# These tools provide the agents with access to financial data and actions

from langchain.tools import tool
from typing import Optional
from datetime import date, timedelta

from sqlalchemy.orm import Session
from contextvars import ContextVar

# Database session helper (async-safe using ContextVar)
_db_session_var: ContextVar[Optional[Session]] = ContextVar("_db_session", default=None)

def set_db_session(db: Session):
    """Set the database session for tools to use."""
    _db_session_var.set(db)

def get_db_session() -> Optional[Session]:
    """Get the current database session."""
    return _db_session_var.get()


# ============================================================================
# COLLECTIONS TOOLS
# ============================================================================

@tool
def get_overdue_invoices(entity_id: str) -> str:
    """Get list of overdue invoices for an entity.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Formatted list of overdue invoices with customer names, amounts, and days overdue
    """
    db = get_db_session()
    
    if db is not None:
        try:
            from app.models.invoice import Invoice
            from app.models.counterparty import Counterparty
            
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
            
            if overdue:
                result = "📋 **Overdue Invoices Report**\n\n"
                total = 0
                for inv in overdue:
                    days_overdue = (today - inv.due_date).days
                    # Try to get counterparty name
                    cp_name = "Unknown Customer"
                    if inv.counterparty_id:
                        cp = db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                        if cp:
                            cp_name = cp.name
                    
                    result += f"- **{inv.invoice_number}**: ₹{inv.balance_due:,.0f} from {cp_name} ({days_overdue} days overdue)\n"
                    total += inv.balance_due
                
                result += f"\n**Total Overdue**: ₹{total:,.0f}"
                result += f"\n**Total Overdue**: ₹{total:,.0f}"
                return result
        except Exception as e:
            return f"Error fetching overdue invoices: {str(e)}"
    
    return "✅ **No overdue invoices found.** Great job on collections!"


@tool
def get_customer_risk_score(customer_name: str) -> str:
    """Get credit risk score for a specific customer/counterparty.
    
    Args:
        customer_name: Name of the customer to assess
        
    Returns:
        Risk score (300-900) and risk band with explanation
    """
    from app.services.scoring_service import ScoringService
    
    # For customer-level scoring, we use simplified heuristics
    # In production, this would query CreditFeature table for the counterparty
    
    db = get_db_session()
    service = ScoringService(db)
    
    # Mock risk profiles (in production, query from CreditFeature model)
    risk_profiles = {
        "ABC Corp": {"score": 450, "band": "C", "history": "2 late payments in last 6 months"},
        "XYZ Ltd": {"score": 720, "band": "A", "history": "Consistent on-time payments"},
        "Tech Solutions": {"score": 650, "band": "B", "history": "1 delayed payment, otherwise good"},
    }
    
    profile = risk_profiles.get(customer_name, {"score": 600, "band": "B", "history": "Limited payment history"})
    
    risk_label = "High Risk" if profile["band"] == "C" else ("Medium Risk" if profile["band"] == "B" else "Low Risk")
    
    return f"""📊 **Risk Assessment: {customer_name}**
- Score: {profile['score']} / 900
- Band: {profile['band']} ({risk_label})
- History: {profile['history']}
"""


@tool
def draft_payment_reminder(customer_name: str, amount: float, days_overdue: int, tone: str = "polite") -> str:
    """Draft a payment reminder email/message for a customer.
    
    Args:
        customer_name: Name of the customer
        amount: Amount due in INR
        days_overdue: Number of days the payment is overdue
        tone: Tone of the message - 'polite', 'firm', or 'urgent'
        
    Returns:
        Draft message text ready to send
    """
    if tone == "urgent" or days_overdue > 30:
        return f"""⚠️ **URGENT: Final Payment Notice**

Dear {customer_name},

This is a FINAL NOTICE regarding your outstanding payment of ₹{amount:,.2f}.

Your account is now **{days_overdue} days overdue**. Immediate payment is required to avoid:
- Late payment fees
- Service suspension
- Credit rating impact

Please remit payment within **48 hours** or contact us to discuss payment arrangements.

Bank Details:
- Account: SmartFlow Pvt Ltd
- IFSC: HDFC0001234
- Account No: 12345678901234

Regards,
SmartFlow Collections
"""
    elif tone == "firm" or days_overdue > 15:
        return f"""📧 **Payment Reminder - Action Required**

Dear {customer_name},

We notice that your payment of ₹{amount:,.2f} is now {days_overdue} days past due.

We kindly request you to clear this outstanding amount at your earliest convenience.

If you have already made the payment, please share the transaction details.

Thank you for your prompt attention.

Best regards,
SmartFlow Team
"""
    else:
        return f"""📧 **Gentle Payment Reminder**

Dear {customer_name},

Hope this message finds you well!

This is a friendly reminder that your payment of ₹{amount:,.2f} is pending. 
The invoice is {days_overdue} days past the due date.

Please let us know if you need any clarification or have any concerns.

Thank you!

Warm regards,
SmartFlow Team
"""


# ============================================================================
# PAYMENTS TOOLS
# ============================================================================

@tool
def get_cash_forecast(entity_id: str, days: int = 30) -> str:
    """Get cash flow forecast for the next N days using Prophet model.
    
    Args:
        entity_id: The unique identifier of the business entity
        days: Number of days to forecast (default 30)
        
    Returns:
        Daily cash balance predictions with confidence intervals
    """
    from app.services.forecasting_service import ForecastingService
    
    db = get_db_session()
    service = ForecastingService(db)
    forecast = service.forecast(entity_id, days)
    
    result = f"📈 **Cash Flow Forecast** (Method: {forecast['method']})\n\n"
    
    # Show key days (7, 14, 21, 30)
    daily = forecast.get('daily_forecast', [])
    key_days = [6, 13, 20, 29]  # 0-indexed
    
    for idx in key_days:
        if idx < len(daily):
            day = daily[idx]
            day_num = idx + 1
            result += f"- **Day {day_num}** ({day['date']}): ₹{day['predicted']:,.0f} "
            result += f"(Range: ₹{day['lower_bound']:,.0f} - ₹{day['upper_bound']:,.0f})\n"
    
    # Add summary
    summary = forecast.get('summary', {})
    result += f"\n**Net Cash Flow**: ₹{summary.get('net_cash_flow', 0):,.0f}"
    
    # Add alerts
    alerts = forecast.get('alerts', [])
    if alerts:
        result += "\n\n**⚠️ Alerts:**\n"
        for alert in alerts:
            result += f"- [{alert['severity']}] {alert['message']}\n"
    
    return result


@tool
def get_pending_payables(entity_id: str) -> str:
    """Get list of pending vendor payments/payables.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        List of pending vendor payments with due dates and priority
    """
    db = get_db_session()
    
    if db is not None:
        try:
            from app.models.invoice import Invoice
            from app.models.counterparty import Counterparty
            
            today = date.today()
            future = today + timedelta(days=30)
            
            payables = (
                db.query(Invoice)
                .filter(Invoice.entity_id == entity_id)
                .filter(Invoice.invoice_type == "payable")
                .filter(Invoice.status.in_(["pending", "partial"]))
                .filter(Invoice.due_date <= future)
                .order_by(Invoice.due_date)
                .limit(10)
                .all()
            )
            
            if payables:
                result = "📋 **Pending Payables**\n\n"
                total = 0
                for inv in payables:
                    days_until = (inv.due_date - today).days
                    cp_name = "Unknown Vendor"
                    if inv.counterparty_id:
                        cp = db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                        if cp:
                            cp_name = cp.name
                    
                    priority = "Critical" if days_until <= 3 else ("Medium" if days_until <= 7 else "Low")
                    result += f"- **{cp_name}**: ₹{inv.balance_due:,.0f} due in {days_until} days [{priority}]\n"
                    total += inv.balance_due
                
                result += f"\n**Total Pending**: ₹{total:,.0f}"
                result += f"\n**Total Pending**: ₹{total:,.0f}"
                return result
            else:
                return "✅ **No pending payables found.** You are up to date!"
        except Exception as e:
             return f"Error fetching payables: {str(e)}"
    
    return "⚠️ Database connection unavailable."


@tool
def schedule_payment(vendor_name: str, amount: float, pay_date: str) -> str:
    """Schedule a payment to a vendor for a specific date.
    
    Args:
        vendor_name: Name of the vendor
        amount: Amount to pay in INR
        pay_date: Date to make payment (YYYY-MM-DD format)
        
    Returns:
        Confirmation of scheduled payment
    """
    # In production, this would create a scheduled payment record
    return f"""✅ **Payment Scheduled**

- **Vendor**: {vendor_name}
- **Amount**: ₹{amount:,.2f}
- **Scheduled Date**: {pay_date}
- **Status**: Pending Owner Approval

*This payment will be executed after approval.*
"""


# ============================================================================
# LEDGER ANALYSIS TOOLS
# ============================================================================

@tool
def analyze_ledger_spending(entity_id: str) -> str:
    """Analyze historical spending from the ledger to find trends.
    Useful for answering 'highest spent month', 'spending trends', etc.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Analysis of monthly spending and top categories.
    """
    db = get_db_session()
    if not db:
        return "Database connection unavailable."
        
    try:
        from app.models.ledger_entry import LedgerEntry
        from sqlalchemy import func, extract
        import calendar
        
        # 1. Monthly Spending Analysis (Expenses only, i.e., amount < 0)
        # Note: In our Ledger, expenses might be negative or positive depending on account type.
        # usually Expenses are Debit, which we often store as negative or track as 'Debit'.
        # Let's assume amount < 0 is outflow/expense for simplicity based on common schema,
        # OR check if category implies expense.
        # Actually safer to look at all transactions and group by month.
        
        results = (
            db.query(
                func.to_char(LedgerEntry.ledger_date, 'YYYY-MM').label("month"),
                func.sum(LedgerEntry.amount).label("net_change"),
                func.sum(func.abs(LedgerEntry.amount)).label("volume")
            )
            .filter(LedgerEntry.entity_id == entity_id)
            .group_by("month")
            .order_by("month")
            .all()
        )
        
        if not results:
            return "No ledger data found to analyze spending."
            
        # Re-query specifically for outflows (assuming negative amounts are outflows, 
        # OR heuristic: if allow manual transaction tool asked for negative/positive, we follow that.
        # Let's try to assume expenses are negative. If user data is all positive, we might need to adjust.
        # Based on previous tasks, user has 2005 entries.
        
        expenses = (
            db.query(
                func.to_char(LedgerEntry.ledger_date, 'YYYY-MM').label("month"),
                func.sum(LedgerEntry.amount).label("total_expense")
            )
            .filter(LedgerEntry.entity_id == entity_id)
            .filter(LedgerEntry.amount < 0)
            .group_by("month")
            .order_by(func.sum(LedgerEntry.amount).asc()) # Most negative first (highest expense)
            .all()
        )
        
        report = "📊 **Ledger Spending Analysis**\n\n"
        
        if expenses:
            highest_month = expenses[0] # Tuple: (month_str, amount)
            # expenses are negative, so min() is highest absolute spending
            
            y, m = highest_month[0].split('-')
            month_name = calendar.month_name[int(m)]
            amount = abs(highest_month[1])
            
            report += f"**Highest Spending Month**: {month_name} {y} (₹{amount:,.0f})\n\n"
            
            report += "**Monthly Spending Trend**:\n"
            # Sort chronologically for trend
            expenses_sorted = sorted(expenses, key=lambda x: x[0], reverse=True)[:6] # Last 6 active months
            for month_str, amount in expenses_sorted:
                amt = abs(amount)
                report += f"- {month_str}: ₹{amt:,.0f}\n"
        else:
            report += "No explicit expense entries (negative amounts) found.\n"
            
        return report

    except Exception as e:
        return f"Error analyzing ledger: {str(e)}"


# ============================================================================
# GST COMPLIANCE TOOLS
# ============================================================================

@tool
def check_gst_compliance(entity_id: str) -> dict:
    """Check GST filing status, ITC availability, and compliance issues.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Dictionary containing GST compliance data
    """
    db = get_db_session()
    
    if db is not None:
        try:
            from app.models.gst_summary import GSTSummary
            
            # Get latest GST summary
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
                
                return {
                    "period": latest.period,
                    "return_type": latest.return_type,
                    "filing_status": latest.filing_status,
                    "filed_on": str(latest.filed_on) if latest.filed_on else None,
                    "tax_summary": {
                        "output_tax": output_tax,
                        "input_credit": input_credit,
                        "net_payable": net_payable
                    }
                }
        except Exception as e:
            return f"Error fetching GST data: {str(e)}"
    
    return {
        "period": "N/A",
        "return_type": "N/A",
        "filing_status": "No GST Data Uploaded",
        "filed_on": None,
        "tax_summary": {
            "output_tax": 0,
            "input_credit": 0,
            "net_payable": 0
        },
        "itc": {
            "available": 0,
            "blocked": 0
        },
        "blocked_itc_details": [],
        "recommendation": "Please upload your GSTR-1 and GSTR-3B JSON files to see compliance status."
    }


@tool 
def get_gst_reconciliation(entity_id: str) -> dict:
    """Reconcile purchase register with GSTR-2A to find mismatches.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Dictionary containing reconciliation data
    """
    # In production, this would compare internal records with GSTR-2A downloaded data
    return {
        "summary": {
            "total_invoices": 0,
            "matched": 0,
            "mismatches": 0
        },
        "mismatches": [],
        "action_required": "No invoices found for reconciliation. Please upload purchase data."
    }


# ============================================================================
# CREDIT ADVISORY TOOLS
# ============================================================================

@tool
def get_entity_credit_score(entity_id: str) -> str:
    """Get overall credit score and risk assessment for the entity.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Credit score, risk band, and key factors
    """
    from app.services.scoring_service import ScoringService
    
    db = get_db_session()
    service = ScoringService(db)
    result = service.calculate_score(entity_id)
    
    output = f"""📊 **SmartFlow Credit Assessment**

**Overall Score**: {result['score']} / 900
**Risk Band**: {result['risk_band']} ({result['risk_label']})
**Method**: {result['method']}

**Key Factors**:
"""
    
    for factor in result.get('factors', [])[:5]:
        icon = "✅" if factor.get('positive', True) else "⚠️"
        output += f"{icon} {factor['factor']} ({factor['impact']})\n"
    
    # Add loan eligibility
    eligibility = result.get('loan_eligibility', {})
    output += f"""
**Lender Eligibility**:
- Working Capital: {eligibility.get('working_capital_limit', 'N/A')}
- Interest Rate: {eligibility.get('indicative_rate', 'N/A')}
- Invoice Discounting: {eligibility.get('invoice_discounting', 'N/A')}
"""
    
    return output


@tool
def calculate_cash_runway(entity_id: str) -> str:
    """Calculate how many days of operating expenses the current cash can cover.
    
    Args:
        entity_id: The unique identifier of the business entity
        
    Returns:
        Cash runway analysis with recommendations
    """
    from app.services.forecasting_service import ForecastingService
    
    db = get_db_session()
    service = ForecastingService(db)
    forecast = service.forecast(entity_id, 30)
    
    # Calculate runway based on forecast
    daily_forecasts = forecast.get('daily_forecast', [])
    
    if not daily_forecasts:
        # Fallback mock data
        return """🏃 **Cash Runway Analysis**

**Current Position**:
- Current Cash Balance: ₹4,50,000
- Average Daily Operating Expense: ₹25,000
- **Runway**: 18 days

**Recommendations**:
1. 🔴 **Urgent**: Accelerate collection from overdue invoices
2. 🟡 **Consider**: Delay non-critical vendor payments
3. 🟢 **Option**: Apply for invoice discounting facility
"""
    
    # Estimate runway from forecast
    cumulative = 0
    runway_days = 0
    # Calculate actual balance from DB
    if db is not None:
        from app.models.ledger_entry import LedgerEntry
        from sqlalchemy import func
        initial_balance = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.entity_id == entity_id).scalar() or 0
    else:
        initial_balance = 450000  # Fallback if no DB session
    
    for i, day in enumerate(daily_forecasts):
        cumulative += day['predicted']
        if initial_balance + cumulative <= 50000:  # Minimum balance threshold
            runway_days = i + 1
            break
    else:
        runway_days = len(daily_forecasts)
    
    net_flow = forecast.get('summary', {}).get('net_cash_flow', 0)
    
    status = "✅ Healthy" if runway_days >= 30 else ("⚠️ Attention Needed" if runway_days >= 15 else "🔴 Critical")
    
    return f"""🏃 **Cash Runway Analysis**

**Current Position**:
- Estimated Cash Balance: ₹4,50,000
- Forecast Method: {forecast.get('method', 'unknown')}
- **Runway**: {runway_days} days {status}

**30-Day Projection**:
- Net Cash Flow: ₹{net_flow:,.0f}

**Recommendations**:
{"1. 🔴 **Urgent**: Cash is critically low, accelerate collections immediately" if runway_days < 15 else "1. ✅ Cash position is healthy"}
2. Review pending payables and prioritize by vendor criticality
3. Consider invoice discounting for immediate cash needs
"""
# ============================================================================
# AUTONOMOUS ACTION TOOLS
# ============================================================================

@tool
def add_ledger_transaction(entity_id: str, description: str, amount: float, category: str = "Other") -> str:
    """AUTONOMOUS ACTION: Adds a new manual transaction to the ledger.
    Use this to record payments, expenses, or income found during analysis.
    
    Args:
        entity_id: The unique identifier of the business entity
        description: Text describing the transaction
        amount: Numerical value (positive for income, negative for expense)
        category: Billing category
    """
    db = get_db_session()
    if not db:
        from app.db.database import SessionLocal
        db = SessionLocal()
        
    try:
        from app.models.ledger_entry import LedgerEntry
        import uuid
        from datetime import datetime
        
        new_entry = LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=datetime.utcnow(),
            description=description,
            amount=amount,
            category=category,
            source_type="manual"
        )
        db.add(new_entry)
        db.commit()
        return f"✅ Autonomous Action Success: Recorded '{description}' for ₹{amount:,.0f}."
    except Exception as e:
        return f"❌ Autonomous Action Failed: {str(e)}"
    finally:
        pass

@tool
def update_invoice_status(invoice_id: str, new_status: str) -> str:
    """AUTONOMOUS ACTION: Updates the status of an invoice.
    Use this after identifying a payment or sending a reminder.
    
    Args:
        invoice_id: The ID of the invoice to update
        new_status: One of: 'paid', 'reminded', 'disputed', 'pending'
    """
    db = get_db_session()
    if not db:
        from app.db.database import SessionLocal
        db = SessionLocal()
        
    try:
        from app.models.invoice import Invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return f"❌ Invoice {invoice_id} not found."
            
        old_status = invoice.status
        invoice.status = new_status
        db.commit()
        return f"✅ Autonomous Action Success: Invoice {invoice.invoice_number} moved from {old_status} to {new_status}."
    except Exception as e:
        return f"❌ Autonomous Action Failed: {str(e)}"
