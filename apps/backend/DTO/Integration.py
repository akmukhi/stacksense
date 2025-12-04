from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.integration import IntegrationType, IntegrationStatus

class IntegrationCreate(BaseModel):
    type: IntegrationType
    organization_id: int
    credentials: Optional[str] = None

class IntegrationResponse(BaseModel):
    id: int
    type: IntegrationType
    organization_id: int
    status: IntegrationStatus
    connected_at: Optional[datetime]
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IntegrationConnect(BaseModel):
    organization_id: int
    auth_code: Optional[str] = None  # For OAuth flows

