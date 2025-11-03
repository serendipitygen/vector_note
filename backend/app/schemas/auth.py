from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

class UserBase(BaseModel):
    """사용자 기본 정보"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """사용자 생성 요청"""
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """비밀번호 유효성 검증"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호는 최소 하나의 문자를 포함해야 합니다.')
        if not re.search(r'[0-9]', v):
            raise ValueError('비밀번호는 최소 하나의 숫자를 포함해야 합니다.')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 유효성 검증"""
        if len(v) < 3:
            raise ValueError('사용자명은 최소 3자 이상이어야 합니다.')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('사용자명은 영문자, 숫자, 언더스코어만 사용할 수 있습니다.')
        return v

class UserResponse(UserBase):
    """사용자 응답 정보"""
    id: int
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """JWT 토큰 페이로드 데이터"""
    username: Optional[str] = None

class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str
    password: str 