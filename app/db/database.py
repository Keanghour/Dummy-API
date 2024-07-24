from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./database_V1.db"

# Create the engine and sessionmaker
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models
Base = declarative_base()

def init_db():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
