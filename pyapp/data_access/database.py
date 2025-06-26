from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pyapp.config.settings import settings

# Create engine using environment variable
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session (used in FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
