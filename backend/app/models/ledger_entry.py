# LedgerEntry model - unified time-indexed ledger
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from app.db.database import Base


class LedgerEntry(Base):
    """
    The unified ledger is the core abstraction in SmartFlow.
    All financial events (bank transactions, invoices, GST) normalize to this table.
    """
    __tablename__ = "ledger_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    
    # Time
    ledger_date = Column(Date, nullable=False)  # Posting date
    
    # Amount (positive = inflow, negative = outflow)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    
    # Dimensions
    counterparty_id = Column(String, ForeignKey("counterparties.id"))
    account_id = Column(String, ForeignKey("accounts.id"))
    invoice_id = Column(String, ForeignKey("invoices.id"))
    
    # Classification
    category = Column(String)  # revenue | expense | gst | salary | loan | other
    subcategory = Column(String)
    
    # Source tracking
    source_type = Column(String)  # bank | tally | gst | manual
    source_record_id = Column(String)  # Original record ID from source
    
    # Description
    description = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
