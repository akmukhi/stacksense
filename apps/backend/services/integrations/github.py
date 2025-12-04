from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from github import Github
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class GitHubIntegration(BaseIntegration):
    """GitHub integration connector"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.client = None
        self._load_client()
    
    def _load_client(self):
        """Load GitHub client from credentials"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            token = creds_dict.get('access_token')
            if token:
                self.client = Github(token)
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to GitHub via OAuth"""
        try:
            client_id = os.getenv('GITHUB_CLIENT_ID')
            client_secret = os.getenv('GITHUB_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                return False
            
            if auth_code:
                # Exchange code for token
                import httpx
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.post(
                        'https://github.com/login/oauth/access_token',
                        data={
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'code': auth_code
                        },
                        headers={'Accept': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        access_token = data.get('access_token')
                        
                        if access_token:
                            creds_dict = {
                                'access_token': access_token
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
                            
                            self.client = Github(access_token)
                            return True
                return False
            else:
                # Return authorization URL
                scopes = 'repo,read:org,read:user'
                redirect_uri = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:8000/api/integrations/github/callback')
                auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect_uri}"
                return auth_url
        except Exception as e:
            print(f"GitHub connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from GitHub"""
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
        """Test GitHub connection"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return False
            
            user = self.client.get_user()
            return user is not None
        except Exception:
            return False
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from GitHub"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            user = self.client.get_user()
            email = user.email
            if email:
                domain = email.split('@')[1] if '@' in email else None
                return [domain] if domain else []
            return []
        except Exception:
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from GitHub"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get authorized apps
            user = self.client.get_user()
            # GitHub API doesn't directly provide this, would need to use GraphQL or web scraping
            return []
        except Exception:
            return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs from GitHub"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # GitHub Enterprise only
            return []
        except Exception:
            return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data from GitHub"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            user = self.client.get_user()
            events = user.get_events()[:limit] if limit else user.get_events()
            
            activities = []
            for event in events:
                activities.append({
                    'type': event.type,
                    'repo': event.repo.name if event.repo else None,
                    'created_at': event.created_at.isoformat() if event.created_at else None
                })
            
            return activities
        except Exception:
            return []

