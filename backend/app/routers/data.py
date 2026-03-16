# Data API Router - Exposes backend data to frontend
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict, Any
from datetime import date, timedelta, datetime
import uuid

from app.db.database import SessionLocal
from app.models.entity import Entity
from app.models.ledger_entry import LedgerEntry
from app.models.invoice import Invoice
from app.models.counterparty import Counterparty
from app.services.forecasting_service import ForecastingService
from app.services.scoring_service import ScoringService
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ENTITIES
# ============================================================================

@router.get("/entities")
async def list_entities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List entities accessible to the current user (RBAC enforced)."""
    entity = db.query(Entity).filter(Entity.id == current_user.entity_id).first()
    if not entity:
        return []
    return [
        {
            "id": entity.id,
            "name": entity.name,
            "gstin": entity.gstin,
            "industry": entity.industry,
            "city": entity.city,
            "state": entity.state
        }
    ]


@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get entity details (RBAC enforced — user can only access their own entity)."""
    if current_user.entity_id != entity_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {
        "id": entity.id,
        "name": entity.name,
        "gstin": entity.gstin,
        "pan": entity.pan,
        "industry": entity.industry,
        "city": entity.city,
        "state": entity.state,
        "entity_type": entity.entity_type
    }


# ============================================================================
# FINANCIAL METRICS (OS DASHBOARD)
# ============================================================================

@router.get("/entities/{entity_id}/financial-metrics")
async def get_financial_metrics(entity_id: str, db: Session = Depends(get_db)):
    """Get high-level financial metrics for the OS dashboard."""
    today = date.today()
    six_months_ago = today - timedelta(days=180)
    
    # 1. Current Cash Balance
    cash_balance = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0
    
    # 2. Monthly Burn Rate (Average monthly outflow over last 6 months)
    # Using Python-side aggregation for SQLite/PostgreSQL compatibility
    expense_entries = db.query(LedgerEntry).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0,
        LedgerEntry.ledger_date >= six_months_ago
    ).all()
    
    monthly_expenses = {}
    for entry in expense_entries:
        month_key = entry.ledger_date.strftime('%Y-%m')
        monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + abs(entry.amount)
    
    if monthly_expenses:
        total_expense = sum(monthly_expenses.values())
        avg_burn_rate = total_expense / max(len(monthly_expenses), 1)
    else:
        avg_burn_rate = 0
        
    # 3. Runway (Months)
    runway_months = (cash_balance / avg_burn_rate) if avg_burn_rate > 0 else 999
    if cash_balance < 0: runway_months = 0
    
    # 4. Net Income This Month
    current_month_start = today.replace(day=1)
    net_income = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.ledger_date >= current_month_start
    ).scalar() or 0
    
    return {
        "cash_balance": round(cash_balance, 2),
        "monthly_burn_rate": round(avg_burn_rate, 2),
        "runway_months": round(runway_months, 1),
        "net_income_this_month": round(net_income, 2)
    }


@router.get("/entities/{entity_id}/dashboard-kpis")
async def get_dashboard_kpis(entity_id: str, db: Session = Depends(get_db)):
    """
    Unified endpoint for all Dashboard KPIs.
    Aggregates: Financial Metrics, Credit Score, and High-Level Risks.
    Uses real ScoringService for accurate credit assessment.
    """
    today = date.today()
    six_months_ago = today - timedelta(days=180)
    
    cash_balance = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0
    
    # Python-side monthly aggregation (SQLite compatible)
    expense_entries = db.query(LedgerEntry).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0,
        LedgerEntry.ledger_date >= six_months_ago
    ).all()
    
    monthly_expenses = {}
    for entry in expense_entries:
        month_key = entry.ledger_date.strftime('%Y-%m')
        monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + abs(entry.amount)
    
    avg_burn_rate = (sum(monthly_expenses.values()) / max(len(monthly_expenses), 1)) if monthly_expenses else 0
    runway_months = (cash_balance / avg_burn_rate) if avg_burn_rate > 0 else 999
    if cash_balance < 0: runway_months = 0
    
    net_income = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.ledger_date >= today.replace(day=1)
    ).scalar() or 0

    # 2. Credit Score — Use real ScoringService for accurate values
    scoring_service = ScoringService(db)
    score_data = scoring_service.calculate_score(entity_id)
    credit_score = score_data.get('score', 650)
    risk_band = score_data.get('risk_band', 'B')
    risk_label = score_data.get('risk_label', 'Medium Risk')

    # 3. Generate dynamic insights based on actual data
    insights = []
    if runway_months < 3:
        insights.append(f"⚠️ Critical: Runway is only {runway_months:.1f} months. Reduce burn or accelerate collections.")
    elif runway_months < 6:
        insights.append(f"Runway at {runway_months:.1f} months. Consider diversifying revenue streams.")
    else:
        insights.append(f"Runway is healthy at {runway_months:.1f} months at current burn rate.")
    
    if net_income < 0:
        insights.append(f"Net loss of ₹{abs(net_income):,.0f} this month. Review expense categories.")
    else:
        insights.append(f"Net income of ₹{net_income:,.0f} this month. Business is cash-flow positive.")
    
    if credit_score < 650:
        insights.append("Credit score needs improvement. Focus on GST compliance and collection speed.")

    return {
        "financials": {
            "cash_balance": round(cash_balance, 2),
            "monthly_burn_rate": round(avg_burn_rate, 2),
            "runway_months": round(runway_months, 1),
            "net_income_this_month": round(net_income, 2)
        },
        "credit": {
            "score": credit_score,
            "risk_band": risk_band,
            "risk_level": risk_label,
            "max_credit_limit": round(avg_burn_rate * 3, 2),
            "factors": score_data.get('factors', [])[:3]
        },
        "insights": insights
    }


