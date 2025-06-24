from typing import List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.services.milvus_service import search_similar

class ChatService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = None
        self.history = []

    def start_chat(self):
        """새로운 채팅 세션 시작"""
        self.chat = self.model.start_chat(history=[])
        self.history = []

    def get_relevant_context(self, query: str, collection_name: str) -> str:
        """쿼리와 관련된 문서 컨텍스트 검색"""
        # 쿼리를 벡터로 변환하는 로직 필요
        query_vector = self._get_embedding(query)
        similar_docs = search_similar(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=3
        )
        context = "\n".join([doc["content"] for doc in similar_docs])
        return context

    async def get_response(self, query: str, collection_name: str) -> dict:
        """사용자 쿼리에 대한 응답 생성"""
        if not self.chat:
            self.start_chat()

        # 관련 문서 검색
        context = self.get_relevant_context(query, collection_name)
        # 프롬프트 구성
        prompt = f"""다음 문서 내용을 기반으로 질문에 답변해주세요:\n\n문서 내용:\n{context}\n\n질문: {query}\n\n가능한 한 문서의 내용을 기반으로 답변해주시고, 문서에 없는 내용은 명시적으로 표시해주세요."""
        # 응답 생성
        response = await self.chat.send_message_async(prompt)
        # 대화 기록 저장
        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": response.text})
        return {
            "response": response.text,
            "context": context
        }

    def _get_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환
        실제 구현에서는 적절한 임베딩 모델 사용 필요
        """
        # TODO: 실제 임베딩 모델 구현
        pass 