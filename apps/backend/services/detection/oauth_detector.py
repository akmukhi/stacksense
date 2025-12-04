from typing import List, Dict, Any
from database import SessionLocal
from models.saas_tool import SaaSTool, ToolStatus
from models.detection_source import DetectionSource, SourceType

class OAuthDetector:
    """Detect SaaS tools from OAuth integrations"""
    
    # OAuth app name patterns to tool mapping
    OAUTH_APP_TO_TOOL = {
        'slack': {'name': 'Slack', 'category': 'Communication', 'vendor': 'Slack Technologies'},
        'github': {'name': 'GitHub', 'category': 'Development', 'vendor': 'GitHub'},
        'notion': {'name': 'Notion', 'category': 'Productivity', 'vendor': 'Notion'},
        'jira': {'name': 'Jira', 'category': 'Project Management', 'vendor': 'Atlassian'},
        'zoom': {'name': 'Zoom', 'category': 'Communication', 'vendor': 'Zoom'},
        'figma': {'name': 'Figma', 'category': 'Design', 'vendor': 'Figma'},
        'linear': {'name': 'Linear', 'category': 'Project Management', 'vendor': 'Linear'},
        'asana': {'name': 'Asana', 'category': 'Project Management', 'vendor': 'Asana'},
        'trello': {'name': 'Trello', 'category': 'Project Management', 'vendor': 'Atlassian'},
        'dropbox': {'name': 'Dropbox', 'category': 'Storage', 'vendor': 'Dropbox'},
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def detect_from_oauth_apps(self, oauth_apps: List[Dict[str, Any]], organization_id: int) -> List[Dict[str, Any]]:
        """Detect tools from OAuth applications"""
        detected_tools = []
        
        for app in oauth_apps:
            app_name = app.get('name', '').lower()
            app_display_name = app.get('displayName', '').lower()
            
            # Try to match app name
            tool_info = None
            for key, value in self.OAUTH_APP_TO_TOOL.items():
                if key in app_name or key in app_display_name:
                    tool_info = value
                    break
            
            if tool_info:
                # Check if tool already exists
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == tool_info['name'],
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    tool = SaaSTool(
                        name=tool_info['name'],
                        category=tool_info['category'],
                        vendor=tool_info['vendor'],
                        status=ToolStatus.ACTIVE,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.OAUTH,
                        source_data={'app': app}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'oauth',
                        'app_name': app.get('name')
                    })
                else:
                    from datetime import datetime
                    existing_tool.last_seen_at = datetime.utcnow()
                    
                    # Check if detection source exists
                    existing_source = self.db.query(DetectionSource).filter(
                        DetectionSource.tool_id == existing_tool.id,
                        DetectionSource.source_type == SourceType.OAUTH
                    ).first()
                    
                    if not existing_source:
                        detection_source = DetectionSource(
                            tool_id=existing_tool.id,
                            source_type=SourceType.OAUTH,
                            source_data={'app': app}
                        )
                        self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': existing_tool.id,
                        'name': existing_tool.name,
                        'source': 'oauth',
                        'app_name': app.get('name')
                    })
            else:
                # Unknown OAuth app
                app_name_display = app.get('displayName') or app.get('name', 'Unknown App')
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == app_name_display,
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    tool = SaaSTool(
                        name=app_name_display,
                        category=None,
                        vendor=None,
                        status=ToolStatus.UNKNOWN,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.OAUTH,
                        source_data={'app': app}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'oauth',
                        'status': 'unknown'
                    })
        
        self.db.commit()
        return detected_tools