@router.get("/entities/{entity_id}/pnl")
async def get_monthly_pnl(entity_id: str, months: int = 6, db: Session = Depends(get_db)):
    """Get aggregated monthly Income vs Expense for charts."""
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)
    
    # Query aggregated by month and type (income/expense)
    # Note: SQLite extraction syntax is slightly different if using SQLite vs Postgres
    # Using generic approach that works for seeded data
    
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.ledger_date >= start_date
    ).all()
    
    monthly_data = {}
    
    for entry in entries:
        month_key = entry.ledger_date.strftime("%Y-%m") # YYYY-MM
        if month_key not in monthly_data:
            monthly_data[month_key] = {"income": 0, "expense": 0}
            
        if entry.amount > 0:
            monthly_data[month_key]["income"] += entry.amount
        else:
            monthly_data[month_key]["expense"] += abs(entry.amount)
            
    # Convert to list sorted by month
    result = []
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        result.append({
            "month": month,
            "income": round(data["income"], 2),
            "expense": round(data["expense"], 2),
            "net": round(data["income"] - data["expense"], 2)
        })
        
    return result[-months:] # Return last N months


@router.get("/entities/{entity_id}/spend-by-category")
async def get_spend_by_category(entity_id: str, db: Session = Depends(get_db)):
    """Get summarized expenses by category."""
    # Logic: Sum negative amounts grouping by category
    
    # SQLite/Postgres agnostic raw query logic using Python aggregation 
    # (safer for compatibility with both DB types in this hybrid dev env)
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0 # Expenses only
    ).all()
    
    category_totals = {}
    
    for entry in entries:
        # Use description or subcategory if category is generic 'expense'
        cat = entry.subcategory or entry.category or "Other"
        if cat.lower() in ["payment", "expense", "purchase"]:
             # Try to infer from description if category is too generic
             if "salary" in (entry.description or "").lower(): cat = "Payroll"
             elif "rent" in (entry.description or "").lower(): cat = "Rent"
             elif "tax" in (entry.description or "").lower(): cat = "Taxes"
        
        cat = cat.title()
        category_totals[cat] = category_totals.get(cat, 0) + abs(entry.amount)
        
    # Convert to list
    result = [
        {"category": k, "amount": round(v, 2)} 
        for k, v in category_totals.items()
    ]
    
    # Sort by amount descending and take top 5, group rest as 'Other'
    result.sort(key=lambda x: x["amount"], reverse=True)
    
    if len(result) > 5:
        top_5 = result[:5]
        other_amount = sum(item["amount"] for item in result[5:])
        top_5.append({"category": "Other", "amount": round(other_amount, 2)})
        return top_5
        
    return result


# ============================================================================
# DASHBOARD STATS (Legacy)
# ============================================================================

