from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os

# You should store this in a secure place, e.g., environment variable or secrets manager
FERNET_KEY = os.getenv("FERNET_KEY", "h2xN9Yn-akbmZ4kAEL0NSZCxfQ96RiNITszA1rqUWXs=")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY environment variable not set.")

fernet = Fernet(FERNET_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encrypt_value(value: str) -> str:
    """Encrypt a string using Fernet."""
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(token: str) -> str:
    """Decrypt a Fernet-encrypted string."""
    return fernet.decrypt(token.encode()).decode()


