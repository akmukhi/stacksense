from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("saas_tools.id"), nullable=False)
    user_email = Column(String, nullable=False, index=True)
    activity_type = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON)

    # Relationships
    tool = relationship("SaaSTool", back_populates="user_activities")

