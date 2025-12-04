from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from jira import JIRA
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class JiraIntegration(BaseIntegration):
    """Jira integration connector"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.client = None
        self._load_client()
    
    def _load_client(self):
        """Load Jira client from credentials"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            server = creds_dict.get('server')
            token = creds_dict.get('api_token')
            if server and token:
                self.client = JIRA(server=server, token_auth=token)
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to Jira"""
        try:
            server = os.getenv('JIRA_SERVER')
            email = os.getenv('JIRA_EMAIL')
            api_token = os.getenv('JIRA_API_TOKEN')
            
            if server and email and api_token:
                creds_dict = {
                    'server': server,
                    'email': email,
                    'api_token': api_token
                }
                
                encrypted = self.encrypt_credentials(creds_dict)
                self.integration.credentials = encrypted
                self.integration.status = IntegrationStatus.CONNECTED
                self.integration.connected_at = datetime.utcnow()
                
                from database import SessionLocal
                db = SessionLocal()
                try:
                    db.add(self.integration)
                    db.commit()
                finally:
                    db.close()
                
                self.client = JIRA(server=server, basic_auth=(email, api_token))
                return True
            return False
        except Exception as e:
            print(f"Jira connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Jira"""
        self.integration.status = IntegrationStatus.DISCONNECTED
        self.integration.credentials = None
        from database import SessionLocal
        db = SessionLocal()
        try:
            db.add(self.integration)
            db.commit()
            return True
        except Exception:
            return False
        finally:
            db.close()
    
    async def test_connection(self) -> bool:
        """Test Jira connection"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return False
            
            self.client.current_user()
            return True
        except Exception:
            return False
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from Jira"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get current user email
            user = self.client.current_user()
            email = user.emailAddress if hasattr(user, 'emailAddress') else None
            if email:
                domain = email.split('@')[1] if '@' in email else None
                return [domain] if domain else []
            return []
        except Exception:
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from Jira"""
        # Jira doesn't provide OAuth app list via API
        return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs from Jira"""
        # Jira Cloud doesn't provide SSO logs via API
        return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data from Jira"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get issues assigned to user or created by user
            jql = f'assignee = {user_email}' if user_email else 'order by updated DESC'
            issues = self.client.search_issues(jql, maxResults=limit)
            
            activities = []
            for issue in issues:
                activities.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'updated': issue.fields.updated
                })
            
            return activities
        except Exception:
            return []

