from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class ToolStatus(str, enum.Enum):
    ACTIVE = "active"
    UNKNOWN = "unknown"
    SUSPECTED_DUPLICATE = "suspected_duplicate"

class SaaSTool(Base):
    __tablename__ = "saas_tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String)
    vendor = Column(String)
    status = Column(SQLEnum(ToolStatus), default=ToolStatus.UNKNOWN, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    first_detected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="tools")
    detection_sources = relationship("DetectionSource", back_populates="tool", cascade="all, delete-orphan")
    user_activities = relationship("UserActivity", back_populates="tool", cascade="all, delete-orphan")
    licenses = relationship("License", back_populates="tool", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="tool", cascade="all, delete-orphan")

