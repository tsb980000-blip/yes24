# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 제미나이 API 키 설정
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

genai.configure(api_key=api_key)

# FastAPI 앱 생성
app = FastAPI()

# 제미나이 모델 초기화 (속도와 효율이 좋은 gemini-1.5-flash 사용)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    카카오톡 챗봇 스킬(Skill) 서버 엔드포인트
    """
    try:
        # 카카오톡 서버가 보낸 JSON 요청 본문 파싱
        payload = await request.json()
        
        # 사용자의 입력 메시지(발화) 추출
        user_utterance = payload.get("userRequest", {}).get("utterance", "").strip()
        print(f"사용자 입력: {user_utterance}")
        
        if not user_utterance:
            response_text = "질문을 이해하지 못했습니다. 다시 입력해 주세요."
        else:
            # 제미나이 API 호출하여 답변 생성
            response = model.generate_content(user_utterance)
            response_text = response.text.strip()
            
        print(f"제미나이 답변: {response_text}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        response_text = "죄송합니다, 답변을 생성하는 중에 오류가 발생했습니다."

    # 카카오톡 챗봇이 요구하는 JSON 규격에 맞게 응답 생성
    kakao_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
    
    return JSONResponse(content=kakao_response)

@app.get("/")
def read_root():
    return {"message": "카카오톡 챗봇 스킬 서버가 정상 동작 중입니다."}

if __name__ == "__main__":
    import uvicorn
    # 로컬 테스트 실행 (포트 8000)
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000, reload=True)
