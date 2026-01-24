# GSTSummary model - GST filing records
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    DateTime,
    Boolean,
    ForeignKey
)
from app.db.database import Base


class GSTSummary(Base):
    __tablename__ = "gst_summaries"

    # ---- Core Identifiers ----
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)

    # ---- Filing Metadata ----
    return_type = Column(String, nullable=False)  
    # GSTR-1 | GSTR-3B | GSTR-2B | CMP-08

    period = Column(String, nullable=False)  
    # e.g. "2024-01", "2024-Q1"

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    filing_status = Column(String, default="filed")  
    # filed | pending | delayed

    filed_on = Column(Date)
    days_delayed = Column(Float, default=0)

    is_revised = Column(Boolean, default=False)

    # ---- Financial Summary ----
    turnover = Column(Float)
    output_tax = Column(Float)
    tax_paid = Column(Float)
    input_credit = Column(Float)

    # ---- Tax Breakup ----
    cgst = Column(Float)
    sgst = Column(Float)
    igst = Column(Float)
    cess = Column(Float)

    payment_mode = Column(String)  
    # cash | itc | mixed

    # ---- Risk & Intelligence (derived later) ----
    mismatch_score = Column(Float)  
    compliance_risk = Column(String)  
    # LOW | MEDIUM | HIGH

    # ---- Audit ----
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)