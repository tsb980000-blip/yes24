"""
교보문고 베스트셀러 데이터 수집 스크립트 (scraper.py)

목적: 교보문고 특정 카테고리(예: IT/컴퓨터)의 베스트셀러 목록을 API를 통해 수집하고,
       이를 바탕으로 CSV 파일 형태로 저장하는 스크립트입니다.
       페이지(page)를 순회하며 전체 데이터를 수집합니다.
"""

import requests
import csv
import time
from pathlib import Path

def fetch_kyobo_best_sellers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_books = []
    page = 1
    
    print("교보문고 API에서 전체 데이터를 수집 시작...")
    
    while True:
        # page 파라미터를 동적으로 변경
        url = f"https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online?page={page}&per=20&saleCmdtClstCode=33&soldOutExcludeYn=N&saleCmdtDsplDvsnCode=KOR&period=002&dsplDvsnCode=001&dsplTrgtDvsnCode=004"
        
        print(f"{page}페이지 데이터를 가져오는 중...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # API 응답 구조에서 데이터 추출 
        best_sellers = data.get("data", {}).get("bestSeller", [])
        
        if not best_sellers:
            print("더 이상 데이터가 없습니다. 수집을 종료합니다.")
            break
            
        all_books.extend(best_sellers)
        
        # 다음 페이지를 위해 page 증가
        page += 1
        
        # 교보문고 서버에 무리를 주지 않기 위해 짧은 대기 시간 추가
        time.sleep(1)

    if not all_books:
        print("수집된 데이터가 없습니다.")
        return

    # 데이터를 저장할 폴더 확인 및 생성
    output_dir = Path("kyobobooks/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "best_sellers.csv"
    
    # 추출할 필드 정의 (순위, 제목, 저자, 출판사, 정가, 판매가)
    headers_csv = ["순위", "도서명", "저자", "출판사", "정가", "판매가"]
    
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers_csv)
        
        for item in all_books:
            rank = item.get("prstRnkn", "")
            prod_info = item.get("product", {}).get("productInfo", {})
            price_info = item.get("product", {}).get("priceInfo", {})
            
            writer.writerow([
                rank,
                prod_info.get("cmdtName", ""),
                prod_info.get("chrcName", ""),
                prod_info.get("pbcmName", ""),
                price_info.get("saleCmdtPrce", ""),
                price_info.get("saleCmdtSapr", "")
            ])
            
    print(f"총 {len(all_books)}개의 데이터 수집 완료: {output_file} 파일에 저장되었습니다.")

if __name__ == "__main__":
    fetch_kyobo_best_sellers()
