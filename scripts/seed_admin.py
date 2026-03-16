import requests

API_BASE = "http://127.0.0.1:8000/api"

def seed():
    # 1. Register Admin
    email = "admin@gmail.com"
    password = "admin"
    name = "Admin User"
    
    print(f"Registering {email}...")
    res = requests.post(f"{API_BASE}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": name,
        "role": "admin"
    })
    
    if res.status_code == 201:
        print("User created.")
    elif res.status_code == 400 and "already registered" in res.text:
        print("User already exists.")
    else:
        print(f"Failed to create user: {res.text}")
        return

    # 2. Login to get token
    print("Logging in...")
    res = requests.post(f"{API_BASE}/auth/token", data={
        "username": email,
        "password": password
    })
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create Organization/Entity
    print("Creating Organization...")
    res = requests.put(f"{API_BASE}/org/", json={
        "name": "SmartFlow Demo Corp",
        "gstin": "29ABCDE1234F1Z5",
        "industry": "Technology",
        "city": "Bangalore",
        "state": "Karnataka"
    }, headers=headers)
    
    if res.status_code == 200:
        print("Organization created/updated.")
    else:
        print(f"Failed to create org: {res.text}")

if __name__ == "__main__":
    seed()
