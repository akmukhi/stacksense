from typing import List, Dict, Any
from database import SessionLocal
from models.saas_tool import SaaSTool, ToolStatus
from models.detection_source import DetectionSource, SourceType
from models.organization import Organization

class EmailDomainDetector:
    """Detect SaaS tools from email domains"""
    
    # Common SaaS tool domains mapping
    DOMAIN_TO_TOOL = {
        'slack.com': {'name': 'Slack', 'category': 'Communication', 'vendor': 'Slack Technologies'},
        'github.com': {'name': 'GitHub', 'category': 'Development', 'vendor': 'GitHub'},
        'notion.so': {'name': 'Notion', 'category': 'Productivity', 'vendor': 'Notion'},
        'atlassian.net': {'name': 'Jira', 'category': 'Project Management', 'vendor': 'Atlassian'},
        'zoom.us': {'name': 'Zoom', 'category': 'Communication', 'vendor': 'Zoom'},
        'figma.com': {'name': 'Figma', 'category': 'Design', 'vendor': 'Figma'},
        'linear.app': {'name': 'Linear', 'category': 'Project Management', 'vendor': 'Linear'},
        'asana.com': {'name': 'Asana', 'category': 'Project Management', 'vendor': 'Asana'},
        'trello.com': {'name': 'Trello', 'category': 'Project Management', 'vendor': 'Atlassian'},
        'dropbox.com': {'name': 'Dropbox', 'category': 'Storage', 'vendor': 'Dropbox'},
        'google.com': {'name': 'Google Workspace', 'category': 'Productivity', 'vendor': 'Google'},
        'microsoft.com': {'name': 'Microsoft 365', 'category': 'Productivity', 'vendor': 'Microsoft'},
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def detect_from_domains(self, domains: List[str], organization_id: int) -> List[Dict[str, Any]]:
        """Detect tools from email domains"""
        detected_tools = []
        
        for domain in domains:
            # Extract root domain
            root_domain = self._extract_root_domain(domain)
            
            # Check if domain matches known SaaS tools
            tool_info = self.DOMAIN_TO_TOOL.get(root_domain)
            
            if tool_info:
                # Check if tool already exists
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == tool_info['name'],
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    # Create new tool
                    tool = SaaSTool(
                        name=tool_info['name'],
                        category=tool_info['category'],
                        vendor=tool_info['vendor'],
                        status=ToolStatus.ACTIVE,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    # Create detection source
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.EMAIL,
                        source_data={'domain': domain, 'root_domain': root_domain}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'email_domain',
                        'domain': domain
                    })
                else:
                    # Update last_seen_at
                    from datetime import datetime
                    existing_tool.last_seen_at = datetime.utcnow()
                    
                    # Check if detection source exists
                    existing_source = self.db.query(DetectionSource).filter(
                        DetectionSource.tool_id == existing_tool.id,
                        DetectionSource.source_type == SourceType.EMAIL,
                        DetectionSource.source_data['domain'].astext == domain
                    ).first()
                    
                    if not existing_source:
                        detection_source = DetectionSource(
                            tool_id=existing_tool.id,
                            source_type=SourceType.EMAIL,
                            source_data={'domain': domain, 'root_domain': root_domain}
                        )
                        self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': existing_tool.id,
                        'name': existing_tool.name,
                        'source': 'email_domain',
                        'domain': domain
                    })
            else:
                # Unknown domain - create as unknown tool
                tool_name = self._domain_to_tool_name(root_domain)
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == tool_name,
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    tool = SaaSTool(
                        name=tool_name,
                        category=None,
                        vendor=None,
                        status=ToolStatus.UNKNOWN,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.EMAIL,
                        source_data={'domain': domain, 'root_domain': root_domain}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'email_domain',
                        'domain': domain,
                        'status': 'unknown'
                    })
        
        self.db.commit()
        return detected_tools
    
    def _extract_root_domain(self, domain: str) -> str:
        """Extract root domain from full domain"""
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain
    
    def _domain_to_tool_name(self, domain: str) -> str:
        """Convert domain to tool name"""
        # Capitalize and format domain name
        parts = domain.split('.')
        name = parts[0].capitalize()
        return name

