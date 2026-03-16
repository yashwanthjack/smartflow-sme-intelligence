import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.entity import Entity

def check():
    print("Starting check...", flush=True)
    db = SessionLocal()
    try:
        print("Querying user...", flush=True)
        user = db.query(User).first()
        if user:
            print(f"Found user: {user.email}", flush=True)
            print(f"User Entity ID: {user.entity_id}", flush=True)
            if user.entity_id:
                print("Querying entity...", flush=True)
                entity = db.query(Entity).filter(Entity.id == user.entity_id).first()
                if entity:
                     print(f"Found entity: {entity.name}", flush=True)
        else:
            print("No users found.", flush=True)
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Done.", flush=True)

if __name__ == "__main__":
    check()
