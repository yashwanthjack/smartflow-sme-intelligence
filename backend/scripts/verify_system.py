import sys
import os
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
EMAIL = "yashwanth@gmail.com"
PASSWORD = "Rryg@2005"

def run_verification():
    print("🔍 SmartFlow System Verification")
    print("================================")
    
    # 1. Authentication
    print("\n1. Testing Authentication...")
    try:
        login_res = requests.post(f"{BASE_URL}/auth/token", data={"username": EMAIL, "password": PASSWORD})
        if login_res.status_code == 200:
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {login_res.status_code}, {login_res.text}")
            return
            
        # Get Profile
        me_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if me_res.status_code == 200:
            user = me_res.json()
            entity_id = user["entity_id"]
            print(f"   ✅ User Profile loaded (Entity ID: {entity_id})")
        else:
            print(f"   ❌ Failed to get profile: {me_res.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    # 2. Dashboard Metrics
    print("\n2. Testing Dashboard Metrics...")
    endpoints = {
        "metrics": f"/data/entities/{entity_id}/financial-metrics",
        "pnl": f"/data/entities/{entity_id}/pnl",
        "spend": f"/data/entities/{entity_id}/spend-by-category",
        "forecast": f"/data/entities/{entity_id}/forecast?days=30",
        "ledger": f"/data/entities/{entity_id}/ledger?limit=10"
    }
    
    for name, path in endpoints.items():
        try:
            res = requests.get(f"{BASE_URL}{path}", headers=headers)
            if res.status_code == 200:
                data = res.json()
                
                # specific checks
                if name == "metrics" and "runway_months" in data:
                    print(f"   ✅ Metrics: OK (Runway: {data['runway_months']} mo)")
                elif name == "forecast" and "daily_forecast" in data:
                     print(f"   ✅ Forecast: OK ({len(data['daily_forecast'])} days projected)")
                elif name == "ledger" and "items" in data:
                     print(f"   ✅ Ledger: OK ({data['total']} entries found, returned {len(data['items'])})")
                else:
                    print(f"   ✅ {name.title()}: OK")
            else:
                print(f"   ❌ {name.title()}: Failed ({res.status_code})")
                print(res.text)
        except Exception as e:
            print(f"   ❌ {name.title()}: Error {e}")

    print("\n--------------------------------")
    print("🎉 Verification Complete!")

if __name__ == "__main__":
    run_verification()
