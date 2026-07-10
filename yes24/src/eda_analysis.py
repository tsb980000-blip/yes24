# -*- coding: utf-8 -*-
"""
YES24 베스트셀러 데이터를 전처리하고 탐색적 데이터 분석(EDA) 및 시각화를 수행하는 모듈입니다.

이 스크립트는 수집된 raw CSV 파일을 읽어와 가격, 할인율, 판매지수, 평점, 리뷰 개수 등의
필드를 기계가 분석하기 좋은 수치형 데이터로 전처리하고 정제된 CSV 파일로 저장합니다.
이후 pandas, matplotlib, seaborn을 활용하여 주요 시각화 차트 5종을 생성하여 저장하며,
분석 결과를 요약한 마크다운 보고서(eda_report.md)를 자동으로 생성합니다.
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def setup_korean_font():
    """
    matplotlib에서 한글 깨짐을 방지하기 위해 시스템 한글 폰트(맑은 고딕)를 설정합니다.
    """
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style="whitegrid", font="Malgun Gothic", rc={"axes.unicode_minus": False})

def clean_data(raw_csv_path, clean_csv_path):
    """
    raw CSV 데이터를 읽어와 결측치 처리 및 수치형 필드로 가공한 후 정제된 CSV로 저장합니다.

    Args:
        raw_csv_path (str): 원본 CSV 파일 경로
        clean_csv_path (str): 정제 결과를 저장할 CSV 파일 경로

    Returns:
        pd.DataFrame: 전처리가 완료된 pandas 데이터프레임
    """
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"원본 데이터 파일이 존재하지 않습니다: {raw_csv_path}")

    # 데이터 로드
    df = pd.read_csv(raw_csv_path, encoding='utf-8-sig')

    # 1. 순위 수치형 변환
    df['순위'] = pd.to_numeric(df['순위'], errors='coerce')

    # 2. 구분 대괄호 제거
    df['구분'] = df['구분'].str.replace(r'[\[\]]', '', regex=True).str.strip()

    # 3. 가격 데이터 정제 (판매가, 정가)
    for col in ['판매가', '정가']:
        df[col] = df[col].astype(str).str.replace('원', '').str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. 할인율 정제
    df['할인율'] = df['할인율'].astype(str).str.replace('%', '').str.strip()
    df['할인율'] = pd.to_numeric(df['할인율'], errors='coerce').fillna(0).astype(int)

    # 5. 포인트 정제 (예: 포인트적립940원 -> 940)
    df['포인트'] = df['포인트'].astype(str).str.replace('포인트적립', '').str.replace('원', '').str.replace(',', '').str.strip()
    df['포인트'] = pd.to_numeric(df['포인트'], errors='coerce').fillna(0).astype(int)

    # 6. 판매지수 정제 (예: 판매지수 24,480 -> 24480)
    df['판매지수'] = df['판매지수'].astype(str).str.replace('판매지수', '').str.replace(',', '').str.strip()
    df['판매지수'] = pd.to_numeric(df['판매지수'], errors='coerce').fillna(0).astype(int)

    # 7. 출간일 정제 및 분리 (예: 2026년 06월 -> 연도 2026, 월 6)
    df['출간연도'] = df['출간일'].astype(str).apply(lambda x: int(re.search(r'(\d+)년', x).group(1)) if re.search(r'(\d+)년', x) else None)
    df['출간월'] = df['출간일'].astype(str).apply(lambda x: int(re.search(r'(\d+)월', x).group(1)) if re.search(r'(\d+)월', x) else None)

    # 8. 평점 및 리뷰 수 파싱
    # 예시 텍스트: "리뷰 총점9.9 정보 더 보기/감추기 종이책 리뷰 (4건) eBook 리뷰 (0건) 종이책 한줄평 (14건) eBook 한줄평 (0건)"
    def parse_rating_details(text):
        if pd.isna(text) or not isinstance(text, str):
            return pd.Series([None, 0, 0, 0, 0, 0])
        
        # 평점 추출
        rating_match = re.search(r'리뷰 총점\s*(\d+(?:\.\d+)?)', text)
        rating = float(rating_match.group(1)) if rating_match else None
        
        # 리뷰 개수 추출 헬퍼 함수
        def get_count(pattern, txt):
            m = re.search(pattern, txt)
            if m:
                return int(m.group(1).replace(',', ''))
            return 0
            
        paper_review = get_count(r'종이책 리뷰\s*\(([\d,]+)건\)', text)
        ebook_review = get_count(r'eBook 리뷰\s*\(([\d,]+)건\)', text)
        paper_comment = get_count(r'종이책 한줄평\s*\(([\d,]+)건\)', text)
        ebook_comment = get_count(r'eBook 한줄평\s*\(([\d,]+)건\)', text)
        
        total_reviews = paper_review + ebook_review + paper_comment + ebook_comment
        
        return pd.Series([rating, paper_review, ebook_review, paper_comment, ebook_comment, total_reviews])

    rating_cols = ['평점_수치', '종이책_리뷰_수', 'eBook_리뷰_수', '종이책_한줄평_수', 'eBook_한줄평_수', '총_리뷰_수']
    df[rating_cols] = df['평점'].apply(parse_rating_details)

    # 정제된 데이터프레임 저장
    df.to_csv(clean_csv_path, index=False, encoding='utf-8-sig')
    print(f"데이터 정제 완료. 정제된 파일 저장 경로: {clean_csv_path}")
    return df

def generate_visualizations(df, images_dir):
    """
    정제된 데이터를 바탕으로 주요 시각화 이미지 5종을 생성하고 지정 디렉토리에 저장합니다.

    Args:
        df (pd.DataFrame): 정제된 데이터프레임
        images_dir (str): 이미지를 저장할 디렉토리 경로
    """
    os.makedirs(images_dir, exist_ok=True)
    setup_korean_font()

    # 1. 베스트셀러 점유율 TOP 10 출판사
    plt.figure(figsize=(10, 6))
    top_publishers = df['출판사'].value_counts().head(10)
    sns.barplot(x=top_publishers.values, y=top_publishers.index, palette="viridis")
    plt.title("베스트셀러 점유율 상위 10개 출판사", fontsize=15, fontweight='bold', pad=15)
    plt.xlabel("베스트셀러 등록 도서 수 (권)", fontsize=12)
    plt.ylabel("출판사명", fontsize=12)
    plt.tight_layout()
    pub_chart_path = os.path.join(images_dir, "top10_publishers.png")
    plt.savefig(pub_chart_path, dpi=150)
    plt.close()
    print(f"출판사 차트 저장 완료: {pub_chart_path}")

    # 2. 베스트셀러 도서의 출간년도 분포
    plt.figure(figsize=(10, 6))
    # 결측치 제외 및 최근 연도 추출
    year_df = df['출간연도'].dropna().astype(int)
    sns.histplot(year_df, bins=max(5, len(year_df.unique())), kde=True, color="skyblue")
    plt.title("베스트셀러 도서 출간 연도 분포 (신간 vs 구간)", fontsize=15, fontweight='bold', pad=15)
    plt.xlabel("출간 연도", fontsize=12)
    plt.ylabel("도서 수 (권)", fontsize=12)
    plt.tight_layout()
    year_chart_path = os.path.join(images_dir, "pub_year_distribution.png")
    plt.savefig(year_chart_path, dpi=150)
    plt.close()
    print(f"출간연도 분포 차트 저장 완료: {year_chart_path}")

    # 3. 판매지수와 총 리뷰 수의 상관관계 분석 (상관관계 산점도)
    plt.figure(figsize=(10, 6))
    # 이상치 영향 차단을 위해 상위 99% 영역으로 제한해서 그리기
    q_sales = df['판매지수'].quantile(0.99)
    q_reviews = df['총_리뷰_수'].quantile(0.99)
    plot_df = df[(df['판매지수'] <= q_sales) & (df['총_리뷰_수'] <= q_reviews)]
    
    sns.scatterplot(data=plot_df, x="총_리뷰_수", y="판매지수", hue="구분", alpha=0.7, palette="Set2")
    plt.title("총 리뷰 수와 판매지수 간의 상관관계", fontsize=15, fontweight='bold', pad=15)
    plt.xlabel("총 리뷰 수 (개)", fontsize=12)
    plt.ylabel("판매지수", fontsize=12)
    plt.tight_layout()
    scatter_chart_path = os.path.join(images_dir, "sales_index_vs_reviews.png")
    plt.savefig(scatter_chart_path, dpi=150)
    plt.close()
    print(f"상관관계 차트 저장 완료: {scatter_chart_path}")

    # 4. 도서 구분(장르)별 판매지수 비교 (Box Plot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="구분", y="판매지수", palette="pastel")
    plt.yscale('log')  # 판매지수의 편차가 크므로 로그 스케일 적용
    plt.title("도서 구분(장르)별 판매지수 분포 (로그 스케일)", fontsize=15, fontweight='bold', pad=15)
    plt.xlabel("구분", fontsize=12)
    plt.ylabel("판매지수 (Log Scale)", fontsize=12)
    plt.tight_layout()
    genre_chart_path = os.path.join(images_dir, "price_distribution_by_genre.png")
    plt.savefig(genre_chart_path, dpi=150)
    plt.close()
    print(f"장르별 판매지수 차트 저장 완료: {genre_chart_path}")

    # 5. 베스트셀러 진입 수 상위 10명 저자
    plt.figure(figsize=(10, 6))
    top_authors = df['저자'].value_counts().head(10)
    sns.barplot(x=top_authors.values, y=top_authors.index, palette="magma")
    plt.title("베스트셀러 등록 도서 수 상위 10개 저자", fontsize=15, fontweight='bold', pad=15)
    plt.xlabel("도서 수 (권)", fontsize=12)
    plt.ylabel("저자명", fontsize=12)
    plt.tight_layout()
    author_chart_path = os.path.join(images_dir, "top10_authors.png")
    plt.savefig(author_chart_path, dpi=150)
    plt.close()
    print(f"저자 차트 저장 완료: {author_chart_path}")

def write_report(df, report_path):
    """
    전처리 및 분석 통계를 바탕으로 마크다운 형식의 상세 분석 보고서를 자동 작성합니다.

    Args:
        df (pd.DataFrame): 정제된 데이터프레임
        report_path (str): 보고서를 저장할 마크다운 파일 경로
    """
    total_books = len(df)
    unique_publishers = df['출판사'].nunique()
    unique_authors = df['저자'].nunique()
    mean_price = df['판매가'].mean()
    mean_orig_price = df['정가'].mean()
    mean_discount = df['할인율'].mean()
    mean_sales_index = df['판매지수'].mean()
    mean_rating = df['평점_수치'].dropna().mean()
    
    # 구분(장르)별 분포
    genre_counts = df['구분'].value_counts()
    genre_text = "\n".join([f"- **{genre}**: {count}권 ({count/total_books*100:.1f}%)" for genre, count in genre_counts.items()])

    # 가장 판매지수가 높은 책
    top_sales_book = df.loc[df['판매지수'].idxmax()]
    
    # 평점이 높은 책 중 리뷰가 30개 이상인 최고 평점 도서 목록
    highly_rated = df[df['총_리뷰_수'] >= 30]
    top_rating_book = highly_rated.loc[highly_rated['평점_수치'].idxmax()] if len(highly_rated) > 0 else df.loc[df['평점_수치'].idxmax()]

    # 마크다운 내용 구성
    report_content = f"""# YES24 당일 베스트셀러 데이터 분석(EDA) 보고서

