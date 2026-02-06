from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User
from app.models.ledger_entry import LedgerEntry
from app.models.counterparty import Counterparty
from app.models.invoice import Invoice
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/data/metrics",
    tags=["metrics"]
)

@router.get("/summary/{entity_id}")
def get_summary_metrics(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get top-level metrics: Bank Balance, Net Burn, Runway, Net Income.
    """
    # 1. Bank Balance (Sum of all transactions)
    balance = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.entity_id == entity_id).scalar() or 0
    
    # 2. Net Burn (Avg monthly outflow last 3 months)
    three_months_ago = datetime.now() - timedelta(days=90)
    total_outflow = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0,
        LedgerEntry.ledger_date >= three_months_ago
    ).scalar() or 0
    monthly_burn = abs(total_outflow) / 3 if total_outflow else 0
    
    # 3. Runway
    runway_months = (balance / monthly_burn) if monthly_burn > 0 else 999
    
    # 4. Net Income (Last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    net_income = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.ledger_date >= thirty_days_ago
    ).scalar() or 0
    
    return {
        "bank_balance": balance,
        "net_burn": monthly_burn,
        "runway_months": runway_months,
        "net_income": net_income
    }

@router.get("/gross-volume/{entity_id}")
def get_gross_volume(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Gross Volume metrics broken down by subcategory.
    """
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Total Volume (All Inflows)
    total_volume = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount > 0,
        LedgerEntry.ledger_date >= thirty_days_ago
    ).scalar() or 0
    
    # Breakdown by subcategory
    breakdown_query = db.query(
        LedgerEntry.subcategory,
        func.sum(LedgerEntry.amount)
    ).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount > 0,
        LedgerEntry.ledger_date >= thirty_days_ago
    ).group_by(LedgerEntry.subcategory).all()
    
    breakdown = [
        {"label": cat or "Other", "value": val, "color": _get_color_for_cat(cat)} 
        for cat, val in breakdown_query if val > 0
    ]
    
    return {
        "totalVolume": total_volume,
        "change": 15, # Mocked change for now
        "breakdown": breakdown
    }

@router.get("/waterfall/{entity_id}")
def get_payments_waterfall(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get payments waterfall (Initiated -> Authorized -> Successful).
    Since we don't have granular transaction states in Ledger, we simulate reliable ratios based on real volume.
    """
    # Base real volume
    thirty_days_ago = datetime.now() - timedelta(days=30)
    successful_volume = db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount > 0,
        LedgerEntry.category == 'revenue',
        LedgerEntry.ledger_date >= thirty_days_ago
    ).scalar() or 0
    
    # extrapolating funnel
    return [
        {"label": "Initiated", "value": successful_volume * 1.4},
        {"label": "Authorized", "value": successful_volume * 1.25},
        {"label": "Successful", "value": successful_volume},
        {"label": "Payouts", "value": successful_volume * 0.95}, # Platform fees
        {"label": "Completed", "value": successful_volume * 0.95}
    ]

@router.get("/customers/{entity_id}")
def get_customer_metrics(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Customer count and new additions.
    """
    total_customers = db.query(func.count(Counterparty.id)).filter(
        Counterparty.entity_id == entity_id,
        Counterparty.counterparty_type == 'customer'
    ).scalar()
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_customers = db.query(func.count(Counterparty.id)).filter(
        Counterparty.entity_id == entity_id,
        Counterparty.counterparty_type == 'customer',
        Counterparty.created_at >= thirty_days_ago
    ).scalar()
    
    return {
        "total_customers": total_customers,
        "new_customers": new_customers,
        "growth_pct": round((new_customers / total_customers * 100), 1) if total_customers else 0
    }

def _get_color_for_cat(cat):
    if cat == 'online': return 'green'
    if cat == 'invoice': return 'blue'
    if cat == 'subscription': return 'purple'
    return 'gray'
