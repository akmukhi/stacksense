from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class InvoiceSource(str, enum.Enum):
    EMAIL = "email"
    UPLOAD = "upload"
    API = "api"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("saas_tools.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD")
    invoice_date = Column(DateTime(timezone=True))
    renewal_date = Column(DateTime(timezone=True))
    source = Column(SQLEnum(InvoiceSource), nullable=False)
    file_path = Column(String)  # Path to uploaded file if applicable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tool = relationship("SaaSTool", back_populates="invoices")

