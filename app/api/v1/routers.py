# app/api/v1/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.schemas import ForgetPasswordRequest, RegisterRequest, ResetPasswordRequest, VerifyRequest, LoginRequest, RegisterResponse, VerifyResponse, LoginResponse, UserRegister
from app.api.v1.controllers import forget_password, register_user, reset_password, verify_user, login_user, get_all_users
from app.db.database import get_db

from typing import List


router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    data = register_user(request, db)
    return {
        "message": "User registered successfully",
        "data": data
    }

@router.post("/verify")
async def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    try:
        message = verify_user(request, db)
        return message
    except HTTPException as e:
        raise e  # Raise the HTTPException to be handled by FastAPI

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    data = login_user(request, db)
    return data

@router.post("/forget-password")
async def forget_password_endpoint(request: ForgetPasswordRequest, db: Session = Depends(get_db)):
    return forget_password(request, db)

@router.post("/reset-password")
async def reset_password_endpoint(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password(request, db)

@router.get("/users", response_model=List[UserRegister])
def get_all_users_endpoint(db: Session = Depends(get_db)):
    return get_all_users(db)



    