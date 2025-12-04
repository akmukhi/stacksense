from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from services.detection.detection_service import DetectionService
from models.organization import Organization
import os

class DetectionJob:
    """Scheduled job for periodic detection scans"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.interval_hours = int(os.getenv('DETECTION_SCAN_INTERVAL_HOURS', 24))
    
    def run_scan(self):
        """Run detection scan for all organizations"""
        db = SessionLocal()
        try:
            organizations = db.query(Organization).all()
            detection_service = DetectionService(db)
            
            import asyncio
            for org in organizations:
                try:
                    asyncio.run(detection_service.scan_organization(org.id))
                    print(f"Scan completed for organization {org.id}")
                except Exception as e:
                    print(f"Error scanning organization {org.id}: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduled job"""
        self.scheduler.add_job(
            self.run_scan,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id='detection_scan',
            name='Periodic SaaS Detection Scan',
            replace_existing=True
        )
        self.scheduler.start()
        print(f"Detection job started with interval: {self.interval_hours} hours")
    
    def stop(self):
        """Stop the scheduled job"""
        self.scheduler.shutdown()