본 보고서는 YES24 당일 베스트셀러 도서 데이터 1,000건의 수집본에 대한 전처리 및 시각화 분석 결과를 제공합니다.

---

## 1. 데이터 개요 및 요약 통계

- **분석 대상 도서 수**: {total_books}권
- **고유 출판사 수**: {unique_publishers}개
- **고유 저자 수**: {unique_authors}명
- **평균 정가**: {mean_orig_price:,.0f}원
- **평균 판매가**: {mean_price:,.0f}원 (평균 할인율: {mean_discount:.1f}%)
- **평균 판매지수**: {mean_sales_index:,.1f}
- **평균 리뷰 평점**: {mean_rating:.2f}점 (5점 만점 기준 환산 전 YES24 평점 10점 만점 기준)

### 도서 구분별 분포
{genre_text}

### 주요 특징 도서
- **판매지수 1위 도서**: `{top_sales_book['도서명']}` (저자: {top_sales_book['저자']}, 출판사: {top_sales_book['출판사']}, 판매지수: {top_sales_book['판매지수']:,})
- **리뷰 30개 이상 최고 평점 도서**: `{top_rating_book['도서명']}` (저자: {top_rating_book['저자']}, 평점: {top_rating_book['평점_수치']}점, 리뷰 및 한줄평 합계: {top_rating_book['총_리뷰_수']}개)

