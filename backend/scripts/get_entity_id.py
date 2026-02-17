import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.user import User

def get_admin_entity_id():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@gmail.com").first()
        if user:
            print(f"User Found: {user.email}")
            print(f"User ID: {user.id}")
            print(f"Entity ID: {user.entity_id}")
        else:
            print("User 'admin@gmail.com' not found.")
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_admin_entity_id()
