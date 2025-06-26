import os
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken
from src.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_fernet_key() -> bytes:
    key = settings.FERNET_KEY
    if not key:
        raise ValueError("FERNET_KEY environment variable not set.")
    try:
        return key.encode() if isinstance(key, str) else key
    except Exception as e:
        raise ValueError(f"Invalid FERNET_KEY: {e}")

fernet = Fernet(get_fernet_key())

def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def encrypt_value(value: str) -> str:
    """Encrypt a string using Fernet and return as base64 string."""
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(token: str) -> str:
    """Decrypt a Fernet-encrypted base64 string."""
    try:
        return fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid encryption token")