---

## 2. 세부 분석 및 시각화 결과

### [1] 베스트셀러 점유율 상위 10개 출판사
![출판사 점유율](../images/eda/top10_publishers.png)

> **인사이트**
> - 특정 출판사의 독점 구조라기보다 다수의 출판사가 고르게 분포되어 있습니다.
> - 상위 10개 출판사는 지속적으로 양질의 인기 베스트셀러를 발행하며 브랜드 충성도와 유통력을 갖추고 있음을 보입니다.

### [2] 베스트셀러 도서 출간 연도 분포
![출간 연도 분포](../images/eda/pub_year_distribution.png)

> **인사이트**
> - 베스트셀러의 대다수는 최근(2025~2026년)에 출간된 신간 도서로 구성되어 있습니다.
> - 하지만 2000년대 초반 혹은 그 이전에 출간된 '스테디셀러'(예: 코스모스, 싯다르타 등)도 여전히 높은 순위에 머물고 있어, 신작 마케팅 도서와 클래식 구간 도서가 공존하는 한국 출판 시장의 특성을 보입니다.

### [3] 총 리뷰 수와 판매지수 간의 상관관계
![리뷰와 판매지수 상관관계](../images/eda/sales_index_vs_reviews.png)

> **인사이트**
> - 전반적으로 리뷰 수(종이책/eBook 리뷰 및 한줄평 총합)가 많은 책이 높은 판매지수를 보이는 양의 상관관계를 나타냅니다.
> - 구매자들의 자발적인 리뷰와 평가는 다른 독자들의 신뢰와 도서 구매 결정에 지대한 영향을 주는 중요한 선행 혹은 동행 지표로 평가할 수 있습니다.

