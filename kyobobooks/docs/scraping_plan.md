## 교보문고 베스트셀러 데이터 수집 계획 (Scraping Plan)

이 문서는 교보문고 베스트셀러 데이터를 수집(Scraping)하기 위한 구체적인 구현 계획(Implementation Plan)입니다.

## Goal Description
교보문고의 특정 카테고리(예: IT/컴퓨터 카테고리 33 등) 베스트셀러 목록 데이터를 수집하여, 엑셀 등에서 손쉽게 확인할 수 있도록 로컬 파일(CSV)로 저장하는 스크립트를 작성합니다. API 엔드포인트를 직접 호출하여 데이터를 확보합니다.

## User Review Required
> [!IMPORTANT]
> - 스크립트 파일은 `kyobobooks/src/scraper.py` 경로에 작성될 예정입니다.
> - CSV에 저장할 컬럼은 **순위(bestrnk), 제목(cmdtName), 저자(chrcName), 출판사(pbcmName), 정가(price), 판매가(sapr)** 등으로 선정했습니다. 추가로 필요한 컬럼이 있다면 말씀해 주세요.

## Proposed Changes

### Data Collection Script
Python `requests` 라이브러리를 사용하여 API 데이터를 가져오고, `csv` 모듈을 활용하여 테이블 형태의 데이터로 기록합니다.

#### [NEW] kyobobooks/src/scraper.py
```python
import requests
import csv
import os
from pathlib import Path

def fetch_kyobo_best_sellers():
    # 제공된 교보문고 API URL
    url = "https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online?page=1&per=20&saleCmdtClstCode=33&soldOutExcludeYn=N&saleCmdtDsplDvsnCode=KOR&period=002&dsplDvsnCode=001&dsplTrgtDvsnCode=004"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print("교보문고 API에서 데이터를 가져오는 중...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    # 교보문고 API 응답 구조에 따라 상품 리스트 추출 (구조 확인 필요, 기본적으로 data['data']['bestSeller'] 등으로 가정)
    # 실제 응답 구조를 기반으로 key 이름은 유연하게 대처할 수 있도록 작성
    best_sellers = data.get("data", {}).get("bestSeller", []) 
    if not best_sellers:
        print("데이터를 찾을 수 없거나 API 응답 구조가 다릅니다.")
        return

    # 데이터를 저장할 폴더 확인 및 생성
    output_dir = Path("kyobobooks/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "best_sellers.csv"
    
    # 추출할 필드 정의
    headers_csv = ["순위", "도서명", "저자", "출판사", "정가", "판매가"]
    
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers_csv)
        
        for item in best_sellers:
            writer.writerow([
                item.get("bestrnk", ""),
                item.get("cmdtName", ""),
                item.get("chrcName", ""),
                item.get("pbcmName", ""),
                item.get("price", ""),
                item.get("sapr", "")
            ])
            
    print(f"데이터 수집 완료: {output_file} 파일에 저장되었습니다.")

if __name__ == "__main__":
    fetch_kyobo_best_sellers()
```

## Verification Plan

### Automated Tests
수동으로 스크립트를 실행하여 검증하는 것으로 대체합니다.

### Manual Verification
1. `uv run python kyobobooks/src/scraper.py` 명령을 실행합니다.
2. 터미널에 에러 없이 `데이터 수집 완료` 메시지가 출력되는지 확인합니다.
3. `kyobobooks/data/best_sellers.csv` 파일이 정상적으로 생성되었는지 확인합니다.
4. 엑셀이나 텍스트 에디터로 CSV 파일을 열었을 때, 한글이 깨지지 않고 표 형태로 정상 출력되는지 확인합니다. (utf-8-sig 인코딩 사용)
