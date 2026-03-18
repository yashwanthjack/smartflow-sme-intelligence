import requests
import json

url = "http://127.0.0.1:8000/api/audit/04e12fbc-4784-4c46-83ed-4b35123863d2?limit=5"
try:
    response = requests.get(url)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Failed: {e}")
