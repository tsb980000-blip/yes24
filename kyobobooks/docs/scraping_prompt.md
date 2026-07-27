# 교보문고 데이터 수집 (Scraping) 계획

## 목적
교보문고 베스트셀러 데이터를 수집하여 CSV 형태로 저장합니다. (전체 페이지 데이터 수집)

## 대상 데이터 (Target API)
- 기본 URL: `https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online?page={page}&per=20&saleCmdtClstCode=33&soldOutExcludeYn=N&saleCmdtDsplDvsnCode=KOR&period=002&dsplDvsnCode=001&dsplTrgtDvsnCode=004`
- 설명: 교보문고 특정 카테고리(예: IT/컴퓨터 33)의 베스트셀러 목록을 반환하는 JSON API 엔드포인트입니다. `page` 파라미터를 변경하여 전체 데이터를 가져옵니다.

## 기술 스택
- **언어**: Python
- **라이브러리**: `requests`, `csv`, `time` (요청 간 딜레이용)
- 가상환경: 워크스페이스 루트의 공통 `.venv` 사용

## 데이터 저장 방식
- **포맷**: CSV (`.csv`)
- **경로**: `kyobobooks/data/` 디렉토리에 저장

## 주요 로직 (예상)
1. `page` 값을 1부터 시작하여 반복문(while)을 통해 타겟 API 엔드포인트 호출
2. 반환된 JSON 응답(Response) 파싱
3. 필요한 도서 정보(순위, 제목, 저자, 가격, 출판사 등) 리스트로 추출
4. 더 이상 데이터(상품 리스트)가 없거나 비어있으면 반복 종료
5. 전체 수집된 도서 데이터를 `csv` 모듈을 사용하여 `kyobobooks/data/best_sellers.csv` 파일에 한 번에 저장
