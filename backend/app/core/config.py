from pydantic_settings import BaseSettings
from typing import Optional, Any, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vector Note"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database - PostgreSQL 설정 (인코딩 문제 해결)
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    print(POSTGRES_SERVER)
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432") 
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "vector_note")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "vector_note_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "vector_note")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}?client_encoding=utf8"
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Milvus
    # MILVUS_HOST: str = "172.30.1.23"
    # MILVUS_PORT: int = 19530
    
    # Google Gemini API
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # File upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    # Qdrant
    # QDRANT_URL: str = os.getenv("QDRANT_URL")
    # QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")

    class Config:
        case_sensitive = True

settings = Settings() 