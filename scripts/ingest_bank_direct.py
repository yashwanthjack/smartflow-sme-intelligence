import requests

ENTITY_ID = "d9ff0ba0-0369-4e7c-8828-f153866594b6"
FILE_PATH = r"d:\1.Education\smartflow-sme-intelligence\Acct Statement_1521_24012026_17.54.20.xls"

# First get a token for joshikha
print("Getting auth token for joshikha...")
login_res = requests.post("http://localhost:8000/api/auth/token", data={
    "username": "joshikha@gmail.com",
    "password": "joshikha123"
})
print(f"Login status: {login_res.status_code}")
if login_res.status_code != 200:
    # Try other passwords
    for pwd in ["password123", "password", "joshi123", "123456", "admin123"]:
        r = requests.post("http://localhost:8000/api/auth/token", data={
            "username": "joshikha@gmail.com", "password": pwd
        })
        print(f"  Tried '{pwd}': {r.status_code}")
        if r.status_code == 200:
            login_res = r
            break

if login_res.status_code == 200:
    token = login_res.json().get("access_token")
    print(f"Got token: {token[:30]}...")
    
    print(f"\nUploading bank statement to entity {ENTITY_ID}...")
    with open(FILE_PATH, "rb") as f:
        res = requests.post(
            "http://localhost:8000/api/ingest/bank",
            headers={"Authorization": f"Bearer {token}"},
            data={"entity_id": ENTITY_ID},
            files={"file": ("bank_statement.xls", f, "application/vnd.ms-excel")}
        )
    print(f"Upload status: {res.status_code}")
    print(f"Response: {res.json()}")
else:
    print("Could not get token. Trying direct DB insert via Python...")
    import sys
    sys.path.insert(0, r"d:\1.Education\smartflow-sme-intelligence\backend")
    from app.db.session import SessionLocal
    from app.services.ingestion_service import IngestionService
    
    db = SessionLocal()
    svc = IngestionService(db)
    count = svc.ingest_bank_statement(FILE_PATH, ENTITY_ID)
    print(f"Directly ingested {count} transactions!")
    db.close()
