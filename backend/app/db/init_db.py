from sqlalchemy import create_engine
from app.core.config import settings
from app.models.user import Base as UserBase
from app.models.note import Base as NoteBase

def init_db():
    """PostgreSQL 데이터베이스 테이블 초기화"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # 모든 테이블 생성
    UserBase.metadata.create_all(bind=engine)
    NoteBase.metadata.create_all(bind=engine)
    
    print("PostgreSQL database tables created successfully!")

if __name__ == "__main__":
    init_db() 