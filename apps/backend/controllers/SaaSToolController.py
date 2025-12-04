from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from DTO.SaaSTool import SaaSToolCreate, SaaSToolResponse, SaaSToolUpdate, SaaSToolListResponse
from models.saas_tool import SaaSTool, ToolStatus
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

saas_tool_controller_router = InferringRouter()

@cbv(saas_tool_controller_router)
class SaaSToolController:
    def __init__(self):
        pass
    
    @saas_tool_controller_router.get("/", response_model=SaaSToolListResponse)
    def list_tools(self, 
                   organization_id: int = Query(None),
                   status: str = Query(None),
                   db: Session = Depends(get_db)):
        try:
            query = db.query(SaaSTool)
            
            if organization_id:
                query = query.filter(SaaSTool.organization_id == organization_id)
            
            if status:
                query = query.filter(SaaSTool.status == ToolStatus(status))
            
            tools = query.all()
            
            # Count by status
            active_count = len([t for t in tools if t.status == ToolStatus.ACTIVE])
            unknown_count = len([t for t in tools if t.status == ToolStatus.UNKNOWN])
            duplicate_count = len([t for t in tools if t.status == ToolStatus.SUSPECTED_DUPLICATE])
            
            return SaaSToolListResponse(
                tools=tools,
                total=len(tools),
                active_count=active_count,
                unknown_count=unknown_count,
                duplicate_count=duplicate_count
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @saas_tool_controller_router.get("/{tool_id}", response_model=SaaSToolResponse)
    def get_tool(self, tool_id: int, db: Session = Depends(get_db)):
        tool = db.query(SaaSTool).filter(SaaSTool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool
    
    @saas_tool_controller_router.post("/", response_model=SaaSToolResponse)
    def create_tool(self, tool: SaaSToolCreate, db: Session = Depends(get_db)):
        try:
            new_tool = SaaSTool(
                name=tool.name,
                category=tool.category,
                vendor=tool.vendor,
                organization_id=tool.organization_id,
                status=ToolStatus.UNKNOWN
            )
            db.add(new_tool)
            db.commit()
            db.refresh(new_tool)
            return new_tool
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @saas_tool_controller_router.patch("/{tool_id}", response_model=SaaSToolResponse)
    def update_tool(self, tool_id: int, tool_update: SaaSToolUpdate, db: Session = Depends(get_db)):
        try:
            tool = db.query(SaaSTool).filter(SaaSTool.id == tool_id).first()
            if not tool:
                raise HTTPException(status_code=404, detail="Tool not found")
            
            if tool_update.name is not None:
                tool.name = tool_update.name
            if tool_update.category is not None:
                tool.category = tool_update.category
            if tool_update.vendor is not None:
                tool.vendor = tool_update.vendor
            if tool_update.status is not None:
                tool.status = tool_update.status
            
            db.commit()
            db.refresh(tool)
            return tool
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @saas_tool_controller_router.delete("/{tool_id}")
    def delete_tool(self, tool_id: int, db: Session = Depends(get_db)):
        try:
            tool = db.query(SaaSTool).filter(SaaSTool.id == tool_id).first()
            if not tool:
                raise HTTPException(status_code=404, detail="Tool not found")
            
            db.delete(tool)
            db.commit()
            return {"status": "deleted"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

