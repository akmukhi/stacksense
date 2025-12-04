from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class IntegrationType(str, enum.Enum):
    GOOGLE_WORKSPACE = "google_workspace"
    MICROSOFT_365 = "microsoft_365"
    SLACK = "slack"
    GITHUB = "github"
    JIRA = "jira"
    NOTION = "notion"

class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(IntegrationType), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    credentials = Column(Text)  # Encrypted JSON string
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING, nullable=False)
    connected_at = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="integrations")

