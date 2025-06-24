from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base_class import Base  # Base를 base_class.py에서 import
# from app.db.base_class import Base  # noqa
# from app.models.user import User  # noqa
# from app.models.note import Note  # noqa
# from app.models.chat import ChatSession, ChatMessage # noqa

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base() # This should be in base_class.py

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 