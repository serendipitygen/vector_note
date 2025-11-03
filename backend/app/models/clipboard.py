from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ClipboardProcessingLog(Base):
    __tablename__ = "clipboard_processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, nullable=False)  # 'text', 'image', 'url', 'file'
    processing_method = Column(String, nullable=False)  # 'ocr', 'direct', 'web_scraping', 'file_extraction'
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")