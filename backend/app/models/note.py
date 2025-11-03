from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)
    
    # Source information
    source_type = Column(String)  # 'text', 'file', 'url', 'clipboard'
    source_path = Column(String, nullable=True)
    
    # Clipboard-specific fields
    clipboard_type = Column(String, nullable=True)  # 'text', 'image', 'url', 'file'
    original_format = Column(String, nullable=True)  # MIME type or format info
    extraction_method = Column(String, nullable=True)  # 'ocr', 'direct', 'web_scraping'
    
    # Metadata for additional information
    metadata = Column(JSON, nullable=True)  # Store additional metadata

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="notes")

    # Milvus collection name will be derived from the table name 