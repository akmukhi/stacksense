from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class SourceType(str, enum.Enum):
    EMAIL = "email"
    OAUTH = "oauth"
    SSO = "sso"
    INVOICE = "invoice"

class DetectionSource(Base):
    __tablename__ = "detection_sources"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("saas_tools.id"), nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    source_data = Column(JSON)  # Flexible JSON data
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tool = relationship("SaaSTool", back_populates="detection_sources")

