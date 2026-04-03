# Persistent Memory Model for SmartFlow Agents
# Allows agents to remember user preferences, business rules, and past insights

from sqlalchemy import Column, String, Integer, Text, DateTime, func
from app.db.database import Base
import uuid


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, nullable=False, index=True)
    
    # Category: preference | rule | insight | fact
    category = Column(String, nullable=False, default="insight")
    
    # The actual memory content
    content = Column(Text, nullable=False)
    
    # Which agent created this memory
    source_agent = Column(String, nullable=True, default="user")
    
    # Importance 1-5 for retrieval ranking
    importance = Column(Integer, nullable=False, default=3)
    
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)  # Optional TTL
