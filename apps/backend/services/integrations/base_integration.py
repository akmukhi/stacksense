from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from models.integration import Integration, IntegrationType, IntegrationStatus

class BaseIntegration(ABC):
    """Base class for all integration connectors"""
    
    def __init__(self, integration: Integration):
        self.integration = integration
        self.type = integration.type
    
    @abstractmethod
    async def connect(self, auth_code: Optional[str] = None) -> bool:
        """Connect to the integration service. Returns True if successful."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the integration service."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is still valid."""
        pass
    
    @abstractmethod
    async def get_email_domains(self) -> List[str]:
        """Extract email domains from the integration."""
        pass
    
    @abstractmethod
    async def get_oauth_apps(self) -> List[Dict[str, Any]]:
        """Get list of OAuth applications connected to the integration."""
        pass
    
    @abstractmethod
    async def get_sso_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SSO authentication logs."""
        pass
    
    @abstractmethod
    async def get_user_activity(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user activity data."""
        pass
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypt credentials before storing. Override for custom encryption."""
        import json
        # In production, use proper encryption (e.g., Fernet from cryptography)
        return json.dumps(credentials)
    
    def decrypt_credentials(self, encrypted: str) -> Dict[str, Any]:
        """Decrypt credentials after retrieving. Override for custom decryption."""
        import json
        # In production, use proper decryption
        return json.loads(encrypted)
    
    def sync(self) -> bool:
        """Perform a sync operation. Default implementation."""
        try:
            import asyncio
            if asyncio.run(self.test_connection()):
                # Update last_sync_at
                from datetime import datetime
                from database import SessionLocal
                db = SessionLocal()
                try:
                    self.integration.last_sync_at = datetime.utcnow()
                    db.add(self.integration)
                    db.commit()
                    return True
                finally:
                    db.close()
            return False
        except Exception:
            return False

