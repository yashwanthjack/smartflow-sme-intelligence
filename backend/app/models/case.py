# Case model - represents an SME credit case
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.db.database import Base

class Case(Base):
    __tablename__ = "cases"
    id = Column(String,primary_key=True, default=lambda: str(uuid.uuid4()))
    sme_name=Column(String,nullable=False)
    status=Column(String,default="ingested")
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
