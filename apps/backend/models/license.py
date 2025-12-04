from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("saas_tools.id"), nullable=False)
    total_seats = Column(Integer, default=0)
    used_seats = Column(Integer, default=0)
    cost_per_seat = Column(Numeric(10, 2))
    renewal_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tool = relationship("SaaSTool", back_populates="licenses")

