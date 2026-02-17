import requests
import sys
import json

BASE_URL = "http://localhost:8000/api"

def test_backend_accuracy():
    print("🔍 Starting Backend Accuracy Verification...")
    
    # 1. Get Entities
    # Note: There isn't a standard /entities endpoint exposed in data.py to my knowledge, 
    # but we can try to guess or use a hardcoded one if we know it.
    # Frontend seems to use /api/profile/me or similar to get entities?
    # Let's try to hit /api/data/entities directly if it exists, or just use a placeholder 
    # and expect a 404 if it doesn't exist, but if we can't find an ID we can't test.
    # 
    # However, for the purpose of this verification, we can try to hit the endpoint 
    # with a likely ID. If the Project is fresh, maybe no entities exist.
    # But usually 'dev-entity-id' or similar might be used in seeds.
    
    # Let's try to list entities via the Organization router if it exists?
    # app.include_router(organization.router, prefix="/api/org" ...)
    
    entity_id = "default" # Placeholder
    
    try:
        # Try to list organizations/entities if endpoint exists
        resp = requests.get(f"{BASE_URL}/org/list") 
        if resp.status_code == 200:
             data = resp.json()
             if data:
                 entity_id = data[0]['id']
                 print(f"✅ Found Entity: {data[0].get('name')} (ID: {entity_id})")
        else:
             # Try another common endpoint pattern or just use a hardcoded UUID from a known seed
             # e.g. "e1" or "ent_12345"
             print(f"⚠️ Could not list entities. Using '{entity_id}' as fallback.")
    except:
        pass

    # 2. Test Dashboard KPIs (Credit Score & Financials)
    # Correct Path: /api/data/entities/{entity_id}/dashboard-kpis (No Auth Required based on code analysis)
    print(f"\n📊 Testing Dashboard KPIs for {entity_id}...")
    try:
        kpi_resp = requests.get(f"{BASE_URL}/data/entities/{entity_id}/dashboard-kpis")
        
        if kpi_resp.status_code == 200:
            data = kpi_resp.json()
            financials = data.get('financials', {})
            credit = data.get('credit', {})
            
            print(f"   • Cash Balance: ₹{financials.get('cash_balance', 0):,}")
            print(f"   • Monthly Burn: ₹{financials.get('monthly_burn_rate', 0):,}")
            print(f"   • Runway: {financials.get('runway_months', 0)} months")
            print(f"   • Credit Score: {credit.get('score')} (Band: {credit.get('risk_band')})")
            
            # Verification Logic
            # Note: If no data exists, score might be default 650
            if credit.get('score') == 750 and credit.get('risk_level') == "Low" and credit.get('risk_band') == "A":
                 # 750 was the old hardcoded value in data.py
                 print("   ⚠️ WARNING: Credit score looks like the old hardcoded default (750).")
            else:
                 print("   ✅ Credit score appears dynamic (from ScoringService).")
                 
            if financials.get('runway_months') == 999: # Default when no burn
                print("   ℹ️  Runway is infinite (no burn detected).")
            else:
                print("   ✅ Runway is calculated based on burn rate.")
        elif kpi_resp.status_code == 404:
            print(f"   ❌ Entity not found (404). Please ensure the database is seeded.")
        else:
            print(f"   ❌ Failed to fetch KPIs: {kpi_resp.status_code}")
            print(f"   Response: {kpi_resp.text[:100]}")
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")

if __name__ == "__main__":
    test_backend_accuracy()
