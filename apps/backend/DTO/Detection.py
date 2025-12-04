from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from models.detection_source import SourceType

class DetectionScanRequest(BaseModel):
    organization_id: int
    integration_types: Optional[list] = None  # If None, scan all integrations

class DetectionSourceResponse(BaseModel):
    id: int
    tool_id: int
    source_type: SourceType
    source_data: Optional[Dict[str, Any]]
    detected_at: datetime

    class Config:
        from_attributes = True

class DetectionResult(BaseModel):
    tools_detected: int
    new_tools: int
    duplicates_found: int
    scan_completed_at: datetime

