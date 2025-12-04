from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models.integration import Integration, IntegrationStatus, IntegrationType
from services.integrations import (
    GoogleWorkspaceIntegration,
    Microsoft365Integration,
    SlackIntegration,
    GitHubIntegration,
    JiraIntegration,
    NotionIntegration
)
import os

class ActivitySyncJob:
    """Scheduled job for syncing user activity from integrations"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.interval_hours = int(os.getenv('ACTIVITY_SYNC_INTERVAL_HOURS', 6))
    
    def sync_activities(self):
        """Sync user activities from all connected integrations"""
        db = SessionLocal()
        try:
            integrations = db.query(Integration).filter(
                Integration.status == IntegrationStatus.CONNECTED
            ).all()
            
            connector_map = {
                IntegrationType.GOOGLE_WORKSPACE: GoogleWorkspaceIntegration,
                IntegrationType.MICROSOFT_365: Microsoft365Integration,
                IntegrationType.SLACK: SlackIntegration,
                IntegrationType.GITHUB: GitHubIntegration,
                IntegrationType.JIRA: JiraIntegration,
                IntegrationType.NOTION: NotionIntegration,
            }
            
            for integration in integrations:
                try:
                    connector_class = connector_map.get(integration.type)
                    if connector_class:
                        connector = connector_class(integration)
                        # Note: sync() is not async, but we keep it for future async support
                        connector.sync()
                        print(f"Activity sync completed for integration {integration.id}")
                except Exception as e:
                    print(f"Error syncing integration {integration.id}: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduled job"""
        self.scheduler.add_job(
            self.sync_activities,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id='activity_sync',
            name='Periodic Activity Sync',
            replace_existing=True
        )
        self.scheduler.start()
        print(f"Activity sync job started with interval: {self.interval_hours} hours")
    
    def stop(self):
        """Stop the scheduled job"""
        self.scheduler.shutdown()

