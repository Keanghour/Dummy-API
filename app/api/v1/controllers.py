# app/api/v1/controllers.py
import logging
import uuid
from sqlalchemy.orm import Session
from app.api.v1.models import PasswordResetToken, User_Register, User_login
from app.api.v1.schemas import RegisterRequest, VerifyRequest, LoginRequest, ForgetPasswordRequest, ResetPasswordRequest
from app.utils.jwt import create_access_token, create_refresh_token, verify_password, hash_password
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

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
    # Validate passwords match
    if request.password != request.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if the email already exists
    existing_user = db.query(User_Register).filter(User_Register.email == request.email).first()
    if existing_user:
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
            hashed_password=hashed_password,
            role=request.role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "id": user.id,
            "timestamp": datetime.now().isoformat(),
            "status": 200,
            "role": user.role
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )

def verify_user(request: VerifyRequest, db: Session):
    email = request.email
    
    user = db.query(User_Register).filter(User_Register.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{email} - not found"
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
        return {
            "email": f"{email} Verify successfully"
        }
    except Exception as e:
        db.rollback()
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
            detail=f"Please verified the {user.firstname} {user.lastname} before you login."
        )
    
    try:
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
            Payload=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
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
                    "data1": {
                        "jwt": {
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                            "expires_in": 86400
                        }
                    }
                }
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while logging in"
        )

def generate_password_reset_token(email: str, db: Session) -> str:
    token = str(uuid.uuid4())
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

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
    email = request.email
    user = db.query(User_Register).filter(User_Register.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        token = generate_password_reset_token(email, db)
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
    password_confirmation = request.password_confirmation
    
    if new_password != password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Retrieve and validate the token
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
    
    hashed_password = hash_password(new_password)
    user.hashed_password = hashed_password
    db.commit()
    
    # Mark the token as used
    reset_token.is_used = True
    db.commit()
    
    return {
        "message": "success",
        "status": 200,
        "data": {
            "message": "Password reset successfully"
        }
    }