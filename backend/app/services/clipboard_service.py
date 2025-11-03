from typing import Optional, Dict, Any, List
import re
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.clipboard import ClipboardProcessingLog
from app.services.content_extractor import ContentExtractor

class ClipboardProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.content_extractor = ContentExtractor()
    
    def detect_content_type(self, content: str) -> str:
        """클립보드 콘텐츠 타입 감지"""
        if not content or not isinstance(content, str):
            return "unknown"
        
        content = content.strip()
        
        # URL 패턴 감지
        url_pattern = r'^https?://[^\s]+$'
        if re.match(url_pattern, content):
            return "url"
        
        # 파일 경로 패턴 감지 (Windows/Unix 경로)
        file_path_patterns = [
            r'^[A-Za-z]:\\[^<>:"|?*\n\r]+$',  # Windows 절대 경로
            r'^\\\\[^<>:"|?*\n\r]+$',         # UNC 경로
            r'^/[^<>:"|?*\n\r]+$',            # Unix 절대 경로
            r'^\.{1,2}/[^<>:"|?*\n\r]+$'      # 상대 경로
        ]
        
        for pattern in file_path_patterns:
            if re.match(pattern, content):
                return "file"
        
        # HTML 콘텐츠 감지
        if content.strip().startswith('<') and content.strip().endswith('>'):
            return "html"
        
        # 기본적으로 텍스트로 처리
        return "text"
    
    def process_text_content(self, text: str, user_id: int) -> Dict[str, Any]:
        """텍스트 콘텐츠 처리"""
        start_time = time.time()
        
        try:
            # 텍스트 정제
            cleaned_text = self.content_extractor.clean_text(text)
            
            # URL이 포함된 텍스트인지 확인
            urls = self._extract_urls_from_text(text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="text",
                processing_method="direct",
                success=True,
                processing_time_ms=processing_time
            )
            
            return {
                "success": True,
                "content": cleaned_text,
                "metadata": {
                    "original_length": len(text),
                    "cleaned_length": len(cleaned_text),
                    "urls_found": urls,
                    "processing_time_ms": processing_time
                }
            }
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            
            # 오류 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="text",
                processing_method="direct",
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )
            
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def process_url_content(self, url: str, user_id: int) -> Dict[str, Any]:
        """URL 콘텐츠 처리"""
        start_time = time.time()
        
        try:
            # URL에서 콘텐츠 추출
            extracted_content = self.content_extractor.extract_from_url(url)
            
            if not extracted_content:
                raise Exception("Failed to extract content from URL")
            
            # 텍스트 정제
            cleaned_content = self.content_extractor.clean_text(extracted_content)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="url",
                processing_method="web_scraping",
                success=True,
                processing_time_ms=processing_time
            )
            
            return {
                "success": True,
                "content": cleaned_content,
                "metadata": {
                    "source_url": url,
                    "content_length": len(cleaned_content),
                    "processing_time_ms": processing_time,
                    "extraction_method": "web_scraping"
                }
            }
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            
            # 오류 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="url",
                processing_method="web_scraping",
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )
            
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def process_file_content(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """파일 콘텐츠 처리"""
        start_time = time.time()
        
        try:
            # 파일에서 콘텐츠 추출
            extracted_content = self.content_extractor.extract_from_file(file_path)
            
            if not extracted_content:
                raise Exception("Failed to extract content from file")
            
            # 텍스트 정제
            cleaned_content = self.content_extractor.clean_text(extracted_content)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="file",
                processing_method="file_extraction",
                success=True,
                processing_time_ms=processing_time
            )
            
            return {
                "success": True,
                "content": cleaned_content,
                "metadata": {
                    "source_file": file_path,
                    "content_length": len(cleaned_content),
                    "processing_time_ms": processing_time,
                    "extraction_method": "file_extraction"
                }
            }
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            
            # 오류 로그 기록
            self._log_processing(
                user_id=user_id,
                content_type="file",
                processing_method="file_extraction",
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )
            
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def process_clipboard_content(self, content: str, user_id: int) -> Dict[str, Any]:
        """클립보드 콘텐츠 통합 처리"""
        content_type = self.detect_content_type(content)
        
        if content_type == "url":
            return self.process_url_content(content, user_id)
        elif content_type == "file":
            return self.process_file_content(content, user_id)
        elif content_type == "text":
            return self.process_text_content(content, user_id)
        else:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}",
                "content": None
            }
    
    def get_supported_content_types(self) -> List[str]:
        """지원되는 콘텐츠 타입 목록 반환"""
        return ["text", "url", "file"]
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """텍스트에서 URL 추출"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    def _log_processing(
        self, 
        user_id: int, 
        content_type: str, 
        processing_method: str, 
        success: bool, 
        error_message: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ):
        """클립보드 처리 로그 기록"""
        try:
            log_entry = ClipboardProcessingLog(
                user_id=user_id,
                content_type=content_type,
                processing_method=processing_method,
                success=success,
                error_message=error_message,
                processing_time_ms=processing_time_ms
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            print(f"Failed to log clipboard processing: {e}")
            self.db.rollback()