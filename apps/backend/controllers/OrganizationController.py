from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from DTO.Organization import OrganizationCreate, OrganizationResponse
from models.organization import Organization
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

organization_controller_router = InferringRouter()

@cbv(organization_controller_router)
class OrganizationController:
    def __init__(self):
        pass
    
    @organization_controller_router.post("/", response_model=OrganizationResponse)
    def create_organization(self, org: OrganizationCreate, db: Session = Depends(get_db)):
        try:
            # Check if domain already exists
            if org.domain:
                existing = db.query(Organization).filter(Organization.domain == org.domain).first()
                if existing:
                    raise HTTPException(status_code=422, detail="Organization with this domain already exists")
            
            new_org = Organization(name=org.name, domain=org.domain)
            db.add(new_org)
            db.commit()
            db.refresh(new_org)
            return new_org
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @organization_controller_router.get("/{org_id}", response_model=OrganizationResponse)
    def get_organization(self, org_id: int, db: Session = Depends(get_db)):
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org
    
    @organization_controller_router.get("/", response_model=list[OrganizationResponse])
    def list_organizations(self, db: Session = Depends(get_db)):
        return db.query(Organization).all()

