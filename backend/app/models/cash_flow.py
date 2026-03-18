# CashFlow model - daily cash flow records
import uuid
from datetime import datetime,date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey
from app.db.database import Base
class CashFlow(Base):
    __tablename__ = "cashflows"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id=Column(String,ForeignKey("cases.id"))
    transaction_date=Column(Date,nullable=False)
    description = Column(String)
    inflow = Column(Float, default=0.0)
    outflow = Column(Float, default=0.0)
    category = Column(String)
    counterparty = Column(String)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String)
    status = Column(String, default="completed")