# app/api/v1/controllers.py

import random
from app.api.v1.models import OTP, PasswordResetToken, User_Register, User_login
from app.api.v1.schemas import OTPResponseSchema, RegisterRequest, VerifyRequest, LoginRequest, ForgetPasswordRequest, ResetPasswordRequest
from app.utils.security import create_access_token, create_refresh_token, verify_password, hash_password

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.api.v1.models import User_Register, OTP 



import logging
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_all_users(db: Session):
    try:
        users = db.query(User_Register).all()
        return users
    except Exception as e:
        logger.error(f"Error while retrieving users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving users"
        )

def register_user(request: RegisterRequest, db: Session):
    if request.password != request.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if db.query(User_Register).filter(User_Register.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        hashed_password = hash_password(request.password)
        user = User_Register(
            firstname=request.firstname,
            lastname=request.lastname,
            email=request.email,
            is_active=False,
            hashed_password=hashed_password,
            role=request.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Registration successful, please verify your email",
            "info": {
                "id": user.id,
                "timestamp": datetime.now().isoformat(),
                "status": 200,
                "role": user.role or None  # Ensure role is None if it's not set
            }
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )

def verify_user(request: VerifyRequest, db: Session):
    user = db.query(User_Register).filter(User_Register.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{request.email} - not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{user.role} already verified"
        )
    
    user.is_active = True
    user.updated_at = datetime.now()
    
    try:
        db.commit()
        return {"email": f"{request.email} Verify successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error while verifying the user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying the user"
        )

def login_user(request: LoginRequest, db: Session):
    user = db.query(User_Register).filter(User_Register.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify your email before logging in"
        )
    
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    
    login_log = User_login(
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        role=user.role,
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=user.is_active
    )
    db.add(login_log)
    db.commit()
    
    return {
        "message": f"{request.email} : Login successful",
        "status": {
            "data": {
                "jwt": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 3600
                },
                "refresh": {
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": 86400
                }
            }
        }
    }

def generate_password_reset_token(email: str, db: Session) -> str:
    token = str(uuid.uuid4())
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(
        id=str(uuid.uuid4()),
        email=email,
        token=token,
        expires_at=expiration_time
    )
    
    try:
        db.add(reset_token)
        db.commit()
        logger.info(f"Generated new password reset token for {email}")
    except Exception as e:
        logger.error(f"Error while generating password reset token: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
    return token

def forget_password(request: ForgetPasswordRequest, db: Session):
    user = db.query(User_Register).filter(User_Register.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        token = generate_password_reset_token(request.email, db)
    except HTTPException as e:
        logger.error(f"Error in forget_password function: {e.detail}")
        raise
    
    return {
        "message": "success",
        "status": 200,
        "data": {
            "forgot_password": {
                "password_token": token
            }
        }
    }

def reset_password(request: ResetPasswordRequest, db: Session):
    token = request.password_token
    new_password = request.password
    if new_password != request.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = db.query(User_Register).filter(User_Register.email == reset_token.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = hash_password(new_password)
    db.commit()
    
    reset_token.is_used = True
    db.commit()
    
    return {
        "message": "success",
        "status": 200,
        "data": {
            "message": "Password reset successfully"
        }
    }

def request_otp(email: str, db: Session) -> OTPResponseSchema:
    # Check if user exists
    user = db.query(User_Register).filter(User_Register.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)  # OTP valid for 5 minutes

    otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
    db.add(otp)
    db.commit()

    # Send OTP via email or SMS (Here we're just returning it for simplicity)
    return OTPResponseSchema(otp_code=otp_code)

def verify_otp(email: str, otp_code: str, db: Session) -> OTPResponseSchema:
    # Find OTP record
    otp = db.query(OTP).filter(OTP.email == email, OTP.otp_code == otp_code, OTP.active == True).first()

    if not otp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid OTP or expired")

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

    # Mark OTP as used
    otp.active = False
    db.commit()

    # Generate tokens for authenticated user
    user = db.query(User_Register).filter(User_Register.email == email).first()
    access_token = create_access_token({"sub": user.email})
    return OTPResponseSchema(access_token=access_token)
