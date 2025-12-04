from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn 
from controllers.UserController import user_controller_router
from controllers.OrganizationController import organization_controller_router
from controllers.IntegrationController import integration_controller_router
from controllers.SaaSToolController import saas_tool_controller_router
from controllers.DetectionController import detection_controller_router
from controllers.DashboardController import dashboard_controller_router
import os
from dotenv import load_dotenv
from database import init_db

app = FastAPI(
    title="StackSense API",
    description="SaaS Discovery and Management System",
    version="1.0.0"
)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Initialize database
init_db()

tags_metadata = [
    {"name": "Users", "description": "Operations Related to User Management"},
    {"name": "Organizations", "description": "Organization management"},
    {"name": "Integrations", "description": "Integration management and OAuth flows"},
    {"name": "SaaS Tools", "description": "SaaS tool queries and management"},
    {"name": "Detection", "description": "SaaS detection and scanning"},
    {"name": "Dashboard", "description": "Dashboard statistics and data"},
]

#Include the routers from the controller modules
app.include_router(user_controller_router, prefix="/users", tags=["Users"])
app.include_router(organization_controller_router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(integration_controller_router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(saas_tool_controller_router, prefix="/api/tools", tags=["SaaS Tools"])
app.include_router(detection_controller_router, prefix="/api/detections", tags=["Detection"])
app.include_router(dashboard_controller_router, prefix="/api/dashboard", tags=["Dashboard"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run("app:app", host=os.environ.get("HOST"), port=int(os.environ.get("PORT")), reload=True)
