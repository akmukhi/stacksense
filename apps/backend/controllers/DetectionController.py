from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from DTO.Detection import DetectionScanRequest, DetectionResult
from services.detection.detection_service import DetectionService
from models.integration import IntegrationType
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

detection_controller_router = InferringRouter()

@cbv(detection_controller_router)
class DetectionController:
    def __init__(self):
        pass
    
    @detection_controller_router.post("/scan", response_model=DetectionResult)
    async def scan_organization(self, scan_request: DetectionScanRequest, db: Session = Depends(get_db)):
        try:
            detection_service = DetectionService(db)
            
            # Convert integration type strings to enums if provided
            integration_types = None
            if scan_request.integration_types:
                integration_types = [IntegrationType(t) for t in scan_request.integration_types]
            
            result = await detection_service.scan_organization(
                scan_request.organization_id,
                integration_types
            )
            
            return DetectionResult(
                tools_detected=result['tools_detected'],
                new_tools=result['new_tools'],
                duplicates_found=result['duplicates_found'],
                scan_completed_at=result['scan_completed_at']
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

