from pydantic import BaseModel
from typing import List, Dict, Any

class DashboardStats(BaseModel):
    total_tools: int
    active_tools: int
    unknown_tools: int
    suspected_duplicates: int
    total_integrations: int
    connected_integrations: int
    last_scan_at: str  # ISO format datetime string

class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_tools: List[Dict[str, Any]]
    integration_status: List[Dict[str, Any]]

