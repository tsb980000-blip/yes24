"""
YES24 베스트셀러 데이터를 분석하여 엑셀(xlsx) 대시보드로 생성하는 스크립트.

이 스크립트는 CSV 데이터를 읽어와 데이터 전처리를 수행하고,
주요 통계(출판사별 점유율, 저자별 점유율 등)를 계산한 후,
엑셀 파일에 시각화 차트를 포함한 대시보드를 생성합니다.
"""
import pandas as pd
import xlsxwriter
import numpy as np

def clean_number(x):
    if pd.isna(x):
        return 0
    if isinstance(x, (int, float)):
        return x
    return int(str(x).replace(',', '').replace('원', '').replace('판매지수 ', '').strip())

# 데이터 로드 및 전처리
df = pd.read_csv('../data/bestseller_day.csv', encoding='utf-8')
df['판매가'] = df['판매가'].apply(clean_number)
df['정가'] = df['정가'].apply(clean_number)
df['판매지수'] = df['판매지수'].apply(clean_number)

# 주요 집계 데이터 생성
# 1. 카테고리별 도서 수
category_counts = df['구분'].value_counts().reset_index()
category_counts.columns = ['구분', '도서 수']

# 2. 상위 10개 출판사
publisher_counts = df['출판사'].value_counts().head(10).reset_index()
publisher_counts.columns = ['출판사', '도서 수']

# 3. 상위 10명 저자
author_counts = df['저자'].value_counts().head(10).reset_index()
author_counts.columns = ['저자', '도서 수']

# 4. 상위 10개 도서 (판매지수 기준)
top_sales = df.sort_values('판매지수', ascending=False).head(10)[['도서명', '판매지수']]

# 엑셀 파일 생성
writer = pd.ExcelWriter('bestseller_dashboard.xlsx', engine='xlsxwriter')

# 1. Raw Data 시트 저장
df.to_excel(writer, sheet_name='Raw Data', index=False)

# 2. 통계 데이터 시트 저장 (차트를 그리기 위한 데이터)
category_counts.to_excel(writer, sheet_name='Stats', index=False, startrow=0, startcol=0)
publisher_counts.to_excel(writer, sheet_name='Stats', index=False, startrow=0, startcol=3)
author_counts.to_excel(writer, sheet_name='Stats', index=False, startrow=0, startcol=6)
top_sales.to_excel(writer, sheet_name='Stats', index=False, startrow=0, startcol=9)

workbook = writer.book
stats_sheet = writer.sheets['Stats']
dashboard_sheet = workbook.add_worksheet('Dashboard')

# 대시보드 꾸미기
header_format = workbook.add_format({'bold': True, 'font_size': 20, 'bg_color': '#1F497D', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter'})
dashboard_sheet.merge_range('B2:N4', 'YES24 당일 베스트셀러 EDA 대시보드', header_format)

# --- 차트 1: 카테고리 분포 (파이 차트) ---
chart1 = workbook.add_chart({'type': 'pie'})
chart1.add_series({
    'name': '카테고리 분포',
    'categories': ['Stats', 1, 0, len(category_counts), 0],
    'values': ['Stats', 1, 1, len(category_counts), 1],
    'data_labels': {'percentage': True}
})
chart1.set_title({'name': '구분별 도서 점유율'})
dashboard_sheet.insert_chart('B6', chart1)

# --- 차트 2: 상위 10 출판사 (막대 차트) ---
chart2 = workbook.add_chart({'type': 'bar'})
chart2.add_series({
    'name': '도서 수',
    'categories': ['Stats', 1, 3, len(publisher_counts), 3],
    'values': ['Stats', 1, 4, len(publisher_counts), 4],
})
chart2.set_title({'name': '상위 10개 출판사'})
chart2.set_y_axis({'reverse': True})
dashboard_sheet.insert_chart('I6', chart2)

# --- 차트 3: 상위 10 저자 (막대 차트) ---
chart3 = workbook.add_chart({'type': 'bar'})
chart3.add_series({
    'name': '도서 수',
    'categories': ['Stats', 1, 6, len(author_counts), 6],
    'values': ['Stats', 1, 7, len(author_counts), 7],
})
chart3.set_title({'name': '상위 10명 저자'})
chart3.set_y_axis({'reverse': True})
dashboard_sheet.insert_chart('B22', chart3)

# --- 차트 4: 판매지수 상위 10 도서 (컬럼 차트) ---
chart4 = workbook.add_chart({'type': 'column'})
chart4.add_series({
    'name': '판매지수',
    'categories': ['Stats', 1, 9, len(top_sales), 9],
    'values': ['Stats', 1, 10, len(top_sales), 10],
})
chart4.set_title({'name': '판매지수 TOP 10 도서'})
chart4.set_legend({'none': True})
dashboard_sheet.insert_chart('I22', chart4)

# 대시보드 시트 탭 색상 및 상태 설정
dashboard_sheet.set_tab_color('red')
dashboard_sheet.activate()

writer.close()
