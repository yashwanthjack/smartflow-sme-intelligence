# Account model - bank accounts and instruments
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    
    # Bank details
    bank_name = Column(String, nullable=False)
    account_number = Column(String)
    ifsc_code = Column(String)
    account_type = Column(String, default="current")  # current | savings | od | cc
    
    # Limits & balances
    current_balance = Column(Float, default=0)
    od_limit = Column(Float, default=0)  # Overdraft limit
    cc_limit = Column(Float, default=0)  # Cash credit limit
    
    # Status
    is_primary = Column(String, default=False)
    status = Column(String, default="active")  # active | inactive | closed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
