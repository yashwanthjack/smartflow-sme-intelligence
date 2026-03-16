import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/data"

def test_dashboard_apis():
    print("🚀 Testing Dashboard APIs...")
    
    # 1. Get Entities
    try:
        resp = requests.get(f"{BASE_URL}/entities")
        if resp.status_code != 200:
            print(f"❌ Failed to get entities: {resp.text}")
            return
            
        entities = resp.json()
        if not entities:
            print("⚠️ No entities found!")
            return
            
        entity_id = entities[0]['id']
        print(f"✅ Found Entity: {entities[0]['name']} (ID: {entity_id})")
        
        # 2. Get Financial Metrics (Runway, Burn)
        print(f"\n📊 Testing Financial Metrics for {entity_id}...")
        resp = requests.get(f"{BASE_URL}/entities/{entity_id}/financial-metrics")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Cash Balance: {data['cash_balance']}")
            print(f"   ✅ Monthly Burn: {data['monthly_burn_rate']}")
            print(f"   ✅ Runway: {data['runway_months']} months")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
            
        # 3. Get P&L
        print(f"\n📈 Testing Monthly P&L...")
        resp = requests.get(f"{BASE_URL}/entities/{entity_id}/pnl")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Retrieved {len(data)} months of data")
            if data:
                print(f"   📅 Last Month: {data[-1]}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
            
        # 4. Get Spend by Category
        print(f"\n💸 Testing Spend by Category...")
        resp = requests.get(f"{BASE_URL}/entities/{entity_id}/spend-by-category")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Top Category: {data[0]['category']} ({data[0]['amount']})")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard_apis()
