"""
Legacy entity manager - kept for backward compatibility.
New code should use database.py and SQLAlchemy models directly.
"""
from database import SessionLocal, Base, engine

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Legacy compatibility - returns a database session
def get_entity_manager():
    return SessionLocal()

# Initialize database on import
init_db()