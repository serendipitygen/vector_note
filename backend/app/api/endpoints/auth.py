from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.core.deps import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, Token, UserResponse

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """새 사용자 등록"""
    # 기존 사용자 확인
    user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 사용자명 또는 이메일입니다."
        )
    
    # 새 사용자 생성
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """사용자 로그인"""
    # 사용자 확인
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비활성화된 사용자 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(security.get_current_user)
) -> Any:
    """현재 사용자 정보 조회"""
    return current_user 