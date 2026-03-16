
import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.entity import Entity

def fix_permissions():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users.")
        
        for user in users:
            print(f"Processing user: {user.email}")
            
            # 1. Promote to Admin
            if user.role != UserRole.ADMIN:
                user.role = UserRole.ADMIN
                print(f"  - Promoted to ADMIN")
            
            # 2. Ensure Organization exists
            if not user.entity_id:
                org_name = f"{user.full_name}'s Organization" if user.full_name else "My Organization"
                print(f"  - Creating organization: {org_name}")
                
                new_entity = Entity(
                    name=org_name,
                    entity_type="sme",
                    industry="technology", # Default
                    city="Bangalore",
                    state="Karnataka"
                )
                db.add(new_entity)
                db.flush() # Generate ID
                
                user.entity_id = new_entity.id
                print(f"  - Linked to new entity ID: {new_entity.id}")
            else:
                # Check if entity exists
                entity = db.query(Entity).filter(Entity.id == user.entity_id).first()
                if not entity:
                    print(f"  - User has entity_id {user.entity_id} but entity not found. Creating new one.")
                    org_name = f"{user.full_name}'s Organization"
                    new_entity = Entity(name=org_name, entity_type="sme")
                    db.add(new_entity)
                    db.flush()
                    user.entity_id = new_entity.id
                else:
                    print(f"  - Already linked to: {entity.name}")
                    
        db.commit()
        print("Permissions fixed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_permissions()
