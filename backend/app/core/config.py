from pydantic_settings import BaseSettings
from typing import Optional, Any, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vector Note"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database - PostgreSQL 설정
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432") 
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "vector_note")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "vector_note_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "vector_note")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?client_encoding=utf8"
    
    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Google Gemini API
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # 파일 업로드 설정
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    
    # Qdrant 설정
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 보안 설정
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def allow_credentials(self) -> bool:
        return not self.is_production
    
    def get_cors_origins(self) -> List[str]:
        """CORS origins 반환"""
        if self.is_production:
            return self.BACKEND_CORS_ORIGINS
        return ["*"]  # 개발 환경에서는 모든 origin 허용

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # 추가 환경 변수를 무시

settings = Settings()

# 프로덕션 환경에서 기본 SECRET_KEY 사용 시 경고
if settings.is_production and settings.SECRET_KEY == "your-secret-key-change-this-in-production":
    raise ValueError("Production 환경에서는 SECRET_KEY를 반드시 변경해야 합니다!") 