import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.supervisor_agent import run_supervisor
from app.db.database import SessionLocal
from app.models.user import User

async def main():
    db = SessionLocal()
    # Get any valid entity ID
    user = db.query(User).filter(User.email == "yash@gmail.com").first()
    if not user:
        # Fallback to admin if that email is wrong
        user = db.query(User).first()
        
    entity_id = user.entity_id
    db.close()
    
    print(f"Test running for Entity ID: {entity_id}")
    result = await run_supervisor(entity_id, "Who paid the highest?")
    
    print("\n--- FINAL RESULT ---")
    print(result.get('output'))

if __name__ == "__main__":
    asyncio.run(main())
