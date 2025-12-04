from typing import List, Dict, Any, Optional
from database import SessionLocal, get_db
from models.organization import Organization
from models.integration import Integration, IntegrationType, IntegrationStatus
from .email_domain_detector import EmailDomainDetector
from .oauth_detector import OAuthDetector
from .sso_detector import SSODetector
from .invoice_detector import InvoiceDetector
from .duplicate_detector import DuplicateDetector
from services.integrations import (
    GoogleWorkspaceIntegration,
    Microsoft365Integration,
    SlackIntegration,
    GitHubIntegration,
    JiraIntegration,
    NotionIntegration
)

class DetectionService:
    """Main detection orchestrator"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.email_detector = EmailDomainDetector(db_session)
        self.oauth_detector = OAuthDetector(db_session)
        self.sso_detector = SSODetector(db_session)
        self.invoice_detector = InvoiceDetector(db_session)
        self.duplicate_detector = DuplicateDetector(db_session)
    
    async def scan_organization(self, organization_id: int, 
                                 integration_types: Optional[List[IntegrationType]] = None) -> Dict[str, Any]:
        """Perform a full detection scan for an organization"""
        results = {
            'tools_detected': 0,
            'new_tools': 0,
            'duplicates_found': 0,
            'sources_scanned': []
        }
        
        # Get all connected integrations
        query = self.db.query(Integration).filter(
            Integration.organization_id == organization_id,
            Integration.status == IntegrationStatus.CONNECTED
        )
        
        if integration_types:
            query = query.filter(Integration.type.in_(integration_types))
        
        integrations = query.all()
        
        for integration in integrations:
            try:
                # Get integration connector
                connector = self._get_integration_connector(integration)
                if not connector:
                    continue
                
                # Test connection
                if not await connector.test_connection():
                    continue
                
                # Scan email domains
                try:
                    domains = await connector.get_email_domains()
                    if domains:
                        detected = await self.email_detector.detect_from_domains(domains, organization_id)
                        results['tools_detected'] += len(detected)
                        results['new_tools'] += len([d for d in detected if 'status' not in d or d.get('status') != 'unknown'])
                        results['sources_scanned'].append(f'email_domains_{integration.type.value}')
                except Exception as e:
                    print(f"Error scanning email domains: {e}")
                
                # Scan OAuth apps
                try:
                    oauth_apps = await connector.get_oauth_apps()
                    if oauth_apps:
                        detected = await self.oauth_detector.detect_from_oauth_apps(oauth_apps, organization_id)
                        results['tools_detected'] += len(detected)
                        results['new_tools'] += len([d for d in detected if 'status' not in d or d.get('status') != 'unknown'])
                        results['sources_scanned'].append(f'oauth_apps_{integration.type.value}')
                except Exception as e:
                    print(f"Error scanning OAuth apps: {e}")
                
                # Scan SSO logs
                try:
                    sso_logs = await connector.get_sso_logs(limit=100)
                    if sso_logs:
                        detected = await self.sso_detector.detect_from_sso_logs(sso_logs, organization_id)
                        results['tools_detected'] += len(detected)
                        results['new_tools'] += len([d for d in detected if 'status' not in d or d.get('status') != 'unknown'])
                        results['sources_scanned'].append(f'sso_logs_{integration.type.value}')
                except Exception as e:
                    print(f"Error scanning SSO logs: {e}")
                
            except Exception as e:
                print(f"Error scanning integration {integration.type.value}: {e}")
                continue
        
        # Detect duplicates
        try:
            duplicates = self.duplicate_detector.detect_duplicates(organization_id)
            results['duplicates_found'] = len(duplicates)
        except Exception as e:
            print(f"Error detecting duplicates: {e}")
        
        from datetime import datetime
        results['scan_completed_at'] = datetime.utcnow()
        
        return results
    
    def _get_integration_connector(self, integration: Integration):
        """Get appropriate integration connector instance"""
        connector_map = {
            IntegrationType.GOOGLE_WORKSPACE: GoogleWorkspaceIntegration,
            IntegrationType.MICROSOFT_365: Microsoft365Integration,
            IntegrationType.SLACK: SlackIntegration,
            IntegrationType.GITHUB: GitHubIntegration,
            IntegrationType.JIRA: JiraIntegration,
            IntegrationType.NOTION: NotionIntegration,
        }
        
        connector_class = connector_map.get(integration.type)
        if connector_class:
            return connector_class(integration)
        return None

