# Invoice model - AR/AP invoices
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from app.db.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    counterparty_id = Column(String, ForeignKey("counterparties.id"))
    
    # Invoice details
    invoice_number = Column(String, nullable=False)
    invoice_type = Column(String, nullable=False)  # receivable | payable
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    
    # Amounts
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0)
    balance_due = Column(Float)
    
    # Status
    status = Column(String, default="pending")  # pending | partial | paid | overdue | disputed
    days_overdue = Column(Float, default=0)
    
    # GST linkage
    gst_invoice_id = Column(String)  # Reference to e-invoice
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
