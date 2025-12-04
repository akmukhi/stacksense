from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from slack_sdk import WebClient
from slack_sdk.oauth import OAuthStateUtils
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class SlackIntegration(BaseIntegration):
    """Slack integration connector"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.client = None
        self._load_client()
    
    def _load_client(self):
        """Load Slack client from credentials"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            token = creds_dict.get('access_token')
            if token:
                self.client = WebClient(token=token)
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to Slack via OAuth"""
        try:
            client_id = os.getenv('SLACK_CLIENT_ID')
            client_secret = os.getenv('SLACK_CLIENT_SECRET')
            redirect_uri = os.getenv('SLACK_REDIRECT_URI', 'http://localhost:8000/api/integrations/slack/callback')
            
            if not client_id or not client_secret:
                return False
            
            if auth_code:
                # Exchange code for token
                import httpx
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.post(
                        'https://slack.com/api/oauth.v2.access',
                        data={
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'code': auth_code,
                            'redirect_uri': redirect_uri
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('ok'):
                            access_token = data.get('authed_user', {}).get('access_token') or data.get('access_token')
                            
                            creds_dict = {
                                'access_token': access_token,
                                'team_id': data.get('team', {}).get('id'),
                                'team_name': data.get('team', {}).get('name')
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
                            
                            self.client = WebClient(token=access_token)
                            return True
                return False
            else:
                # Return authorization URL
                scopes = ['users:read', 'users:read.email', 'team:read']
                auth_url = f"https://slack.com/oauth/v2/authorize?client_id={client_id}&scope={','.join(scopes)}&redirect_uri={redirect_uri}"
                return auth_url
        except Exception as e:
            print(f"Slack connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Slack"""
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
        """Test Slack connection"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return False
            
            response = self.client.auth_test()
            return response.get('ok', False)
        except Exception:
            return False
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from Slack workspace"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get team info
            team_info = self.client.team_info()
            if team_info.get('ok'):
                domain = team_info.get('team', {}).get('domain')
                if domain:
                    return [f"{domain}.slack.com"]
            return []
        except Exception:
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from Slack"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get apps installed in workspace
            apps = self.client.apps_list()
            if apps.get('ok'):
                return apps.get('apps', [])
            return []
        except Exception:
            return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs from Slack"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Slack doesn't provide direct SSO logs via API
            # Would need Enterprise Grid with audit logs API
            return []
        except Exception:
            return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data from Slack"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get users
            users = self.client.users_list()
            if users.get('ok'):
                user_list = users.get('members', [])
                if user_email:
                    user_list = [u for u in user_list if u.get('profile', {}).get('email') == user_email]
                return user_list
            return []
        except Exception:
            return []