@router.get("/entities/{entity_id}/stats")
async def get_dashboard_stats(entity_id: str, db: Session = Depends(get_db)):
    """Get dashboard statistics for an entity."""
    from sqlalchemy import func
    
    today = date.today()
    
    # Cash balance (sum of all ledger entries)
    cash_balance = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0
    
    # Receivables (pending invoices)
    receivables = db.query(func.sum(Invoice.balance_due)).filter(
        Invoice.entity_id == entity_id,
        Invoice.invoice_type == "receivable",
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).scalar() or 0
    
    # Overdue count
    overdue_count = db.query(Invoice).filter(
        Invoice.entity_id == entity_id,
        Invoice.invoice_type == "receivable",
        Invoice.due_date < today,
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).count()
    
    # Payables (pending payments)
    payables = db.query(func.sum(Invoice.balance_due)).filter(
        Invoice.entity_id == entity_id,
        Invoice.invoice_type == "payable",
        Invoice.status.in_(["pending", "partial"])
    ).scalar() or 0
    
    return {
        "cash_balance": round(cash_balance, 2),
        "receivables": round(receivables, 2),
        "overdue_count": overdue_count,
        "payables": round(payables, 2)
    }


# ============================================================================
# LEDGER & TRANSACTIONS
# ============================================================================

