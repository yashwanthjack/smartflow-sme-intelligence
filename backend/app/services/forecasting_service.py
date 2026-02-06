# Forecasting Service - Cash flow prediction using Prophet
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import pandas as pd

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not installed. Using simple moving average fallback.")

from sqlalchemy.orm import Session
from sqlalchemy import func


class ForecastingService:
    """
    Cash flow forecasting service using Facebook Prophet.
    Falls back to simple moving average if Prophet is not installed.
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def prepare_data_from_ledger(self, entity_id: str) -> pd.DataFrame:
        """
        Prepare time series data from LedgerEntry model.
        Aggregates daily cash flows.
        """
        if self.db is None:
            # Return mock data for testing
            return self._get_mock_data()
        
        from app.models.ledger_entry import LedgerEntry
        
        # Query and aggregate by date
        results = (
            self.db.query(
                LedgerEntry.ledger_date,
                func.sum(LedgerEntry.amount).label('total')
            )
            .filter(LedgerEntry.entity_id == entity_id)
            .group_by(LedgerEntry.ledger_date)
            .order_by(LedgerEntry.ledger_date)
            .all()
        )
        
        if not results:
            return self._get_mock_data()
        
        # Convert to DataFrame with Prophet column names
        df = pd.DataFrame([
            {'ds': r.ledger_date, 'y': float(r.total)}
            for r in results
        ])
        
        return df
    
    def _get_mock_data(self) -> pd.DataFrame:
        """Generate mock cash flow data for testing."""
        import numpy as np
        
        # Generate 90 days of historical data
        dates = pd.date_range(end=date.today(), periods=90)
        
        # Base cash flow with weekly seasonality and trend
        base = 50000  # ₹50k average daily flow
        trend = np.linspace(0, 10000, 90)  # Growing business
        weekly_pattern = np.sin(np.arange(90) * 2 * np.pi / 7) * 15000  # Weekly cycle
        noise = np.random.normal(0, 8000, 90)  # Random variation
        
        values = base + trend + weekly_pattern + noise
        
        return pd.DataFrame({
            'ds': dates,
            'y': values
        })
    
    def forecast(self, entity_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Generate cash flow forecast for the next N days.
        
        Returns:
            dict with forecast data, summary statistics, and alerts
        """
        df = self.prepare_data_from_ledger(entity_id)
        
        if PROPHET_AVAILABLE:
            return self._prophet_forecast(df, days)
        else:
            return self._simple_forecast(df, days)
    
    def _prophet_forecast(self, df: pd.DataFrame, days: int) -> Dict[str, Any]:
        """Generate forecast using Facebook Prophet."""
        # Initialize Prophet with weekly and monthly seasonality
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05  # Conservative change detection
        )
        
        # Add monthly seasonality for salary/rent cycles
        model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=5
        )
        
        # Fit model
        model.fit(df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        # Extract forecast for future dates only
        future_forecast = forecast.tail(days)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
        # Calculate summary stats
        forecasted_values = future_forecast['yhat'].values
        
        return {
            'method': 'prophet',
            'entity_id': df.get('entity_id', 'unknown'),
            'forecast_days': days,
            'daily_forecast': [
                {
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted': round(row['yhat'], 2),
                    'lower_bound': round(row['yhat_lower'], 2),
                    'upper_bound': round(row['yhat_upper'], 2)
                }
                for _, row in future_forecast.iterrows()
            ],
            'summary': {
                'total_predicted_inflow': round(sum(v for v in forecasted_values if v > 0), 2),
                'total_predicted_outflow': round(sum(v for v in forecasted_values if v < 0), 2),
                'net_cash_flow': round(sum(forecasted_values), 2),
                'min_balance_day': int(forecasted_values.argmin()) + 1,
                'min_balance_amount': round(forecasted_values.min(), 2)
            },
            'alerts': self._generate_alerts(forecasted_values)
        }
    
    def _simple_forecast(self, df: pd.DataFrame, days: int) -> Dict[str, Any]:
        """Fallback: Simple moving average forecast."""
        # Calculate moving averages
        ma_7 = df['y'].tail(7).mean()
        ma_30 = df['y'].tail(30).mean() if len(df) >= 30 else ma_7
        
        # Blend short and long term averages
        blend_weight = 0.7  # Favor recent data
        base_forecast = ma_7 * blend_weight + ma_30 * (1 - blend_weight)
        
        # Add some noise for realistic bounds
        std = df['y'].tail(30).std() if len(df) >= 30 else df['y'].std()
        
        daily_forecasts = []
        for i in range(days):
            forecast_date = date.today() + timedelta(days=i+1)
            daily_forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted': round(base_forecast, 2),
                'lower_bound': round(base_forecast - 1.5 * std, 2),
                'upper_bound': round(base_forecast + 1.5 * std, 2)
            })
        
        return {
            'method': 'moving_average',
            'forecast_days': days,
            'daily_forecast': daily_forecasts,
            'summary': {
                'total_predicted_inflow': round(base_forecast * days if base_forecast > 0 else 0, 2),
                'total_predicted_outflow': round(base_forecast * days if base_forecast < 0 else 0, 2),
                'net_cash_flow': round(base_forecast * days, 2),
                'min_balance_day': days,
                'min_balance_amount': round(base_forecast, 2)
            },
            'alerts': []
        }
    
    def _generate_alerts(self, forecasted_values) -> List[Dict[str, str]]:
        """Generate alerts based on forecast analysis."""
        alerts = []
        
        # Check for low cash periods
        cumulative = 0
        min_balance = float('inf')
        min_day = 0
        
        for i, val in enumerate(forecasted_values):
            cumulative += val
            if cumulative < min_balance:
                min_balance = cumulative
                min_day = i + 1
        
        if min_balance < 50000:  # ₹50k threshold
            alerts.append({
                'type': 'LOW_CASH',
                'severity': 'HIGH' if min_balance < 0 else 'MEDIUM',
                'message': f'Cash balance expected to drop to ₹{min_balance:,.0f} around day {min_day}',
                'recommendation': 'Accelerate collections or delay non-critical payments'
            })
        
        # Check for consistent negative flow
        negative_days = sum(1 for v in forecasted_values if v < 0)
        if negative_days > len(forecasted_values) * 0.6:
            alerts.append({
                'type': 'NEGATIVE_TREND',
                'severity': 'MEDIUM',
                'message': f'{negative_days} of {len(forecasted_values)} days show negative cash flow',
                'recommendation': 'Review recurring expenses and revenue pipeline'
            })
        
        return alerts


# Convenience function
def get_cash_forecast(entity_id: str, days: int = 30, db: Session = None) -> Dict[str, Any]:
    """Get cash flow forecast for an entity."""
    service = ForecastingService(db)
    return service.forecast(entity_id, days)
