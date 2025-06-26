# src/config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-")
    MOCK_MODE = os.getenv("TBLCONV_MOCK_MODE", "false").lower() == "true"
    VECTORSTORE_DIR = os.getenv("TBLCONV_VECTORSTORE_DIR", "./chroma_db")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/talk2tables")
    SCHEMA_JSON_DIR = os.getenv("TBLCONV_SCHEMA_JSON_DIR", "./schema_json")
    VECTORSTORE_DIR = os.getenv("TBLCONV_VECTORSTORE_DIR", "./chroma_db")
    FERNET_KEY = os.getenv("TBLCONV_FERNET_KEY", "h2xN9Yn-akbmZ4kAEL0NSZCxfQ96RiNITszA1rqUWXs=")  # Add more settings here as needed
    JWT_SECRET_KEY = os.getenv("TBLCONV_JWT_SECRET_KEY", "super-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("TBLCONV_ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    FRONTEND_URL = os.getenv("TBLCONV_FRONTEND_URL", "http://localhost:5173")

settings = Settings()
