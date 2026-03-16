from typing import Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.forecasting_service import ForecastingService
from app.services.scoring_service import ScoringService


class HealthService:
    """
    Calculates a composite 'Health Pulse' score (0-100) for the business.
    Aggregates: Runway, Burn Trend, Credit Score, and DSO.
    All values are computed from real ledger data.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.forecast_service = ForecastingService(db)
        self.scoring_service = ScoringService(db)

    def calculate_health_pulse(self, entity_id: str) -> Dict[str, Any]:
        from app.models.ledger_entry import LedgerEntry
        
        today = date.today()
        
        # ─── 1. Runway Score (30%) ───────────────────────────────────
        # Calculate from real cash balance and burn rate
        cash_balance = self.db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id
        ).scalar() or 0
        
        three_months_ago = today - timedelta(days=90)
        total_outflow = self.db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id,
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= three_months_ago
        ).scalar() or 0
        
        monthly_burn = abs(total_outflow) / 3 if total_outflow else 0
        runway_months = (cash_balance / monthly_burn) if monthly_burn > 0 else 999
        
        # Runway > 12mo = 100, 6mo = 75, 3mo = 50, <1mo = 10
        if runway_months >= 12:
            runway_score = 100
        elif runway_months >= 6:
            runway_score = 50 + (runway_months - 6) * (50 / 6)
        elif runway_months >= 3:
            runway_score = 25 + (runway_months - 3) * (25 / 3)
        elif runway_months >= 1:
            runway_score = 10 + (runway_months - 1) * (15 / 2)
        else:
            runway_score = max(0, runway_months * 10)
        
        # ─── 2. Credit Score Component (20%) ─────────────────────────
        credit_data = self.scoring_service.calculate_score(entity_id)
        features = credit_data.get('features', {})
        credit_score = credit_data.get('score', 600)
        credit_component = (credit_score - 300) / 600 * 100  # Normalize 300-900 to 0-100
        
        # ─── 3. DSO Score (25%) ──────────────────────────────────────
        # Target DSO < 45. If 30 -> 100, if 90 -> 0
        dso = features.get('avg_days_to_collect', 45)
        dso_score = max(0, min(100, 100 - (dso - 30) * (100 / 60)))
        
        # ─── 4. Burn Trend Score (25%) ───────────────────────────────
        # Compare recent 45 days burn vs previous 45 days burn
        forty_five_ago = today - timedelta(days=45)
        ninety_ago = today - timedelta(days=90)
        
        recent_burn = abs(self.db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id,
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= forty_five_ago
        ).scalar() or 0)
        
        older_burn = abs(self.db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.entity_id == entity_id,
            LedgerEntry.amount < 0,
            LedgerEntry.ledger_date >= ninety_ago,
            LedgerEntry.ledger_date < forty_five_ago
        ).scalar() or 0)
        
        if older_burn > 0:
            burn_change = (recent_burn - older_burn) / older_burn
            # Decreasing burn = good (score 80-100), increasing burn = bad (score 20-50)
            if burn_change <= -0.1:
                burn_score = 90  # Burn decreasing significantly
            elif burn_change <= 0:
                burn_score = 80  # Burn stable or slightly decreasing
            elif burn_change <= 0.1:
                burn_score = 65  # Slight increase
            elif burn_change <= 0.3:
                burn_score = 45  # Moderate increase
            else:
                burn_score = 25  # Burn spiking
        else:
            burn_score = 70  # Default neutral if no older data
        
        # ─── Composite Score ─────────────────────────────────────────
        health_score = (
            0.30 * runway_score +
            0.20 * credit_component +
            0.25 * dso_score +
            0.25 * burn_score
        )
        
        if health_score > 80:
            status = "Excellent"
        elif health_score > 60:
            status = "Good"
        elif health_score > 40:
            status = "Fair"
        else:
            status = "At Risk"
        
        return {
            "score": int(health_score),
            "status": status,
            "components": {
                "Runway": int(runway_score),
                "Credit": int(credit_component),
                "DSO": int(dso_score),
                "Efficiency": int(burn_score)
            }
        }
