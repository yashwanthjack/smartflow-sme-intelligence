# Counterparty model - customers and vendors
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.database import Base


class Counterparty(Base):
    __tablename__ = "counterparties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    name = Column(String, nullable=False)
    counterparty_type = Column(String, nullable=False)  # customer | vendor | lender
    gstin = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    
    # Risk & behavior metrics (computed)
    avg_payment_delay = Column(Float, default=0)  # days
    risk_score = Column(Float)
    credit_limit = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
