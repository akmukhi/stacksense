from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

