# Entity model - SME or branch
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from app.db.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    entity_type = Column(String, default="sme")  # sme | branch | subsidiary
    gstin = Column(String)  # GST Identification Number
    pan = Column(String)  # PAN Number
    industry = Column(String)
    city = Column(String)
    state = Column(String)
    
    # Lender Platform / Public Profile
    is_public_profile = Column(Boolean, default=False)
    public_profile_slug = Column(String, unique=True, index=True, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
