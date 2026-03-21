import requests
import json
import time

url = "http://127.0.0.1:8000/api/agents/query/93307096-1e07-4110-b1b6-819413de90ab"
headers = {"Content-Type": "application/json"}
queries = [
    "whats the highest payment done?",
    "who gave me the highest income?"
]

for query in queries:
    print(f"\nTesting Query: '{query}'")
    data = {"query": query}
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            res_json = response.json()
            print(f"Agent Used: {res_json.get('agent_used')}")
            print(f"Intent Type: {res_json.get('intent')}")
            print(f"Output: {res_json.get('output')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")
