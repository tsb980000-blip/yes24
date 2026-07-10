# -*- coding: utf-8 -*-
"""
YES24 당일 베스트셀러 도서 정보를 수집하는 스크래퍼 모듈입니다.

이 모듈은 YES24 베스트셀러 페이지에서 데이터를 HTML 형태로 받아와
BeautifulSoup을 사용해 파싱한 후, CSV 파일로 저장하는 기능을 제공합니다.
중복 데이터 감지 및 순위 역주행 감지 등의 예외 처리 로직이 포함되어 있습니다.
"""

import csv
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

def clean_text(text):
    """
    텍스트 데이터의 줄바꿈, 연속된 공백 등을 정형화하고 좌우 공백을 제거합니다.

    Args:
        text (str): 정제할 원본 텍스트

    Returns:
        str: 정제된 텍스트. text가 None이거나 빈 값일 경우 빈 문자열("") 반환
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_bestseller():
    """
    YES24 일별 베스트셀러 목록을 페이지 단위로 돌며 수집하고 CSV 파일로 저장합니다.

    수집 항목:
        순위, 상품번호, 구분, 도서명, 저자, 출판사, 출간일, 할인율, 판매가, 정가, 포인트, 판매지수, 평점, 배송정보

    특징:
        - 페이지 요청 간에 임의의 대기 시간(0.1 ~ 0.5초)을 두어 서버 부하를 최소화합니다.
        - 순위 역주행(이전 페이지의 최대 순위보다 현재 순위가 작아지는 현상) 발생 시 수집을 자동으로 종료합니다.
        - 동일한 상품 번호가 반복되어 나타나는 경우 중복 루프로 감지하고 수집을 종료합니다.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Referer": "https://www.yes24.com/product/category/daybestseller?categoryNumber=001&pageNumber=1&pageSize=24&type=day&saleDts="
    }
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "bestseller_day.csv")
    
    seen_goods = set()
    max_rank = 0
    
    print("새로운 데이터 수집을 시작합니다. 기존 파일을 초기화합니다.")
    write_mode = 'w'
        
    headers_csv = ["순위", "상품번호", "구분", "도서명", "저자", "출판사", "출간일", "할인율", "판매가", "정가", "포인트", "판매지수", "평점", "배송정보"]
    
    with open(csv_path, write_mode, encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers_csv)
        writer.writeheader()
            
        page = 1
        should_stop = False
        
        while not should_stop:
            # 0.1~0.5초 사이 랜덤 대기
            sleep_time = random.uniform(0.1, 0.5)
            print(f"대기 중... ({sleep_time:.3f}초)")
            time.sleep(sleep_time)
            
            url = f"https://www.yes24.com/product/category/BestSellerContents?categoryNumber=001&sumGb=06&sex=A&age=255&goodsTp=0&addOptionTp=0&excludeTp=2&pageNumber={page}&pageSize=24&goodsStatGb=06&eBookTp=0&bestType=DAY_BESTSELLER&type=day&saleYear=0&saleMonth=0&weekNo=0&saleDts=&viewMode=&freeYn="
            print(f"페이지 {page} 요청 중: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"페이지 {page} 가져오기 실패: HTTP 상태 코드 {response.status_code}")
                    break
            except Exception as e:
                print(f"요청 중 오류 발생: {e}")
                break
                
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            book_items = soup.find_all('li', attrs={'data-goods-no': True})
            if not book_items:
                print(f"페이지 {page}에서 도서 아이템을 찾을 수 없습니다. 수집을 종료합니다.")
                break
            
            # 현재 페이지 도서들의 상품 번호 추출
            page_goods = [item.get('data-goods-no', '').strip() for item in book_items]
            
            # 1. 모든 책이 이미 수집된 책인 경우 중복 루프 감지 종료
            if all(g in seen_goods for g in page_goods):
                print(f"페이지 {page}의 모든 데이터가 이미 수집된 데이터입니다. (중복 루프 감지) 수집을 종료합니다.")
                break
                
            data_list = []
            for item in book_items:
                goods_no = item.get('data-goods-no', '').strip()
                
                # 순위
                rank_elem = item.find('em', class_='rank')
                rank = clean_text(rank_elem.text) if rank_elem else ""
                
                # 순위값 정수 검증 및 역주행(wrap-around) 감지
                rank_val = None
                try:
                    rank_val = int(rank)
                except ValueError:
                    pass
                
                if rank_val is not None:
                    # 2. 순위가 이전의 최대 순위보다 작다면 페이지가 첫 페이지로 래핑된 것으로 판단하여 종료
                    if rank_val < max_rank:
                        print(f"순위 역주행 감지 (현재 순위: {rank_val}, 최대 순위: {max_rank}). 수집을 종료합니다.")
                        should_stop = True
                        break
                    max_rank = max(max_rank, rank_val)
                
                seen_goods.add(goods_no)
                
                # 도서명 및 구분
                info_name = item.find('div', class_='info_name')
                title = ""
                book_type = ""
                if info_name:
                    type_elem = info_name.find('span', class_='gd_res')
                    if type_elem:
                        book_type = clean_text(type_elem.text)
                    name_elem = info_name.find('a', class_='gd_name')
                    if name_elem:
                        title = clean_text(name_elem.text)
                
                # 출판 정보
                info_pub_grp = item.find('div', class_='info_pubGrp')
                author = ""
                publisher = ""
                pub_date = ""
                if info_pub_grp:
                    auth_elem = info_pub_grp.find('span', class_='info_auth')
                    if auth_elem:
                        author = clean_text(auth_elem.text)
                    pub_elem = info_pub_grp.find('span', class_='info_pub')
                    if pub_elem:
                        publisher = clean_text(pub_elem.text)
                    date_elem = info_pub_grp.find('span', class_='info_date')
                    if date_elem:
                        pub_date = clean_text(date_elem.text)
                        
                # 가격 정보
                info_price = item.find('div', class_='info_price')
                discount_rate = ""
                sale_price = ""
                original_price = ""
                point = ""
                if info_price:
                    disc_elem = info_price.find('span', class_='txt_sale')
                    if disc_elem:
                        discount_rate = clean_text(disc_elem.text)
                    sale_elem = info_price.find('strong', class_='txt_num')
                    if sale_elem:
                        sale_price = clean_text(sale_elem.text)
                    orig_elem = info_price.find('span', class_='txt_num dash')
                    if orig_elem:
                        original_price = clean_text(orig_elem.text)
                    point_elem = info_price.find('span', class_='yPoint')
                    if point_elem:
                        point = clean_text(point_elem.text)
                        
                # 판매지수 및 평점
                info_rating = item.find('div', class_='info_rating')
                sales_index = ""
                rating = ""
                if info_rating:
                    sales_elem = info_rating.find('span', class_='saleNum')
                    if sales_elem:
                        sales_index = clean_text(sales_elem.text)
                    rating_elem = info_rating.find('span', class_='rating_grade')
                    if rating_elem:
                        rating = clean_text(rating_elem.text)
                    elif 'notRating' not in info_rating.get('class', []):
                        yes_r = info_rating.find('span', class_='yes_r')
                        if yes_r:
                            rating = clean_text(yes_r.text)
                
                # 배송 정보
                info_deli = item.find('div', class_='info_deli')
                delivery_info = ""
                if info_deli:
                    delivery_info = clean_text(info_deli.text)
                    
                data_list.append({
                    "순위": rank,
                    "상품번호": goods_no,
                    "구분": book_type,
                    "도서명": title,
                    "저자": author,
                    "출판사": publisher,
                    "출간일": pub_date,
                    "할인율": discount_rate,
                    "판매가": sale_price,
                    "정가": original_price,
                    "포인트": point,
                    "판매지수": sales_index,
                    "평점": rating,
                    "배송정보": delivery_info
                })
            
            if data_list:
                writer.writerows(data_list)
                print(f"페이지 {page} 데이터를 파일에 기록했습니다. ({len(data_list)}개)")
            page += 1
            
    print(f"수집 완료. 총 {len(seen_goods)}개의 도서가 {os.path.abspath(csv_path)}에 저장되었습니다.")

if __name__ == "__main__":
    scrape_bestseller()
