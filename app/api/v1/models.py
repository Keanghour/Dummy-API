# app/api/v1/models.py
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import base64
import os

Base = declarative_base()

def generate_random_id():
    return base64.b64encode(os.urandom(16)).decode('utf-8')

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    
    id = Column(String, primary_key=True, index=True)
    # email = Column(String, index=True)
    email = Column(String, index=True, unique=False)
    token = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

class User_Register(Base):
    __tablename__ = 'register_logs'
    
    id = Column(String, primary_key=True, default=generate_random_id)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=False)

class User_login(Base):
    __tablename__ = 'login_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    token_type = Column(String, default='bearer')
    expires_in = Column(Integer, nullable=False)
    Payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=False)
