"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.config import settings

# Resolve database path relative to project root
if settings.DATABASE_URL.startswith("sqlite"):
    # Extract path from SQLite URL
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not Path(db_path).is_absolute():
        # Make path relative to project root
        db_path = str(settings.PROJECT_ROOT / db_path)
    # Ensure parent directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{db_path}"
else:
    db_url = settings.DATABASE_URL

# Create engine
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
