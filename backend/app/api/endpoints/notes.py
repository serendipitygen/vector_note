from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.note import Note
from app.models.user import User
from app.services.milvus_service import insert_vectors, delete_vectors
from app.services.embedding_service import EmbeddingService
from app.services.content_extractor import ContentExtractor
from app.services.news_reader_service import extract_content_from_url
from app.core.deps import get_current_user
import os
from app.core.config import settings

router = APIRouter()
embedding_service = EmbeddingService()
content_extractor = ContentExtractor()

@router.post("/notes/")
async def create_note(
    title: str = Form(...),
    content: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    source_type: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새로운 노트 생성"""
    try:
        print(f"Creating note with title: {title}, source_type: {source_type}")
        
        note = Note(
            title=title,
            category=category,
            source_type=source_type,
            user_id=current_user.id
        )
        
        extracted_text = None
        
        if source_type == "file" and file:
            print(f"Processing file: {file.filename}")
            # 파일 저장
            file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                file_content = await file.read()
                buffer.write(file_content)
            
            note.source_path = file_path
            extracted_text = content_extractor.extract_from_file(file_path)
            
        elif source_type == "url":
            print(f"Processing URL: {content}")
            note.source_path = content
            extracted_text = content_extractor.extract_from_url(content)
            
        else:
            print(f"Processing text content")
            extracted_text = content
        
        if extracted_text:
            note.content = content_extractor.clean_text(extracted_text)
            print(f"Setting note content: {note.content[:100]}...")
            
            chunks, embeddings = embedding_service.process_text(note.content)
            
            db.add(note)
            db.commit()
            db.refresh(note)
            print(f"Note saved with ID: {note.id}")
            
            # Milvus에 벡터 저장
            insert_vectors(
                collection_name="notes",
                vectors=embeddings,
                ids=list(range(len(chunks))),
                note_ids=[note.id] * len(chunks),
                contents=chunks
            )
            
            return note
        else:
            print("Failed to extract content")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract content"
            )
            
    except Exception as e:
        print(f"Error creating note: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/notes/")
def get_notes(
    skip: int = 0,
    limit: int = 5,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """노트 목록 조회"""
    try:
        query = db.query(Note).filter(Note.user_id == current_user.id)
        
        if category:
            query = query.filter(Note.category == category)
        
        if search:
            query = query.filter(
                Note.title.ilike(f"%{search}%") |
                Note.content.ilike(f"%{search}%")
            )
        
        total = query.count()
        notes = query.offset(skip).limit(limit).all()
        
        return {"notes": notes, "total": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/notes/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 노트 조회"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """노트 삭제"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # 파일이 있는 경우 삭제
    if note.source_type == "file" and note.source_path:
        try:
            os.remove(note.source_path)
        except OSError:
            pass
    
    # Milvus에서 벡터 삭제
    try:
        delete_vectors("notes", note_id)
    except Exception as e:
        print(f"Failed to delete vectors: {e}")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted"} 