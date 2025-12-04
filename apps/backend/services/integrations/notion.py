from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from notion_client import Client
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class NotionIntegration(BaseIntegration):
    """Notion integration connector"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.client = None
        self._load_client()
    
    def _load_client(self):
        """Load Notion client from credentials"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            token = creds_dict.get('access_token')
            if token:
                self.client = Client(auth=token)
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to Notion via OAuth"""
        try:
            client_id = os.getenv('NOTION_CLIENT_ID')
            client_secret = os.getenv('NOTION_CLIENT_SECRET')
            redirect_uri = os.getenv('NOTION_REDIRECT_URI', 'http://localhost:8000/api/integrations/notion/callback')
            
            if not client_id or not client_secret:
                return False
            
            if auth_code:
                # Exchange code for token
                import httpx
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.post(
                        'https://api.notion.com/v1/oauth/token',
                        data={
                            'grant_type': 'authorization_code',
                            'code': auth_code,
                            'redirect_uri': redirect_uri
                        },
                        auth=(client_id, client_secret)
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        access_token = data.get('access_token')
                        
                        if access_token:
                            creds_dict = {
                                'access_token': access_token,
                                'workspace_id': data.get('workspace_id'),
                                'workspace_name': data.get('workspace_name')
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
                            
                            self.client = Client(auth=access_token)
                            return True
                return False
            else:
                # Return authorization URL
                scopes = 'read'
                auth_url = f"https://api.notion.com/v1/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"
                return auth_url
        except Exception as e:
            print(f"Notion connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Notion"""
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
        """Test Notion connection"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return False
            
            # Test by getting users
            self.client.users.list()
            return True
        except Exception:
            return False
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from Notion"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get workspace users
            users = self.client.users.list()
            domains = set()
            for user in users.get('results', []):
                if user.get('type') == 'person' and user.get('person', {}).get('email'):
                    email = user['person']['email']
                    domain = email.split('@')[1] if '@' in email else None
                    if domain:
                        domains.add(domain)
            return list(domains)
        except Exception:
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from Notion"""
        # Notion doesn't provide OAuth app list via API
        return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs from Notion"""
        # Notion doesn't provide SSO logs via API
        return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data from Notion"""
        try:
            if not self.client:
                self._load_client()
            if not self.client:
                return []
            
            # Get pages/databases
            search_results = self.client.search(query=user_email if user_email else "")
            return search_results.get('results', [])
        except Exception:
            return []

