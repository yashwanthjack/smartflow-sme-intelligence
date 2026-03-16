from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.auth import get_password_hash
import uuid

def fix_admin():
    db = SessionLocal()
    try:
        email = "admin@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("User not found, creating...")
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                role="admin",
                is_active=True
            )
            db.add(user)
        else:
            print(f"User found: {user.email}, Role: {user.role}")
            user.role = "admin" # Ensure admin
            user.hashed_password = get_password_hash("admin") # Reset password just in case

        # Check/Create Entity
        if not user.entity_id:
            print("No entity linked. Creating...")
            entity = Entity(
                id=str(uuid.uuid4()),
                name="SmartFlow Demo Corp",
                gstin="29ABCDE1234F1Z5",
                industry="Tech",
                city="Bangalore",
                state="KA"
            )
            db.add(entity)
            db.flush() # get ID
            user.entity_id = entity.id
            print(f"Linked entity: {entity.name}")
        else:
            entity = db.query(Entity).filter(Entity.id == user.entity_id).first()
            if entity:
                print(f"Already linked to: {entity.name}")
            else:
                print("Linked entity ID not found, creating new...")
                # ... same creation logic
                
        db.commit()
        print("Admin user fixed.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin()
