"""
Unit tests for SmartFlow backend services.
Tests ForecastingService and ScoringService with mock data.
"""
import pytest
from app.services.forecasting_service import ForecastingService


class TestForecastingService:
    """Test the cash flow forecasting service."""

    def test_forecast_returns_required_keys(self):
        """Forecast response must contain method, forecast_days, daily_forecast, summary."""
        service = ForecastingService(db=None)  # Uses mock data
        result = service.forecast("test-entity", days=30)

        assert "method" in result
        assert "forecast_days" in result
        assert "daily_forecast" in result
        assert "summary" in result
        assert result["forecast_days"] == 30

    def test_forecast_daily_entries_have_correct_shape(self):
        """Each daily forecast entry must have date, predicted, lower/upper bounds."""
        service = ForecastingService(db=None)
        result = service.forecast("test-entity", days=15)

        for entry in result["daily_forecast"]:
            assert "date" in entry
            assert "predicted" in entry
            assert "lower_bound" in entry
            assert "upper_bound" in entry
            # Upper bound must exceed lower bound
            assert entry["upper_bound"] >= entry["lower_bound"]

    def test_forecast_summary_has_financials(self):
        """Summary must contain inflow, outflow, and net cash flow."""
        service = ForecastingService(db=None)
        result = service.forecast("test-entity", days=30)
        summary = result["summary"]

        assert "total_predicted_inflow" in summary
        assert "total_predicted_outflow" in summary
        assert "net_cash_flow" in summary
        # Net = inflow + outflow (outflow is negative)
        expected_net = summary["total_predicted_inflow"] + summary["total_predicted_outflow"]
        assert abs(summary["net_cash_flow"] - expected_net) < 1.0  # Float tolerance

    def test_forecast_with_different_horizons(self):
        """Forecast should work for various time horizons."""
        service = ForecastingService(db=None)

        for days in [7, 30, 60, 90]:
            result = service.forecast("test-entity", days=days)
            assert result["forecast_days"] == days
            # Should have at least 'days' entries (history + future)
            assert len(result["daily_forecast"]) >= days

    def test_mock_data_generation(self):
        """Mock data generator should produce 90 days of data."""
        service = ForecastingService(db=None)
        df = service._get_mock_data()

        assert len(df) == 90
        assert "ds" in df.columns
        assert "y" in df.columns
        assert df["y"].notna().all()


class TestForecastAlerts:
    """Test the alert generation logic."""

    def test_no_alerts_for_healthy_flow(self):
        """Large positive values should generate no alerts."""
        import numpy as np

        service = ForecastingService(db=None)
        # All positive, large values → no LOW_CASH or NEGATIVE_TREND
        healthy_values = np.array([100000] * 30)
        alerts = service._generate_alerts(healthy_values)

        low_cash = [a for a in alerts if a["type"] == "LOW_CASH"]
        assert len(low_cash) == 0

    def test_alert_on_negative_trend(self):
        """Mostly negative values should trigger NEGATIVE_TREND alert."""
        import numpy as np

        service = ForecastingService(db=None)
        # 80% negative days
        negative_values = np.array([-5000] * 24 + [5000] * 6)
        alerts = service._generate_alerts(negative_values)

        negative_alerts = [a for a in alerts if a["type"] == "NEGATIVE_TREND"]
        assert len(negative_alerts) == 1
        assert negative_alerts[0]["severity"] == "MEDIUM"
