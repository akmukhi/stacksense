from typing import List, Dict, Any
from database import SessionLocal
from models.saas_tool import SaaSTool, ToolStatus
from models.detection_source import DetectionSource, SourceType

class SSODetector:
    """Detect SaaS tools from SSO logs"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def detect_from_sso_logs(self, sso_logs: List[Dict[str, Any]], organization_id: int) -> List[Dict[str, Any]]:
        """Detect tools from SSO authentication logs"""
        detected_tools = []
        
        # Extract unique application/service names from SSO logs
        apps_seen = set()
        
        for log in sso_logs:
            app_name = log.get('appDisplayName') or log.get('applicationName') or log.get('service')
            if app_name and app_name not in apps_seen:
                apps_seen.add(app_name)
                
                # Check if tool already exists
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == app_name,
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    tool = SaaSTool(
                        name=app_name,
                        category=None,
                        vendor=None,
                        status=ToolStatus.ACTIVE,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.SSO,
                        source_data={'log': log}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'sso',
                        'app_name': app_name
                    })
                else:
                    from datetime import datetime
                    existing_tool.last_seen_at = datetime.utcnow()
                    
                    # Check if detection source exists
                    existing_source = self.db.query(DetectionSource).filter(
                        DetectionSource.tool_id == existing_tool.id,
                        DetectionSource.source_type == SourceType.SSO
                    ).first()
                    
                    if not existing_source:
                        detection_source = DetectionSource(
                            tool_id=existing_tool.id,
                            source_type=SourceType.SSO,
                            source_data={'log': log}
                        )
                        self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': existing_tool.id,
                        'name': existing_tool.name,
                        'source': 'sso',
                        'app_name': app_name
                    })
        
        self.db.commit()
        return detected_tools

