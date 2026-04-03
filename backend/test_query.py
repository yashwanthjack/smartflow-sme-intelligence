import requests

def get_token():
    url = "http://localhost:8000/api/auth/token"
    data = {
        "username": "9047889889@gmail.com",
        "password": "9047889889"
    }
    response = requests.post(url, data=data)
    return response.json()["access_token"]

try:
    token = get_token()
    
    from app.db.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    user = db.query(User).filter(User.email=="9047889889@gmail.com").first()
    entity_id = user.entity_id
    db.close()
    
    url = f"http://localhost:8000/api/agents/query/{entity_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"query": "hello"}
    r = requests.post(url, json=payload, headers=headers)
    print(r.status_code)
    print(r.json())
except Exception as e:
    print(e)
