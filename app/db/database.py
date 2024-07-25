from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.v1.models import Base

from app.api.products.models import Base

DATABASE_URL = "sqlite:///./database_V1.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
