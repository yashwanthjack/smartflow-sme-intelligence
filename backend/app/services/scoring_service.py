# Credit Scoring Service - Risk assessment using XGBoost or heuristics
from typing import Dict, Any, Optional, Tuple, List
from datetime import date, timedelta
from dataclasses import dataclass
import numpy as np

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from sqlalchemy.orm import Session
from sqlalchemy import func


@dataclass
class CreditFeatures:
    """Features used for credit scoring."""
    avg_daily_balance: float = 0.0
    balance_volatility: float = 0.0  # Coefficient of variation
    inflow_consistency: float = 0.0  # % of days with positive inflow
    avg_days_to_collect: float = 0.0  # DSO approximation
    gst_compliance_rate: float = 0.0  # % of on-time GST filings
    bounce_rate: float = 0.0  # % of bounced transactions
    revenue_trend: float = 0.0  # Month-over-month growth
    top_customer_concentration: float = 0.0  # Revenue from top 3 customers


class ScoringService:
    """
    Credit scoring service for SME risk assessment.
    Uses XGBoost if available, otherwise falls back to rule-based heuristics.
    
    Score Range: 300 (highest risk) to 900 (lowest risk)
    Risk Bands:
        - A++ (850-900): Excellent
        - A (750-849): Low Risk
        - B (650-749): Medium Risk
        - C (500-649): High Risk
        - D (300-499): Very High Risk
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.model = None  # XGBoost model (if trained)
    
    def compute_features(self, entity_id: str, days: int = 90) -> CreditFeatures:
        """
        Extract credit-relevant features from financial data.
        """
        if self.db is None:
            return self._get_mock_features()
        
        from app.models.ledger_entry import LedgerEntry
        from app.models.invoice import Invoice
        
        cutoff_date = date.today() - timedelta(days=days)
        
        # Query ledger entries
        ledger_entries = (
            self.db.query(LedgerEntry)
            .filter(LedgerEntry.entity_id == entity_id)
            .filter(LedgerEntry.ledger_date >= cutoff_date)
            .all()
        )
        
        if not ledger_entries:
            return self._get_mock_features()
        
        # Calculate features
        amounts = [e.amount for e in ledger_entries]
        inflows = [a for a in amounts if a > 0]
        
        # Balance statistics
        avg_balance = np.mean(amounts) if amounts else 0
        balance_volatility = np.std(amounts) / avg_balance if avg_balance != 0 else 0
        
        # Inflow consistency
        daily_inflows = {}
        for e in ledger_entries:
            if e.amount > 0:
                daily_inflows[e.ledger_date] = daily_inflows.get(e.ledger_date, 0) + e.amount
        inflow_consistency = len(daily_inflows) / days if days > 0 else 0
        
        # DSO from invoices
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.entity_id == entity_id)
            .filter(Invoice.invoice_type == "receivable")
            .filter(Invoice.status.in_(["paid", "partial"]))
            .all()
        )
        
        if invoices:
            collection_days = []
            for inv in invoices:
                if inv.invoice_date and inv.updated_at:
                    days_to_collect = (inv.updated_at.date() - inv.invoice_date).days
                    collection_days.append(max(0, days_to_collect))
            avg_dso = np.mean(collection_days) if collection_days else 45
        else:
            avg_dso = 45  # Default
        
        return CreditFeatures(
            avg_daily_balance=avg_balance,
            balance_volatility=balance_volatility,
            inflow_consistency=inflow_consistency,
            avg_days_to_collect=avg_dso,
            gst_compliance_rate=0.95,  # TODO: Integrate with GSTSummary
            bounce_rate=0.02,  # TODO: Integrate with bank data
            revenue_trend=0.05,  # TODO: Calculate MoM growth
            top_customer_concentration=0.4  # TODO: Calculate from counterparty data
        )
    
    def _get_mock_features(self) -> CreditFeatures:
        """Generate mock features for testing."""
        return CreditFeatures(
            avg_daily_balance=75000,
            balance_volatility=0.25,
            inflow_consistency=0.7,
            avg_days_to_collect=42,
            gst_compliance_rate=0.92,
            bounce_rate=0.03,
            revenue_trend=0.08,
            top_customer_concentration=0.45
        )
    
    def calculate_score(self, entity_id: str) -> Dict[str, Any]:
        """
        Calculate credit score for an entity.
        
        Returns:
            dict with score, risk_band, factors, and recommendations
        """
        features = self.compute_features(entity_id)
        
        if XGBOOST_AVAILABLE and self.model is not None:
            return self._xgboost_score(features)
        else:
            return self._heuristic_score(features)
    
    def _heuristic_score(self, features: CreditFeatures) -> Dict[str, Any]:
        """
        Rule-based credit scoring using weighted factors.
        This is a transparent, explainable approach suitable for SMEs.
        """
        # Initialize base score
        base_score = 600
        adjustments = []
        
        # Factor 1: Balance Volatility (weight: 15%)
        # Lower volatility = higher score
        if features.balance_volatility < 0.2:
            adj = 45
            adjustments.append({'factor': 'Stable cash flow', 'impact': f'+{adj}', 'positive': True})
        elif features.balance_volatility < 0.4:
            adj = 15
            adjustments.append({'factor': 'Moderate cash flow stability', 'impact': f'+{adj}', 'positive': True})
        elif features.balance_volatility > 0.6:
            adj = -30
            adjustments.append({'factor': 'High cash flow volatility', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Factor 2: Inflow Consistency (weight: 20%)
        if features.inflow_consistency > 0.8:
            adj = 60
            adjustments.append({'factor': 'Consistent daily inflows', 'impact': f'+{adj}', 'positive': True})
        elif features.inflow_consistency > 0.5:
            adj = 20
            adjustments.append({'factor': 'Regular inflows', 'impact': f'+{adj}', 'positive': True})
        elif features.inflow_consistency < 0.3:
            adj = -40
            adjustments.append({'factor': 'Irregular revenue pattern', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Factor 3: Days Sales Outstanding (weight: 20%)
        if features.avg_days_to_collect < 30:
            adj = 60
            adjustments.append({'factor': 'Fast collections (DSO < 30)', 'impact': f'+{adj}', 'positive': True})
        elif features.avg_days_to_collect < 45:
            adj = 30
            adjustments.append({'factor': 'Good collections (DSO < 45)', 'impact': f'+{adj}', 'positive': True})
        elif features.avg_days_to_collect > 60:
            adj = -45
            adjustments.append({'factor': 'Slow collections (DSO > 60)', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Factor 4: GST Compliance (weight: 15%)
        if features.gst_compliance_rate >= 0.95:
            adj = 45
            adjustments.append({'factor': 'Excellent GST compliance', 'impact': f'+{adj}', 'positive': True})
        elif features.gst_compliance_rate >= 0.8:
            adj = 15
            adjustments.append({'factor': 'Good GST compliance', 'impact': f'+{adj}', 'positive': True})
        elif features.gst_compliance_rate < 0.6:
            adj = -60
            adjustments.append({'factor': 'Poor GST compliance', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Factor 5: Bounce Rate (weight: 15%)
        if features.bounce_rate < 0.02:
            adj = 45
            adjustments.append({'factor': 'Very low bounce rate', 'impact': f'+{adj}', 'positive': True})
        elif features.bounce_rate < 0.05:
            adj = 15
            adjustments.append({'factor': 'Low bounce rate', 'impact': f'+{adj}', 'positive': True})
        elif features.bounce_rate > 0.1:
            adj = -60
            adjustments.append({'factor': 'High bounce rate (>10%)', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Factor 6: Customer Concentration (weight: 15%)
        if features.top_customer_concentration < 0.3:
            adj = 45
            adjustments.append({'factor': 'Diversified customer base', 'impact': f'+{adj}', 'positive': True})
        elif features.top_customer_concentration > 0.6:
            adj = -30
            adjustments.append({'factor': 'High customer concentration', 'impact': f'{adj}', 'positive': False})
        else:
            adj = 0
        base_score += adj
        
        # Clamp score to valid range
        final_score = max(300, min(900, base_score))
        
        # Determine risk band
        risk_band = self._get_risk_band(final_score)
        
        return {
            'entity_id': 'unknown',
            'score': final_score,
            'risk_band': risk_band['band'],
            'risk_label': risk_band['label'],
            'method': 'heuristic',
            'factors': adjustments,
            'features': {
                'avg_daily_balance': features.avg_daily_balance,
                'balance_volatility': round(features.balance_volatility, 3),
                'inflow_consistency': round(features.inflow_consistency, 3),
                'avg_days_to_collect': round(features.avg_days_to_collect, 1),
                'gst_compliance_rate': round(features.gst_compliance_rate, 3),
                'bounce_rate': round(features.bounce_rate, 3),
                'top_customer_concentration': round(features.top_customer_concentration, 3)
            },
            'recommendations': self._get_recommendations(features, final_score),
            'loan_eligibility': self._get_loan_eligibility(final_score, features.avg_daily_balance)
        }
    
    def _xgboost_score(self, features: CreditFeatures) -> Dict[str, Any]:
        """Score using trained XGBoost model."""
        # Convert features to array
        X = np.array([[
            features.avg_daily_balance,
            features.balance_volatility,
            features.inflow_consistency,
            features.avg_days_to_collect,
            features.gst_compliance_rate,
            features.bounce_rate,
            features.revenue_trend,
            features.top_customer_concentration
        ]])
        
        # Predict (model outputs probability of default)
        prob_default = self.model.predict_proba(X)[0][1]
        
        # Convert to score (lower default probability = higher score)
        score = int(900 - (prob_default * 600))
        score = max(300, min(900, score))
        
        risk_band = self._get_risk_band(score)
        
        return {
            'score': score,
            'risk_band': risk_band['band'],
            'risk_label': risk_band['label'],
            'method': 'xgboost',
            'probability_of_default': round(prob_default, 4)
        }
    
    def _get_risk_band(self, score: int) -> Dict[str, str]:
        """Map score to risk band."""
        if score >= 850:
            return {'band': 'A++', 'label': 'Excellent'}
        elif score >= 750:
            return {'band': 'A', 'label': 'Low Risk'}
        elif score >= 650:
            return {'band': 'B', 'label': 'Medium Risk'}
        elif score >= 500:
            return {'band': 'C', 'label': 'High Risk'}
        else:
            return {'band': 'D', 'label': 'Very High Risk'}
    
    def _get_recommendations(self, features: CreditFeatures, score: int) -> List[str]:
        """Generate actionable recommendations to improve score."""
        recommendations = []
        
        if features.avg_days_to_collect > 45:
            recommendations.append("Reduce DSO by implementing stricter collection policies")
        
        if features.balance_volatility > 0.4:
            recommendations.append("Stabilize cash flow by negotiating payment terms with suppliers")
        
        if features.gst_compliance_rate < 0.9:
            recommendations.append("Improve GST filing consistency to build compliance history")
        
        if features.top_customer_concentration > 0.5:
            recommendations.append("Diversify customer base to reduce concentration risk")
        
        if features.bounce_rate > 0.05:
            recommendations.append("Address bounced transactions to improve payment reliability")
        
        if not recommendations:
            recommendations.append("Maintain current financial discipline to preserve strong credit standing")
        
        return recommendations
    
    def _get_loan_eligibility(self, score: int, avg_balance: float) -> Dict[str, Any]:
        """Estimate loan eligibility based on score and financials."""
        if score >= 750:
            multiplier = 8
            rate_range = "10-12%"
        elif score >= 650:
            multiplier = 5
            rate_range = "12-15%"
        elif score >= 500:
            multiplier = 3
            rate_range = "15-18%"
        else:
            multiplier = 0
            rate_range = "N/A"
        
        max_working_capital = avg_balance * 30 * multiplier / 100000  # In lakhs
        
        return {
            'working_capital_limit': f"₹{max_working_capital:.1f} Lakhs" if multiplier > 0 else "Not Eligible",
            'indicative_rate': rate_range,
            'invoice_discounting': "Eligible" if score >= 600 else "Not Eligible",
            'term_loan': "Eligible" if score >= 700 else "Limited"
        }


# Convenience function
def get_credit_score(entity_id: str, db: Session = None) -> Dict[str, Any]:
    """Get credit score for an entity."""
    service = ScoringService(db)
    return service.calculate_score(entity_id)
