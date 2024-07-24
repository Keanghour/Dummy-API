# app/api/v1/schemas.py
from pydantic import BaseModel
from typing import Optional


from datetime import datetime

class UserRegisterBase(BaseModel):
    firstname: str
    lastname: str
    email: str
    role: str
    is_active: bool

class UserRegisterCreate(UserRegisterBase):
    hashed_password: str

class UserRegister(UserRegisterBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True



class RegisterRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str
    password_confirmation: str
    role: str

class VerifyRequest(BaseModel):
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    message: str
    data: dict

class VerifyResponse(BaseModel):
    email: str

class LoginResponse(BaseModel):
    message: str
    status: dict

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    password: str
    password_confirmation: str
    password_token: str