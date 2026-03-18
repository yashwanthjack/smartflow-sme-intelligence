import requests
import json

url = "http://127.0.0.1:8000/api/agents/query/04e12fbc-4784-4c46-83ed-4b35123863d2"
headers = {"Content-Type": "application/json"}
data = {"query": "Who should I pay first and do I have the cash?"}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Failed: {e}")
