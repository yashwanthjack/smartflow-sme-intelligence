# CreditFeature model - computed credit features
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from app.db.database import Base
class CreditFeature(Base):
    __tablename__ = "credit_features"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id=Column(String,ForeignKey("cases.id"),nullable=False)
    score=Column(Float)
    pd_band=Column(String)
    avg_monthly_inflow=Column(Float)
    volatility_index=Column(Float)
    concentration_risk=Column(Float)
    
    gst_gaps=Column(Float)
    flags=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)
    
