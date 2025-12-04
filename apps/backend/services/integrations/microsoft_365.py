from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from msal import ConfidentialClientApplication, PublicClientApplication
from .base_integration import BaseIntegration
from models.integration import Integration, IntegrationType, IntegrationStatus

class Microsoft365Integration(BaseIntegration):
    """Microsoft 365 integration connector"""
    
    SCOPES = [
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/Directory.Read.All',
        'https://graph.microsoft.com/AuditLog.Read.All',
    ]
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.app = None
        self.token = None
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize MSAL application"""
        client_id = os.getenv('MICROSOFT_CLIENT_ID')
        client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
        tenant_id = os.getenv('MICROSOFT_TENANT_ID')
        
        if client_id and client_secret and tenant_id:
            self.app = ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=f"https://login.microsoftonline.com/{tenant_id}"
            )
    
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to Microsoft 365 via OAuth"""
        try:
            if not self.app:
                self._initialize_app()
            
            if auth_code:
                result = self.app.acquire_token_by_authorization_code(
                    auth_code,
                    scopes=self.SCOPES
                )
                
                if 'access_token' in result:
                    self.token = result['access_token']
                    
                    # Store credentials
                    creds_dict = {
                        'access_token': self.token,
                        'refresh_token': result.get('refresh_token'),
                        'expires_at': result.get('expires_in', 3600)
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
                    
                    return True
                return False
            else:
                # Return authorization URL
                auth_url = self.app.get_authorization_request_url(
                    scopes=self.SCOPES,
                    redirect_uri=os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8000/api/integrations/microsoft_365/callback')
                )
                return auth_url
        except Exception as e:
            print(f"Microsoft 365 connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Microsoft 365"""
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
        """Test Microsoft 365 connection"""
        try:
            if not self.token:
                self._load_token()
            if not self.token:
                return False
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                return response.status_code == 200
        except Exception:
            return False
    
    def _load_token(self):
        """Load token from credentials"""
        if self.integration.credentials:
            creds_dict = self.decrypt_credentials(self.integration.credentials)
            self.token = creds_dict.get('access_token')
    
    async def get_email_domains(self) -> List[str]:
        """Get email domains from Microsoft 365"""
        try:
            if not self.token:
                self._load_token()
            if not self.token:
                return []
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://graph.microsoft.com/v1.0/domains',
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    return [d.get('id') for d in data.get('value', []) if d.get('id')]
            return []
        except Exception:
            return []
    
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get OAuth applications from Microsoft 365"""
        try:
            if not self.token:
                self._load_token()
            if not self.token:
                return []
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://graph.microsoft.com/v1.0/applications',
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('value', [])
            return []
        except Exception:
            return []
    
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs"""
        try:
            if not self.token:
                self._load_token()
            if not self.token:
                return []
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://graph.microsoft.com/v1.0/auditLogs/signIns?$top={limit}',
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('value', [])
            return []
        except Exception:
            return []
    
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data"""
        try:
            if not self.token:
                self._load_token()
            if not self.token:
                return []
            
            import httpx
            async with httpx.AsyncClient() as client:
                url = 'https://graph.microsoft.com/v1.0/users'
                if user_email:
                    url = f'https://graph.microsoft.com/v1.0/users/{user_email}'
                
                response = await client.get(
                    url,
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('value', []) if isinstance(data, dict) and 'value' in data else [data]
            return []
        except Exception:
            return []

