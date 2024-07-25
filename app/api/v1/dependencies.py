# app/api/v1/dependencies.py

# from datetime import datetime, timedelta
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
# from app.core.config import settings
# from app.api.v1.models import User_Register
# from app.db.database import get_db

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         email = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         user = db.query(User_Register).filter(User_Register.email == email).first()
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# def get_current_active_user(current_user: User_Register = Depends(get_current_user)):
#     if not current_user.is_active:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
#     return current_user

# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=60)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
