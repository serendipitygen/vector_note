import os
import google.generativeai as genai
from typing import List, Dict

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_chat_response(self, history: List[Dict[str, str]], question: str, context: str):
        """
        채팅 기록과 컨텍스트를 기반으로 Gemini API로부터 스트리밍 응답을 생성합니다.
        """
        # Gemini API가 요구하는 형식으로 대화 기록 변환
        gemini_history = []
        for message in history:
            role = 'user' if message['role'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [message['content']]})

        # 시스템 프롬프트와 컨텍스트, 사용자 질문을 결합
        prompt = f"""당신은 노트 내용을 기반으로 질문에 답변하는 AI 어시스턴트입니다.
        주어진 컨텍스트 정보를 최대한 활용하여 사용자의 질문에 답변하세요.
        답변은 항상 한국어로 작성해주세요.

        ---
        컨텍스트 정보:
        {context}
        ---

        사용자 질문:
        {question}
        """

        try:
            # 최종 프롬프트를 대화 기록에 추가
            gemini_history.append({'role': 'user', 'parts': [prompt]})
            
            # 전체 대화 기록을 API에 전달하여 응답 생성
            response_stream = self.model.generate_content(
                gemini_history,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=2048,
                    temperature=0.7,
                ),
                stream=True
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"Gemini API 호출 중 오류 발생: {e}")
            yield "죄송합니다, 답변을 생성하는 중에 오류가 발생했습니다." 