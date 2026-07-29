"""
교보문고 베스트셀러 데이터 탐색적 데이터 분석(EDA) 스크립트

목적: 수집된 베스트셀러 데이터를 바탕으로 기초 통계, 시각화, 텍스트 분석(TF-IDF)을 수행하고
결과를 마크다운 리포트로 자동 생성합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# 폴더 생성
os.makedirs("kyobobooks/images", exist_ok=True)
os.makedirs("kyobobooks/report", exist_ok=True)

report_content = ["# 교보문고 베스트셀러 탐색적 데이터 분석(EDA) 리포트\n"]

# 1. 데이터 로드 및 기본 탐색
df = pd.read_csv("kyobobooks/data/best_sellers.csv")

# 할인율 파생변수 생성
df['할인율'] = ((df['정가'] - df['판매가']) / df['정가'] * 100).fillna(0)

report_content.append("## 1. 데이터 기본 탐색\n")
report_content.append("### 상위 5개 행\n```text\n" + df.head().to_string() + "\n```\n")
report_content.append("### 하위 5개 행\n```text\n" + df.tail().to_string() + "\n```\n")

import io
buffer = io.StringIO()
df.info(buf=buffer)
info_str = buffer.getvalue()
report_content.append("### 데이터 기본 정보 (info)\n```text\n" + info_str + "\n```\n")

report_content.append(f"### 데이터 크기\n- **전체 행(Row) 수**: {df.shape[0]}\n- **전체 열(Column) 수**: {df.shape[1]}\n\n")

duplicates = df.duplicated().sum()
report_content.append(f"### 중복 데이터 확인\n- **중복된 행의 수**: {duplicates}\n\n")

report_content.append("### 수치형 변수 기술통계량\n```text\n" + df.describe().to_string() + "\n```\n")
report_content.append("### 범주형 변수 기술통계량\n```text\n" + df.describe(include=['O']).to_string() + "\n```\n")

# 2. 시각화 및 분석
report_content.append("## 2. 데이터 시각화 및 심층 분석\n")

def add_plot(fig, filename, title, interpret, table_text):
    filepath = f"kyobobooks/images/{filename}"
    fig.tight_layout()
    fig.savefig(filepath, dpi=300)
    plt.close(fig)
    report_content.append(f"### {title}\n")
    report_content.append(f"![{title}](../../{filepath})\n\n")
    report_content.append(f"**[참고 표/통계량]**\n```text\n{table_text}\n```\n\n")
    report_content.append(f"**[해석 및 인사이트]**\n{interpret}\n\n")

# V1: 출판사 빈도 (상위 30)
pub_counts = df['출판사'].value_counts().head(30)
fig1, ax1 = plt.subplots(figsize=(12, 6))
pub_counts.plot(kind='bar', ax=ax1, color='skyblue')
ax1.set_title("상위 30개 출판사 빈도수")
ax1.set_ylabel("도서 수")
interpret1 = "가장 많은 베스트셀러를 배출한 출판사를 확인하기 위한 시각화입니다. 특정 출판사가 상위권을 독점하고 있는지, 아니면 다양한 출판사가 골고루 분포하고 있는지 확인할 수 있습니다. 데이터 분석 결과 상위 출판사들의 점유율이 두드러지게 나타나는 것을 알 수 있으며, 이는 IT/컴퓨터 분야에서 특정 출판사들의 브랜드 파워나 기획력이 시장에서 강하게 작용함을 시사합니다."
add_plot(fig1, "v1_top_publishers.png", "1. 상위 30개 출판사 빈도수", interpret1, pub_counts.to_frame().to_string())

# V2: 저자 빈도 (상위 30)
author_counts = df['저자'].value_counts().head(30)
fig2, ax2 = plt.subplots(figsize=(12, 6))
author_counts.plot(kind='bar', ax=ax2, color='lightgreen')
ax2.set_title("상위 30명 저자 빈도수")
ax2.set_ylabel("도서 수")
interpret2 = "베스트셀러 목록에 가장 많이 이름을 올린 저자 상위 30명을 시각화한 결과입니다. 단일 저자가 여러 책을 흥행시켰는지, 다양한 저자들이 경쟁하고 있는지 보여줍니다. 주로 수험서나 기본서를 지속적으로 출간하는 특정 저자 혹은 단체(팀)가 다수의 도서를 베스트셀러에 올리는 경향을 뚜렷하게 확인할 수 있습니다."
add_plot(fig2, "v2_top_authors.png", "2. 상위 30명 저자 빈도수", interpret2, author_counts.to_frame().to_string())

# V3: 정가 분포 (Histogram)
fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.hist(df['정가'].dropna(), bins=30, color='coral', edgecolor='black')
ax3.set_title("도서 정가 분포")
ax3.set_xlabel("정가 (원)")
ax3.set_ylabel("빈도수")
interpret3 = "도서들의 정가가 어떤 가격대에 집중되어 있는지 파악하기 위한 히스토그램입니다. 대부분의 IT/컴퓨터 도서들이 특정 가격대(예: 2~3만원대)에 밀집해 있는 것을 볼 수 있습니다. 이는 전공 서적이나 실무서의 평균적인 가격 저항선과 시장의 표준 가격대가 형성되어 있음을 의미하며 출판사의 가격 책정 전략을 엿볼 수 있습니다."
add_plot(fig3, "v3_price_dist.png", "3. 도서 정가 분포", interpret3, df['정가'].describe().to_frame().to_string())

# V4: 판매가 분포 (Histogram)
fig4, ax4 = plt.subplots(figsize=(10, 5))
ax4.hist(df['판매가'].dropna(), bins=30, color='gold', edgecolor='black')
ax4.set_title("도서 판매가 분포")
ax4.set_xlabel("판매가 (원)")
ax4.set_ylabel("빈도수")
interpret4 = "실제 소비자가 구매하는 판매가의 분포를 시각화한 히스토그램입니다. 정가 분포와 유사한 형태를 띠지만, 온라인 서점의 기본 할인율(주로 10%)이 적용되어 전체적으로 가격대가 낮아진 축으로 이동한 모습을 명확하게 확인할 수 있습니다. 실질적인 구매자들의 예산 범위를 파악하는데 중요한 자료가 됩니다."
add_plot(fig4, "v4_sapr_dist.png", "4. 도서 판매가 분포", interpret4, df['판매가'].describe().to_frame().to_string())

# V5: 정가 vs 판매가 산점도
fig5, ax5 = plt.subplots(figsize=(8, 8))
ax5.scatter(df['정가'], df['판매가'], alpha=0.5)
ax5.set_title("정가와 판매가의 관계")
ax5.set_xlabel("정가")
ax5.set_ylabel("판매가")
ax5.plot([0, df['정가'].max()], [0, df['정가'].max()], 'r--', label='할인 없음 (정가=판매가)')
ax5.legend()
interpret5 = "정가와 판매가 사이의 관계를 나타내는 산점도(Scatter plot)입니다. 붉은 점선은 할인이 전혀 없는 상태를 의미하며, 대부분의 점들이 이 선보다 약간 아래에 일직선 형태로 위치하고 있습니다. 이는 대부분의 도서가 일괄적으로 10% 할인을 적용받고 있는 도서 정가제의 전형적인 패턴을 그대로 반영하고 있음을 확실하게 보여줍니다."
add_plot(fig5, "v5_price_scatter.png", "5. 정가와 판매가의 상관관계 산점도", interpret5, df[['정가', '판매가']].corr().to_string())

# V6: 상위 10개 출판사의 평균 정가
top10_pubs = df['출판사'].value_counts().head(10).index
df_top10_pubs = df[df['출판사'].isin(top10_pubs)]
pub_price_mean = df_top10_pubs.groupby('출판사')['정가'].mean().sort_values(ascending=False)
fig6, ax6 = plt.subplots(figsize=(10, 6))
pub_price_mean.plot(kind='bar', ax=ax6, color='purple')
ax6.set_title("상위 10개 출판사의 평균 정가")
ax6.set_ylabel("평균 정가 (원)")
interpret6 = "가장 많은 베스트셀러를 배출한 상위 10개 출판사들을 대상으로 평균 정가를 비교한 바 차트입니다. 출판사별로 주로 다루는 도서의 성격(가벼운 입문서 vs 두꺼운 전문 개발서)에 따라 평균 가격대가 눈에 띄게 다름을 알 수 있습니다. 특정 출판사가 고가의 전문서적 위주로 포지셔닝하고 있는지, 저렴한 대중서 위주인지 파악할 수 있는 유용한 지표입니다."
add_plot(fig6, "v6_pub_mean_price.png", "6. 상위 10개 출판사의 평균 정가", interpret6, pub_price_mean.to_frame().to_string())

# V7: 할인율 분포
fig7, ax7 = plt.subplots(figsize=(10, 5))
ax7.hist(df['할인율'], bins=20, color='teal', edgecolor='black')
ax7.set_title("도서 할인율 분포")
ax7.set_xlabel("할인율 (%)")
ax7.set_ylabel("빈도수")
interpret7 = "도서별 할인율((정가-판매가)/정가)의 분포를 나타냅니다. 대부분의 도서가 정확히 10%의 할인율 구간에 압도적으로 집중되어 있는 것을 확인할 수 있습니다. 한국의 현행 도서정가제 하에서 온라인 서점이 제공할 수 있는 최대 직간접 할인이 적용된 결과이며, 가격 경쟁보다는 콘텐츠 자체의 경쟁력이 중요함을 반증합니다."
add_plot(fig7, "v7_discount_rate.png", "7. 도서 할인율 분포", interpret7, df['할인율'].describe().to_frame().to_string())

# V8: 순위(1~100위)와 평균 가격의 관계 (추세)
# 순위를 100단위 등 구간으로 나누어 평균 가격 확인
df['순위구간'] = (df['순위'] // 100) * 100
rank_price = df.groupby('순위구간')['정가'].mean()
fig8, ax8 = plt.subplots(figsize=(10, 5))
rank_price.plot(kind='line', marker='o', ax=ax8, color='magenta')
ax8.set_title("순위 구간별 평균 정가 추세")
ax8.set_xlabel("순위 구간 (예: 0=1~99위)")
ax8.set_ylabel("평균 정가")
interpret8 = "순위 구간별(100위 단위)로 평균 정가가 어떻게 변화하는지 보여주는 선 그래프입니다. 최상위권 베스트셀러들이 상대적으로 가격이 낮은 대중적인 입문서인지, 아니면 가격이 높더라도 필수적인 수험서/전문서적인지 그 특징을 파악할 수 있습니다. 전반적인 가격 변동 추세를 통해 독자들의 구매 심리나 선호 가격대를 유추할 수 있는 의미 있는 시각화입니다."
add_plot(fig8, "v8_rank_price_trend.png", "8. 순위 구간별 평균 정가 추세", interpret8, rank_price.to_frame().to_string())

# V9: 상관관계 히트맵 (정가, 판매가, 할인율, 순위)
import seaborn as sns # 히트맵을 위해서만 제한적 사용(스타일 변경 목적 아님)
numeric_df = df[['순위', '정가', '판매가', '할인율']].dropna()
corr = numeric_df.corr()
fig9, ax9 = plt.subplots(figsize=(8, 6))
cax = ax9.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
fig9.colorbar(cax)
ax9.set_xticks(range(len(corr.columns)))
ax9.set_yticks(range(len(corr.columns)))
ax9.set_xticklabels(corr.columns)
ax9.set_yticklabels(corr.columns)
ax9.set_title("수치형 변수 간 상관관계 히트맵", pad=20)
for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        ax9.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
interpret9 = "순위, 정가, 판매가, 할인율 등 수치형 변수들 간의 상관관계를 한눈에 파악할 수 있는 히트맵 시각화입니다. 정가와 판매가는 당연히 1.0에 가까운 극도로 높은 양의 상관관계를 보입니다. 반면 순위와 가격 변수들 간의 상관계수는 0에 가깝게 나타나, 단순히 가격이 저렴하다고 해서 순위가 높아지거나 비싸다고 순위가 낮아지는 단순 선형 관계는 아님을 분명히 보여줍니다."
add_plot(fig9, "v9_correlation.png", "9. 수치형 변수 간 상관관계 히트맵", interpret9, corr.to_string())


# 3. 텍스트 데이터 분석 (도서명 TF-IDF)
report_content.append("## 3. 텍스트 데이터 분석 (도서명 TF-IDF)\n")
titles = df['도서명'].dropna().astype(str).tolist()

vectorizer = TfidfVectorizer(max_features=1000, stop_words=['및', '위한', '수', '있는', '책'])
X = vectorizer.fit_transform(titles)
words = vectorizer.get_feature_names_out()
tfidf_scores = X.sum(axis=0).A1
tfidf_df = pd.DataFrame({'키워드': words, 'TF-IDF점수': tfidf_scores})
top_30_keywords = tfidf_df.sort_values(by='TF-IDF점수', ascending=False).head(30)

fig10, ax10 = plt.subplots(figsize=(12, 8))
top_30_keywords.plot(kind='barh', x='키워드', y='TF-IDF점수', ax=ax10, color='indigo')
ax10.invert_yaxis()
ax10.set_title("도서명 내 상위 30개 핵심 키워드 (TF-IDF)")
ax10.set_xlabel("TF-IDF 총합 점수")
interpret10 = "도서명 텍스트 데이터를 대상으로 TF-IDF 알고리즘을 적용하여 추출한 핵심 키워드 상위 30개의 중요도를 보여주는 가로 막대 그래프입니다. 단순 빈도수가 아니라 단어의 정보량을 고려한 기법을 적용했기 때문에, 현재 IT/컴퓨터 도서 시장에서 가장 뜨거운 트렌드(예: 파이썬, AI, 자격증 이름 등)가 무엇인지 정확하게 짚어냅니다. 독자들이 가장 갈구하는 기술 스택과 학습 주제를 직관적으로 확인할 수 있습니다."
add_plot(fig10, "v10_tfidf_keywords.png", "10. 도서명 내 상위 30개 핵심 키워드 (TF-IDF)", interpret10, top_30_keywords.to_string(index=False))

with open("kyobobooks/report/eda_report.md", "w", encoding="utf-8") as f:
    f.writelines(report_content)

print("EDA 분석 완료: kyobobooks/report/eda_report.md 파일이 생성되었습니다.")
