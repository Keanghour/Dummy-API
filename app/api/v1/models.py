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
    email = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

class User_Register(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, index=True, default=generate_random_id)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User_login(Base):
    __tablename__ = 'user_logins'
    
    id = Column(String, primary_key=True, index=True, default=generate_random_id)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, index=True)
    role = Column(String)
    access_token = Column(String)
    token_type = Column(String)
    expires_in = Column(Integer)
    Payload = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    request_time = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    active = Column(Boolean, default=True)