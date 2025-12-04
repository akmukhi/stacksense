from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.saas_tool import ToolStatus

class SaaSToolCreate(BaseModel):
    name: str
    category: Optional[str] = None
    vendor: Optional[str] = None
    organization_id: int

class SaaSToolResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    vendor: Optional[str]
    status: ToolStatus
    organization_id: int
    first_detected_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True

class SaaSToolUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    vendor: Optional[str] = None
    status: Optional[ToolStatus] = None

class SaaSToolListResponse(BaseModel):
    tools: List[SaaSToolResponse]
    total: int
    active_count: int
    unknown_count: int
    duplicate_count: int

