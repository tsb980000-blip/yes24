# 카카오톡 제미나이 챗봇 스킬 서버

이 프로젝트는 카카오톡 챗봇(카카오 i 오픈빌더)의 요청을 받아 Google Gemini API와 연동하는 중계(스킬) 서버입니다.

## 폴더 구조
* `src/`: 챗봇 구동 소스 코드
* `docs/`: 프로젝트 관련 문서
* `data/`: 필요한 데이터 파일 저장소
* `images/`: 이미지 리소스 저장소

## 실행 방법
워크스페이스 루트(`D:\Project\yes24`)에서 아래 명령어를 실행하여 서버를 가동합니다.

```bash
.venv\Scripts\python.exe -m uvicorn kakaobot.src.chatbot:app --host 0.0.0.0 --port 8000 --reload
```

## 외부 노출 (ngrok 설정)
카카오톡 서버가 로컬 웹서버에 접근하도록 ngrok을 기동합니다.
```bash
ngrok http 8000
```
포워딩된 HTTPS 주소 뒤에 `/chat`을 붙여 카카오 i 오픈빌더 스킬 URL로 등록해 주세요.
* 예: `https://xxxx.ngrok-free.app/chat`
