from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class GoogleWorkspaceIntegration(BaseIntegration):
    """Google Workspace integration connector"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.user.readonly',
        'https://www.googleapis.com/auth/admin.directory.domain.readonly',
        'https://www.googleapis.com/auth/admin.reports.audit.readonly',
    ]
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.credentials = None
        self.service = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from integration"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            self.credentials = Credentials.from_authorized_user_info(creds_dict)
            if self.credentials and self.credentials.valid:
                self.service = build('admin', 'directory_v1', credentials=self.credentials)
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to Google Workspace via OAuth"""
        try:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/integrations/google_workspace/callback')
            
            if not client_id or not client_secret:
                return False
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            if auth_code:
                flow.fetch_token(code=auth_code)
                self.credentials = flow.credentials
                
                # Store credentials
                creds_dict = {
                    'token': self.credentials.token,
                    'refresh_token': self.credentials.refresh_token,
                    'token_uri': self.credentials.token_uri,
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scopes': self.credentials.scopes
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
                
                self.service = build('admin', 'directory_v1', credentials=self.credentials)
                return True
            else:
                # Return authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                return auth_url
        except Exception as e:
            print(f"Google Workspace connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google Workspace"""
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
        """Test Google Workspace connection"""
        try:
            if not self.service:
                self._load_credentials()
            if not self.service:
                return False
            
            # Try to get domains
            domains = self.service.domains().list(customer='my_customer').execute()
            return True
        except Exception:
            return False
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from Google Workspace"""
        try:
            if not self.service:
                self._load_credentials()
            if not self.service:
                return []
            
            domains_result = self.service.domains().list(customer='my_customer').execute()
            domains = domains_result.get('domains', [])
            return [d.get('domainName') for d in domains if d.get('domainName')]
        except Exception as e:
            print(f"Error getting email domains: {e}")
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from Google Workspace"""
        try:
            if not self.service:
                self._load_credentials()
            if not self.service:
                return []
            
            # Get users and check their OAuth apps
            # This is a simplified version - in production, use Admin SDK Reports API
            users_result = self.service.users().list(customer='my_customer', maxResults=10).execute()
            users = users_result.get('users', [])
            
            oauth_apps = []
            for user in users:
                # Extract OAuth apps from user data
                # This would need Admin SDK Reports API for full implementation
                pass
            
            return oauth_apps
        except Exception:
            return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs"""
        try:
            if not self.service:
                self._load_credentials()
            if not self.service:
                return []
            
            # Use Admin SDK Reports API
            reports_service = build('admin', 'reports_v1', credentials=self.credentials)
            activities = reports_service.activities().list(
                userKey='all',
                applicationName='login',
                maxResults=limit
            ).execute()
            
            logs = []
            for activity in activities.get('items', []):
                logs.append({
                    'user': activity.get('actor', {}).get('email'),
                    'timestamp': activity.get('id', {}).get('time'),
                    'ip_address': activity.get('ipAddress'),
                    'event_type': activity.get('events', [{}])[0].get('name') if activity.get('events') else None
                })
            
            return logs
        except Exception:
            return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data"""
        try:
            if not self.service:
                self._load_credentials()
            if not self.service:
                return []
            
            # Get user activity from Admin SDK
            activities = []
            # Implementation would use Reports API to get user activities
            return activities
        except Exception:
            return []

