from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from DTO.Integration import IntegrationCreate, IntegrationResponse, IntegrationConnect
from models.integration import Integration, IntegrationType, IntegrationStatus
from services.integrations import (
    GoogleWorkspaceIntegration,
    Microsoft365Integration,
    SlackIntegration,
    GitHubIntegration,
    JiraIntegration,
    NotionIntegration
)
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

integration_controller_router = InferringRouter()

@cbv(integration_controller_router)
class IntegrationController:
    def __init__(self):
        pass
    
    @integration_controller_router.post("/", response_model=IntegrationResponse)
    def create_integration(self, integration: IntegrationCreate, db: Session = Depends(get_db)):
        try:
            new_integration = Integration(
                type=integration.type,
                organization_id=integration.organization_id,
                credentials=integration.credentials,
                status=IntegrationStatus.PENDING
            )
            db.add(new_integration)
            db.commit()
            db.refresh(new_integration)
            return new_integration
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @integration_controller_router.get("/", response_model=list[IntegrationResponse])
    def list_integrations(self, organization_id: int = Query(None), db: Session = Depends(get_db)):
        query = db.query(Integration)
        if organization_id:
            query = query.filter(Integration.organization_id == organization_id)
        return query.all()
    
    @integration_controller_router.get("/{integration_id}", response_model=IntegrationResponse)
    def get_integration(self, integration_id: int, db: Session = Depends(get_db)):
        integration = db.query(Integration).filter(Integration.id == integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return integration
    
    @integration_controller_router.post("/{integration_type}/connect")
    async def connect_integration(self, integration_type: str, connect_data: IntegrationConnect, 
                                 auth_code: str = Query(None), db: Session = Depends(get_db)):
        try:
            # Get or create integration
            integration = db.query(Integration).filter(
                Integration.type == IntegrationType(integration_type),
                Integration.organization_id == connect_data.organization_id
            ).first()
            
            if not integration:
                integration = Integration(
                    type=IntegrationType(integration_type),
                    organization_id=connect_data.organization_id,
                    status=IntegrationStatus.PENDING
                )
                db.add(integration)
                db.commit()
                db.refresh(integration)
            
            # Get connector
            connector_map = {
                'google_workspace': GoogleWorkspaceIntegration,
                'microsoft_365': Microsoft365Integration,
                'slack': SlackIntegration,
                'github': GitHubIntegration,
                'jira': JiraIntegration,
                'notion': NotionIntegration,
            }
            
            connector_class = connector_map.get(integration_type)
            if not connector_class:
                raise HTTPException(status_code=400, detail=f"Unknown integration type: {integration_type}")
            
            connector = connector_class(integration)
            
            # Connect
            result = await connector.connect(auth_code or connect_data.auth_code)
            
            if isinstance(result, str):
                # Return auth URL
                return {"auth_url": result, "requires_oauth": True}
            elif result:
                db.commit()
                return {"status": "connected", "integration_id": integration.id}
            else:
                raise HTTPException(status_code=400, detail="Failed to connect integration")
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @integration_controller_router.delete("/{integration_id}")
    async def disconnect_integration(self, integration_id: int, db: Session = Depends(get_db)):
        try:
            integration = db.query(Integration).filter(Integration.id == integration_id).first()
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
            
            # Get connector and disconnect
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
                connector = connector_class(integration)
                await connector.disconnect()
            
            db.delete(integration)
            db.commit()
            return {"status": "disconnected"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