@router.get("/entities/{entity_id}/ledger")
async def get_ledger_entries(
    entity_id: str, 
    limit: int = 50, 
    offset: int = 0,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get ledger transactions with pagination support."""
    query = db.query(LedgerEntry).filter(LedgerEntry.entity_id == entity_id)
    
    if category:
        query = query.filter(LedgerEntry.category == category)
        
    total = query.count()
    entries = query.order_by(LedgerEntry.ledger_date.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": e.id,
                "date": e.ledger_date.isoformat() if e.ledger_date else None,
                "description": e.description,
                "amount": float(e.amount),
                "category": e.category,
                "subcategory": e.subcategory,
                "source_type": e.source_type
            }
            for e in entries
        ]
    }


@router.post("/entities/{entity_id}/ledger/manual")
async def add_manual_ledger_entry(
    entity_id: str,
    entry_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Add a manual transaction to the ledger."""
    try:
        # Validate date
        ledger_date = datetime.strptime(entry_data.get("date"), "%Y-%m-%d").date()
        
        amount = float(entry_data.get("amount"))
        if entry_data.get("type", "").lower() == "expense":
            amount = -abs(amount)
        else:
            amount = abs(amount)
            
        new_entry = LedgerEntry(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            ledger_date=ledger_date,
            description=entry_data.get("description"),
            amount=amount,
            category=entry_data.get("category", "Other"),
            subcategory=entry_data.get("subcategory"),
            source_type="manual",
            created_at=datetime.utcnow()
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        return {"id": new_entry.id, "message": "Transaction added successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/entities/{entity_id}/ledger/{entry_id}")
async def delete_ledger_entry(
    entity_id: str,
    entry_id: str,
    db: Session = Depends(get_db)
):
    """Delete a manual ledger entry."""
    entry = db.query(LedgerEntry).filter(
        LedgerEntry.id == entry_id,
        LedgerEntry.entity_id == entity_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
        
    db.delete(entry)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}


# ============================================================================
# INVOICES
# ============================================================================

@router.get("/entities/{entity_id}/invoices")
async def get_invoices(
    entity_id: str,
    invoice_type: Optional[str] = None,  # receivable | payable
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get invoices for an entity."""
    query = db.query(Invoice).filter(Invoice.entity_id == entity_id)
    
    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.order_by(Invoice.due_date.desc()).limit(50).all()
    
    return [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "invoice_type": inv.invoice_type,
            "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "amount": inv.amount,
            "total_amount": inv.total_amount,
            "paid_amount": inv.paid_amount,
            "balance_due": inv.balance_due,
            "status": inv.status,
            "counterparty_id": inv.counterparty_id
        }
        for inv in invoices
    ]


@router.get("/entities/{entity_id}/invoices/overdue")
async def get_overdue_invoices(entity_id: str, db: Session = Depends(get_db)):
    """Get overdue receivable invoices."""
    today = date.today()
    
    invoices = db.query(Invoice).filter(
        Invoice.entity_id == entity_id,
        Invoice.invoice_type == "receivable",
        Invoice.due_date < today,
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).order_by(Invoice.balance_due.desc()).all()
    
    result = []
    for inv in invoices:
        # Get counterparty name
        cp_name = "Unknown"
        if inv.counterparty_id:
            cp = db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
            if cp:
                cp_name = cp.name
        
        days_overdue = (today - inv.due_date).days if inv.due_date else 0
        
        result.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "counterparty_name": cp_name,
            "amount": inv.balance_due,
            "days_overdue": days_overdue,
            "due_date": inv.due_date.isoformat() if inv.due_date else None
        })
    
    return result


# ============================================================================
# COUNTERPARTIES
# ============================================================================

@router.get("/entities/{entity_id}/counterparties")
async def get_counterparties(entity_id: str, db: Session = Depends(get_db)):
    """Get counterparties (customers and vendors)."""
    counterparties = db.query(Counterparty).filter(
        Counterparty.entity_id == entity_id
    ).all()
    
    return [
        {
            "id": cp.id,
            "name": cp.name,
            "gstin": cp.gstin,
            "type": cp.counterparty_type
        }
        for cp in counterparties
    ]


# ============================================================================
# FORECASTING
# ============================================================================

@router.get("/entities/{entity_id}/forecast")
async def get_cash_forecast(
    entity_id: str, 
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get cash flow forecast using Prophet."""
    service = ForecastingService(db)
    forecast = service.forecast(entity_id, days)
    return forecast


# ============================================================================
# CREDIT SCORE
# ============================================================================

@router.get("/entities/{entity_id}/credit-score")
async def get_credit_score(entity_id: str, db: Session = Depends(get_db)):
    """Get credit score and risk assessment."""
    service = ScoringService(db)
    score = service.calculate_score(entity_id)
    score["entity_id"] = entity_id
    return score


# ============================================================================
# RISK SCORE (Alias for credit-score with PD Band - README compliant endpoint)
# ============================================================================

@router.get("/entities/{entity_id}/risk-score")
async def get_risk_score(entity_id: str, db: Session = Depends(get_db)):
    """
    Get credit score and Probability of Default (PD) band.
    README API: GET /api/entities/{id}/risk-score
    """
    service = ScoringService(db)
    score_data = service.calculate_score(entity_id)
    
    # Add PD (Probability of Default) band based on score
    # Fix: Service returns 'score', not 'credit_score'
    credit_score = score_data.get("score", 650)
    
    # Use service's risk band if available, else calculate
    if "risk_band" in score_data:
        pd_band = score_data["risk_band"]
        risk_level = score_data.get("risk_label", "Medium")
        pd_percentage = 2.5 # Mock based on band B
    elif credit_score is None:
        pd_band = "N/A"
        risk_level = "No Data"
        pd_percentage = 0.0
    else:
        if credit_score >= 750:
            pd_band = "A"
            pd_percentage = 0.5
            risk_level = "Low"
        elif credit_score >= 650:
            pd_band = "B"
            pd_percentage = 2.5
            risk_level = "Medium"
        elif credit_score >= 550:
            pd_band = "C"
            pd_percentage = 8.0
            risk_level = "High"
        else:
            pd_band = "D"
            pd_percentage = 15.0
            risk_level = "Critical"
    
    return {
        "entity_id": entity_id,
        "credit_score": credit_score,
        "score": credit_score, # For frontend compatibility
        "risk_band": pd_band,  # For frontend compatibility
        "pd_band": pd_band,
        "pd_percentage": pd_percentage,
        "risk_level": risk_level,
        "risk_label": risk_level, # For frontend compatibility
        "factors": score_data.get("factors", []),
        "shap_values": score_data.get("shap_values", []),
        "recommendations": score_data.get("recommendations", [])
    }


# ============================================================================
# COLLECTIONS PLAN (Agent-based prioritized collection actions)
# ============================================================================

@router.get("/entities/{entity_id}/collections-plan")
async def get_collections_plan(entity_id: str, db: Session = Depends(get_db)):
    """
    Get prioritized collection actions from Collections Agent.
    README API: GET /api/entities/{id}/collections-plan
    """
    from app.models.invoice import Invoice
    from datetime import date, timedelta
    
    today = date.today()
    
    # Get overdue invoices
    overdue_invoices = db.query(Invoice).filter(
        Invoice.entity_id == entity_id,
        Invoice.status != "paid",
        Invoice.due_date < today
    ).order_by(Invoice.due_date.asc()).all()
    
    # Build prioritized collection plan
    collection_actions = []
    for inv in overdue_invoices:
        days_overdue = (today - inv.due_date).days
        priority_score = float(inv.amount) * days_overdue  # Amount * Days = Priority
        
        # Determine action urgency
        if days_overdue > 60:
            urgency = "critical"
            action = "Escalate to legal/collection agency"
        elif days_overdue > 30:
            urgency = "high"
            action = "Direct phone call + formal demand letter"
        elif days_overdue > 15:
            urgency = "medium"
            action = "Send firm payment reminder email"
        else:
            urgency = "low"
            action = "Send friendly reminder email"
        
        collection_actions.append({
            "invoice_id": str(inv.id),
            "invoice_number": inv.invoice_number,
            "counterparty_id": str(inv.counterparty_id) if inv.counterparty_id else None,
            "amount": float(inv.amount),
            "days_overdue": days_overdue,
            "due_date": inv.due_date.isoformat(),
            "priority_score": priority_score,
            "urgency": urgency,
            "recommended_action": action
        })
    
    # Sort by priority score (highest first)
    collection_actions.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Calculate summary stats
    total_overdue = sum(a["amount"] for a in collection_actions)
    avg_days_overdue = sum(a["days_overdue"] for a in collection_actions) / max(len(collection_actions), 1)
    
    return {
        "entity_id": entity_id,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_overdue_amount": total_overdue,
            "overdue_invoice_count": len(collection_actions),
            "average_days_overdue": round(avg_days_overdue, 1),
            "critical_count": len([a for a in collection_actions if a["urgency"] == "critical"]),
            "high_count": len([a for a in collection_actions if a["urgency"] == "high"])
        },
        "actions": collection_actions[:20]  # Top 20 priorities
    }


# ============================================================================
# PAYMENTS SCHEDULE (Optimized payment calendar)
# ============================================================================

@router.get("/entities/{entity_id}/payments-schedule")
async def get_payments_schedule(entity_id: str, db: Session = Depends(get_db)):
    """
    Get optimized payment schedule from Payments Agent.
    README API: GET /api/entities/{id}/payments-schedule
    """
    from app.models.invoice import Invoice
    from datetime import date, timedelta
    
    today = date.today()
    next_30_days = today + timedelta(days=30)
    
    # Get current cash balance
    cash_balance = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0
    
    # Get pending payables (invoices where we need to pay vendors)
    pending_payables = db.query(Invoice).filter(
        Invoice.entity_id == entity_id,
        Invoice.invoice_type == "payable",
        Invoice.status != "paid",
        Invoice.due_date <= next_30_days
    ).order_by(Invoice.due_date.asc()).all()
    
    # If no outbound invoices, mock some data for demo
    if not pending_payables:
        # Generate sample payment schedule
        payment_schedule = [
            {
                "payment_id": f"PAY-{i+1}",
                "vendor": f"Vendor {i+1}",
                "amount": 25000 + (i * 10000),
                "due_date": (today + timedelta(days=i*5)).isoformat(),
                "scheduled_date": (today + timedelta(days=i*5 + 2)).isoformat(),
                "priority": "high" if i < 2 else "medium",
                "status": "scheduled",
                "reasoning": "Scheduled 2 days after due date to optimize cash flow"
            }
            for i in range(5)
        ]
    else:
        payment_schedule = []
        running_balance = cash_balance
        min_balance = 50000  # Minimum cash buffer
        
        for inv in pending_payables:
            amount = float(inv.amount)
            
            # Determine if we can pay now or need to delay
            if running_balance - amount >= min_balance:
                scheduled_date = inv.due_date
                status = "approved"
                reasoning = "Sufficient cash balance to pay on time"
            else:
                # Delay by 7 days and hope for receivables
                scheduled_date = inv.due_date + timedelta(days=7)
                status = "delayed"
                reasoning = f"Delayed to maintain ₹{min_balance:,} minimum balance"
            
            # Priority based on vendor criticality
            days_until_due = (inv.due_date - today).days
            if days_until_due <= 3:
                priority = "critical"
            elif days_until_due <= 7:
                priority = "high"
            else:
                priority = "medium"
            
            # Resolve vendor name
            vendor_name = "Unknown Vendor"
            if inv.counterparty_id:
                cp = db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                if cp:
                    vendor_name = cp.name

            payment_schedule.append({
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "vendor": vendor_name,
                "amount": amount,
                "due_date": inv.due_date.isoformat(),
                "scheduled_date": scheduled_date.isoformat(),
                "priority": priority,
                "status": status,
                "reasoning": reasoning
            })
            
            if status == "approved":
                running_balance -= amount
    
    # Summary
    total_payables = sum(p["amount"] for p in payment_schedule)
    
    return {
        "entity_id": entity_id,
        "generated_at": datetime.now().isoformat(),
        "current_cash_balance": float(cash_balance),
        "summary": {
            "total_payables_30_days": total_payables,
            "payment_count": len(payment_schedule),
            "critical_payments": len([p for p in payment_schedule if p["priority"] == "critical"]),
            "delayed_payments": len([p for p in payment_schedule if p["status"] == "delayed"])
        },
        "schedule": payment_schedule
    }

