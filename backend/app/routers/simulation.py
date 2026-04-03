# Scenario Simulation Router
# Adapted from JACK project - provides hiring/expense impact analysis

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.db.database import get_db
from app.models.ledger_entry import LedgerEntry
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["Simulation"])


class ScenarioInput(BaseModel):
    """Input parameters for scenario simulation."""
    hiring_count: int = 0
    monthly_salary_per_hire: float = 80000  # ₹80k default for Indian market
    marketing_increase_percent: float = 0
    revenue_growth_percent: float = 0
    one_time_expense: float = 0


class ProjectionPoint(BaseModel):
    """Single point in the projection series."""
    month: str
    balance: float
    burn: float
    threshold: float = 500000  # Safety threshold line


class ScenarioResult(BaseModel):
    """Result of scenario simulation."""
    current_runway_months: float
    new_runway_months: float
    current_monthly_burn: float
    new_monthly_burn: float
    risk_level: str  # Low, Moderate, High, Critical
    status: str  # SAFE, WARN, BLOCK
    impact_summary: str
    ai_recommendation: str
    projection_series: List[ProjectionPoint]


def calculate_runway(balance: float, burn: float) -> float:
    """Calculate runway in months."""
    if burn <= 0:
        return 99.9
    return round(balance / burn, 1)


def get_risk_level(runway: float) -> tuple[str, str]:
    """Determine risk level and status based on runway."""
    if runway < 3:
        return "Critical", "BLOCK"
    elif runway < 6:
        return "High", "WARN"
    elif runway < 12:
        return "Moderate", "SAFE"
    else:
        return "Low", "SAFE"


def generate_recommendation(scenario: ScenarioInput, current_runway: float, new_runway: float) -> str:
    """Generate AI-style recommendation based on scenario impact."""
    
    if new_runway < 3:
        return "🛑 **Critical Action Needed**: This decision would reduce runway to dangerous levels. Pause all non-essential expenses immediately. Consider fundraising or revenue acceleration."
    
    if scenario.hiring_count > 2 and new_runway < 8:
        return f"⚠️ **Caution**: Hiring {scenario.hiring_count} people drops runway to {new_runway:.1f} months. Consider staggering hires: hire 1 now, rest in next quarter."
    
    if scenario.marketing_increase_percent > 20 and scenario.revenue_growth_percent < 5:
        return "💡 **Optimization**: High marketing spend without corresponding revenue growth. Verify CAC efficiency before scaling spend."
    
    if new_runway > 12:
        return "✅ **Safe to Proceed**: Strong runway maintained. You have capital headroom for this investment."
    
    runway_impact = current_runway - new_runway
    if runway_impact > 3:
        return f"⚠️ **Significant Impact**: This reduces runway by {runway_impact:.1f} months. Ensure this investment has clear ROI within 6 months."
    
    return "✅ Runway remains healthy. Monitor monthly burn rate post-implementation."


