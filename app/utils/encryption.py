# app/api/products/encryption.py

from cryptography.fernet import Fernet
from app.core.config import settings

# SECRET_KEY = b'oRc5Hdo6Hv1s1rEmHIFVaka78ueJASGDUT-xgv0iBHY='  # Ensure this matches the key used for encryption
# fernet = Fernet(SECRET_KEY)

# Initialize Fernet with the key from .env
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt the data using Fernet"""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_text: str) -> str:
    try:
        decrypted_data = fernet.decrypt(encrypted_text.encode()).decode()
        return decrypted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption error: {str(e)}")