# Test script for SmartFlow Services
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def test_forecasting_service():
    """Test the ForecastingService."""
    print("\n" + "="*60)
    print("📈 Testing ForecastingService")
    print("="*60)
    
    from app.services.forecasting_service import ForecastingService
    
    service = ForecastingService(db=None)  # No DB, will use mock data
    result = service.forecast("test-entity", days=30)
    
    print(f"Method: {result['method']}")
    print(f"Days: {result['forecast_days']}")
    print(f"Summary: {result['summary']}")
    print(f"Alerts: {result.get('alerts', [])}")
    print(f"\nFirst 3 days:")
    for day in result['daily_forecast'][:3]:
        print(f"  {day}")
    
    return result

def test_scoring_service():
    """Test the ScoringService."""
    print("\n" + "="*60)
    print("📊 Testing ScoringService")
    print("="*60)
    
    from app.services.scoring_service import ScoringService
    
    service = ScoringService(db=None)  # No DB, will use mock data
    result = service.calculate_score("test-entity")
    
    print(f"Score: {result['score']}")
    print(f"Risk Band: {result['risk_band']} ({result['risk_label']})")
    print(f"Method: {result['method']}")
    print(f"\nFactors:")
    for factor in result.get('factors', [])[:5]:
        print(f"  {'✅' if factor.get('positive') else '⚠️'} {factor['factor']} ({factor['impact']})")
    print(f"\nLoan Eligibility: {result.get('loan_eligibility', {})}")
    
    return result

def test_tools():
    """Test the agent tools."""
    print("\n" + "="*60)
    print("🔧 Testing Agent Tools")
    print("="*60)
    
    from app.agents.tools import (
        get_overdue_invoices,
        get_cash_forecast,
        get_entity_credit_score
    )
    
    print("\n--- get_overdue_invoices ---")
    invoices = get_overdue_invoices.invoke({"entity_id": "test"})
    print(invoices[:500])
    
    print("\n--- get_cash_forecast ---")
    forecast = get_cash_forecast.invoke({"entity_id": "test", "days": 30})
    print(forecast[:500])
    
    print("\n--- get_entity_credit_score ---")
    score = get_entity_credit_score.invoke({"entity_id": "test"})
    print(score[:500])
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SmartFlow Services")
    parser.add_argument("--test", type=str, choices=["forecast", "score", "tools", "all"],
                        default="all", help="Which service to test")
    
    args = parser.parse_args()
    
    print("\n🚀 SmartFlow Service Test Suite")
    print("="*60)
    
    if args.test == "forecast" or args.test == "all":
        test_forecasting_service()
    
    if args.test == "score" or args.test == "all":
        test_scoring_service()
    
    if args.test == "tools" or args.test == "all":
        test_tools()
    
    print("\n✅ All tests complete!")