@router.post("", response_model=ScenarioResult)
async def run_scenario(
    scenario: ScenarioInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run a financial scenario simulation.
    
    Calculates impact of hiring, marketing spend, and revenue changes on runway.
    Provides 12-month cash projection and risk assessment.
    """
    entity_id = current_user.entity_id
    if not entity_id:
        raise HTTPException(status_code=400, detail="User must be linked to an organization")
    
    # Get current financial state
    today = date.today()
    six_months_ago = today - timedelta(days=180)
    
    # Calculate current cash balance
    cash_balance = float(db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0)
    
    # Calculate average monthly burn (last 6 months expenses)
    total_expenses = float(db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0,
        LedgerEntry.ledger_date >= six_months_ago
    ).scalar() or 0)
    
    current_burn = abs(total_expenses) / 6 if total_expenses else 50000.0  # Default ₹50k if no data
    current_runway = calculate_runway(cash_balance, current_burn)
    
    # Calculate scenario impact
    hiring_cost = scenario.hiring_count * scenario.monthly_salary_per_hire
    
    # Marketing as % of current burn (assume 10% is marketing baseline)
    marketing_delta = (current_burn * 0.10) * (scenario.marketing_increase_percent / 100)
    
    # Revenue offset (assume 50% of burn is from revenue)
    revenue_offset = (current_burn * 0.5) * (scenario.revenue_growth_percent / 100)
    
    # New burn rate
    new_burn = current_burn + hiring_cost + marketing_delta - revenue_offset
    
    # Apply one-time expense to cash
    adjusted_cash = cash_balance - scenario.one_time_expense
    
    # New runway
    new_runway = calculate_runway(adjusted_cash, new_burn)
    
    # Risk assessment
    risk_level, status = get_risk_level(new_runway)
    
    # Monte Carlo Simulation
    # Run 1000 simulations with random variations in burn and revenue
    simulations = []
    
    import numpy as np
    
    for _ in range(1000):
        sim_balance = adjusted_cash
        sim_path = []
        
        # Add random noise to monthly burn (±10%) and revenue (±15%)
        # Identify base components
        base_burn = current_burn + hiring_cost + marketing_delta - revenue_offset
        
        for month in range(1, 13):
            # Randomize monthly fluctuation
            # Burn might vary by 5-10%
            monthly_burn_noise = np.random.normal(0, base_burn * 0.05) 
            # Revenue/Collections might vary by 10-15% (affecting net burn)
            # We treat 'burn' as net outflow here
            
            simulated_burn = base_burn + monthly_burn_noise
            sim_balance -= simulated_burn
            
            if sim_balance < 0:
                sim_balance = 0
            
            sim_path.append(sim_balance)
        
        simulations.append(sim_path)
    
    # Calculate median path for projection
    simulations_array = np.array(simulations)
    median_path = np.median(simulations_array, axis=0)
    p10_path = np.percentile(simulations_array, 10, axis=0) # Pessimistic
    
    # Generate 12-month projection from median
    projection = []
    for i, balance in enumerate(median_path):
         projection.append(ProjectionPoint(
            month=f"Month {i+1}",
            balance=round(float(balance), 0),
            burn=round(new_burn, 0),
            threshold=500000
        ))

    # Recalculate runway based on Monte Carlo (P10 - conservative)
    # If P10 hits 0 at month X, that's the conservative runway
    conservative_runway = 12.0
    for i, bal in enumerate(p10_path):
        if bal <= 0:
            conservative_runway = float(i) + (p10_path[i-1] / (p10_path[i-1] - bal)) if i > 0 else 0.0
            break
            
    # If conservative runway is still > 12, check linear
    if conservative_runway >= 12 and new_burn > 0:
        conservative_runway = calculate_runway(adjusted_cash, new_burn)

    # Use conservative runway for risk assessment
    risk_runway = conservative_runway
    
    # Generate recommendation using conservative estimates from Monte Carlo
    recommendation = generate_recommendation(scenario, current_runway, risk_runway)
    
    # Impact summary
    runway_change = current_runway - new_runway
    impact = f"Runway changes from {current_runway:.1f} to {new_runway:.1f} months ({'-' if runway_change > 0 else '+'}{abs(runway_change):.1f} months)"
    
    return ScenarioResult(
        current_runway_months=current_runway,
        new_runway_months=new_runway,
        current_monthly_burn=round(current_burn, 2),
        new_monthly_burn=round(new_burn, 2),
        risk_level=risk_level,
        status=status,
        impact_summary=impact,
        ai_recommendation=recommendation,
        projection_series=projection
    )


@router.get("/quick-check")
async def quick_hire_check(
    count: int = 1,
    salary: float = 80000,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Quick check: What happens if I hire N people at salary X?"""
    scenario = ScenarioInput(
        hiring_count=count,
        monthly_salary_per_hire=salary
    )
    return await run_scenario(scenario, current_user, db)


@router.get("/live")
async def live_scenario(
    hiring_count: int = 0,
    salary: float = 80000,
    marketing_pct: float = 0,
    revenue_pct: float = 0,
    one_time: float = 0,
    loan_amount: float = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Lightweight real-time scenario endpoint for interactive sliders.
    Uses deterministic linear projection (no Monte Carlo) for <100ms response.
    """
    entity_id = current_user.entity_id
    if not entity_id:
        raise HTTPException(status_code=400, detail="User must be linked to an organization")

    today = date.today()
    six_months_ago = today - timedelta(days=180)

    # Current cash balance
    cash_balance = float(db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id
    ).scalar() or 0)

    # Average monthly burn (last 6 months)
    total_expenses = float(db.query(func.sum(LedgerEntry.amount)).filter(
        LedgerEntry.entity_id == entity_id,
        LedgerEntry.amount < 0,
        LedgerEntry.ledger_date >= six_months_ago
    ).scalar() or 0)

    current_burn = abs(total_expenses) / 6 if total_expenses else 50000.0

    # Calculate new burn
    hiring_cost = hiring_count * salary
    marketing_delta = (current_burn * 0.10) * (marketing_pct / 100)
    revenue_offset = (current_burn * 0.5) * (revenue_pct / 100)
    new_burn = current_burn + hiring_cost + marketing_delta - revenue_offset

    # Adjusted cash (one-time expense + loan injection)
    adjusted_cash = cash_balance - one_time + loan_amount

    # Current and new runway
    current_runway = calculate_runway(cash_balance, current_burn)
    new_runway = calculate_runway(adjusted_cash, new_burn)

    risk_level, status = get_risk_level(new_runway)

    # Simple 12-month linear projection (fast, no numpy)
    baseline_projection = []
    scenario_projection = []
    baseline_bal = cash_balance
    scenario_bal = adjusted_cash

    for month in range(1, 13):
        baseline_bal -= current_burn
        scenario_bal -= new_burn
        baseline_projection.append({
            "month": f"Month {month}",
            "baseline": round(max(baseline_bal, 0), 0),
            "scenario": round(max(scenario_bal, 0), 0),
            "threshold": 500000,
        })

    recommendation = generate_recommendation(
        ScenarioInput(
            hiring_count=hiring_count,
            monthly_salary_per_hire=salary,
            marketing_increase_percent=marketing_pct,
            revenue_growth_percent=revenue_pct,
            one_time_expense=one_time,
        ),
        current_runway,
        new_runway,
    )

    return {
        "current_runway": round(current_runway, 1),
        "new_runway": round(new_runway, 1),
        "current_burn": round(current_burn, 0),
        "new_burn": round(new_burn, 0),
        "cash_balance": round(cash_balance, 0),
        "adjusted_cash": round(adjusted_cash, 0),
        "risk_level": risk_level,
        "status": status,
        "recommendation": recommendation,
        "projection": baseline_projection,
    }
