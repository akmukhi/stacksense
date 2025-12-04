from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from DTO.Dashboard import DashboardResponse, DashboardStats
from models.saas_tool import SaaSTool, ToolStatus
from models.integration import Integration, IntegrationStatus
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

dashboard_controller_router = InferringRouter()

@cbv(dashboard_controller_router)
class DashboardController:
    def __init__(self):
        pass
    
    @dashboard_controller_router.get("/stats", response_model=DashboardResponse)
    def get_dashboard_stats(self, organization_id: int = Query(None), db: Session = Depends(get_db)):
        try:
            # Get tool stats
            tool_query = db.query(SaaSTool)
            if organization_id:
                tool_query = tool_query.filter(SaaSTool.organization_id == organization_id)
            
            tools = tool_query.all()
            total_tools = len(tools)
            active_tools = len([t for t in tools if t.status == ToolStatus.ACTIVE])
            unknown_tools = len([t for t in tools if t.status == ToolStatus.UNKNOWN])
            suspected_duplicates = len([t for t in tools if t.status == ToolStatus.SUSPECTED_DUPLICATE])
            
            # Get integration stats
            integration_query = db.query(Integration)
            if organization_id:
                integration_query = integration_query.filter(Integration.organization_id == organization_id)
            
            integrations = integration_query.all()
            total_integrations = len(integrations)
            connected_integrations = len([i for i in integrations if i.status == IntegrationStatus.CONNECTED])
            
            # Get last scan time (most recent last_seen_at from tools)
            last_scan = None
            if tools:
                last_seen_times = [t.last_seen_at for t in tools if t.last_seen_at]
                if last_seen_times:
                    last_scan = max(last_seen_times).isoformat()
            
            stats = DashboardStats(
                total_tools=total_tools,
                active_tools=active_tools,
                unknown_tools=unknown_tools,
                suspected_duplicates=suspected_duplicates,
                total_integrations=total_integrations,
                connected_integrations=connected_integrations,
                last_scan_at=last_scan or ""
            )
            
            # Get recent tools (last 10)
            recent_tools = []
            if tools:
                sorted_tools = sorted(tools, key=lambda t: t.last_seen_at or t.first_detected_at, reverse=True)
                recent_tools = [
                    {
                        'id': t.id,
                        'name': t.name,
                        'status': t.status.value,
                        'last_seen_at': t.last_seen_at.isoformat() if t.last_seen_at else None
                    }
                    for t in sorted_tools[:10]
                ]
            
            # Get integration status
            integration_status = [
                {
                    'id': i.id,
                    'type': i.type.value,
                    'status': i.status.value,
                    'connected_at': i.connected_at.isoformat() if i.connected_at else None,
                    'last_sync_at': i.last_sync_at.isoformat() if i.last_sync_at else None
                }
                for i in integrations
            ]
            
            return DashboardResponse(
                stats=stats,
                recent_tools=recent_tools,
                integration_status=integration_status
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

