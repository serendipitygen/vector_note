import requests
from bs4 import BeautifulSoup
from typing import Optional
import PyPDF2
import docx
import io
import os
from pathlib import Path

class ContentExtractor:
    def extract_from_url(self, url: str) -> Optional[str]:
        """URL에서 텍스트 컨텐츠 추출"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 불필요한 요소 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # 본문 추출
            text = soup.get_text(separator='\n', strip=True)
            return text
        except Exception as e:
            print(f"Failed to extract content from URL: {e}")
            return None

    def extract_from_file(self, file_path: str) -> Optional[str]:
        """파일에서 텍스트 컨텐츠 추출"""
        try:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif ext == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            
            elif ext in ['.doc', '.docx']:
                doc = docx.Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            elif ext in ['.md', '.markdown']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            else:
                print(f"Unsupported file type: {ext}")
                return None
                
        except Exception as e:
            print(f"Failed to extract content from file: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """텍스트 정제"""
        if not text:
            return ""
            
        # 여러 줄 바꿈 제거
        text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        
        # 불필요한 공백 제거
        text = ' '.join(text.split())
        
        return text 