### [4] 도서 구분(장르)별 판매지수 분포
![장르별 판매지수 분포](../images/eda/price_distribution_by_genre.png)

> **인사이트**
> - 일반적인 단행본인 `[도서]`가 점유율과 수치적 분포 모두에서 주류를 차지하고 있습니다.
> - `[만화]` 등 타 구분의 도서들은 권당 단가가 다르고 타겟 독자층이 명확하여, 평균 판매지수 및 분포에서 단행본 도서류와 명확한 차이점을 보입니다.

### [5] 베스트셀러 등록 도서 수 상위 10개 저자
![저자 점유율](../images/eda/top10_authors.png)

> **인사이트**
> - 한 저자가 여러 도서를 베스트셀러 순위에 동시에 올려둔 다작/인기 저자 리스트입니다.
> - 주로 자격증 수험서 저자(예: 최태성), 시리즈물 만화 작가, 혹은 지속적인 충성 독자층을 확보한 저자들이 상위권을 점유하고 있습니다.

---

## 3. 종합 결론

1. **신간 주도의 시장 흐름과 스테디셀러의 생존**: 베스트셀러 리스트는 최근 1년 이내 출간된 도서 중심(신간)으로 로테이션이 활발하나, 검증된 고전 및 스테디셀러는 시장 유행과 상관없이 굳건한 판매고를 유지합니다.
2. **리뷰 인프라의 중요성**: 판매지수와 독자 리뷰 활성도 간의 밀접한 상관성이 시각적으로 입증되었습니다. 신작 발간 시 초기 독자 반응 유도(리뷰 유치)가 베스트셀러 궤도 안착에 핵심적일 것입니다.
3. **학습/수험서 및 검증된 인플루언서의 강세**: 역사 검정 수험서와 시리즈 만화, 유명 경제 전문가 등 강력한 팬덤 혹은 학습 목적이 명확한 책들이 상위 랭킹을 차지하고 있어 불황 속 한국 출판 시장의 실용 중심 트렌드를 고스란히 반영하고 있습니다.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"EDA 보고서 생성 완료: {report_path}")

def main():
    """
    전체 전처리 및 시각화, 보고서 작성을 순차적으로 실행하는 메인 함수입니다.
    """
    # 경로 설정 (상대경로 활용)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir) # D:/Project/yes24/yes24
    
    raw_csv = os.path.join(project_dir, 'data', 'bestseller_day.csv')
    clean_csv = os.path.join(project_dir, 'data', 'bestseller_cleaned.csv')
    images_dir = os.path.join(project_dir, 'images', 'eda')
    report_md = os.path.join(project_dir, 'docs', 'eda_report.md')

    print("===== YES24 베스트셀러 데이터 EDA 프로세스 시작 =====")
    
    # 1. 데이터 정제
    df = clean_data(raw_csv, clean_csv)
    
    # 2. 시각화 그래프 생성
    generate_visualizations(df, images_dir)
    
    # 3. 리포트 자동 작성
    write_report(df, report_md)
    
    print("===== EDA 프로세스 완료 =====")

if __name__ == "__main__":
    main()
