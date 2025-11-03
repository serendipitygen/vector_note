from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator:
    """데이터베이스 세션 생성"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# get_current_user는 app.core.security에서 import하여 사용
from app.core.security import get_current_user 