from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import logging
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        try:
            # 한국어 특화 모델 로드
            self.model = SentenceTransformer('nlpai-lab/KURE-v1')
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.warning("EmbeddingService will be disabled.")
            self.model = None
            self.text_splitter = None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """텍스트 리스트를 임베딩 벡터로 변환"""
        if not self.model:
            logger.warning("Embedding model not available. Returning empty embeddings.")
            return [[0.0] * 768 for _ in texts]
        
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings

    def split_text(self, text: str) -> List[str]:
        """텍스트를 청크로 분할"""
        if not self.text_splitter:
            logger.warning("Text splitter not available. Performing basic split.")
            return [text[i:i + 500] for i in range(0, len(text), 500)]
        return self.text_splitter.split_text(text)

    def process_text(self, text: str) -> tuple[List[str], List[List[float]]]:
        """텍스트를 처리하여 청크와 임베딩 반환"""
        chunks = self.split_text(text)
        embeddings = self.get_embeddings(chunks)
        return chunks, embeddings 