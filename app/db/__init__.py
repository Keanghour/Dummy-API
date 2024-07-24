from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.api.v1.models import Base  # Import Base from your models

# Database setup
engine = create_engine(settings.DATABASE_URL)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
