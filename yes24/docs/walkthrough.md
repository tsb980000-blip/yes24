# YES24 당일 베스트셀러 EDA 작업 완료 보고서

수집된 YES24 베스트셀러 1,000건의 데이터를 전처리하고 탐색적 데이터 분석(EDA)을 진행하여 시각화 차트 5종 및 종합 분석 보고서 작성을 완료했습니다.

---

## 1. 생성 및 변경된 파일 목록

- **데이터 정제 & EDA 통합 스크립트**:
  - [eda_analysis.py](file:///D:/Project/yes24/yes24/src/eda_analysis.py) [NEW]
    - 정가, 판매가, 할인율, 판매지수 수치형 변환
    - 평점 데이터 파싱을 통한 평점 및 리뷰 개수 세부 추출
    - 시각화 이미지 5종 자동 저장 및 마크다운 보고서 자동 작성 로직 탑재
- **정제된 데이터셋**:
  - [bestseller_cleaned.csv](file:///D:/Project/yes24/yes24/data/bestseller_cleaned.csv) [NEW]
- **시각화 이미지 5종**:
  - [images/eda/](file:///D:/Project/yes24/yes24/images/eda/) [NEW]
    - [top10_publishers.png](file:///D:/Project/yes24/yes24/images/eda/top10_publishers.png) (베스트셀러 점유율 상위 10개 출판사)
    - [pub_year_distribution.png](file:///D:/Project/yes24/yes24/images/eda/pub_year_distribution.png) (도서 출간 연도 분포)
    - [sales_index_vs_reviews.png](file:///D:/Project/yes24/yes24/images/eda/총 리뷰 수와 판매지수의 상관관계)
    - [price_distribution_by_genre.png](file:///D:/Project/yes24/yes24/images/eda/price_distribution_by_genre.png) (도서 구분별 판매지수 로그스케일 박스플롯)
    - [top10_authors.png](file:///D:/Project/yes24/yes24/images/eda/top10_authors.png) (베스트셀러 등록 도서 수 상위 10개 저자)
- **종합 보고서 및 작업 관리**:
  - [eda_report.md](file:///D:/Project/yes24/yes24/docs/eda_report.md) [NEW] (EDA 시각화 결과 및 종합 분석 서술)
  - [task.md](file:///D:/Project/yes24/yes24/docs/task.md) [MODIFY] (모든 작업 태스크 완료 업데이트)

---

## 2. 작업 검증 및 실행 결과

1. **가상환경 의존성**:
   - `pandas`, `matplotlib`, `seaborn`이 가상환경에 성공적으로 설치되었습니다.
2. **분석 스크립트 실행 완료**:
   - `uv run python yes24/src/eda_analysis.py` 명령어가 정상 실행되어 데이터 전처리 및 시각화 프로세스가 한글 폰트 깨짐 없이 정상 완료되었습니다.
3. **종합 보고서**:
   - 데이터 기반의 분석 수치 및 5가지 테마별 시각화가 결합된 마크다운 보고서가 [eda_report.md](file:///D:/Project/yes24/yes24/docs/eda_report.md)에 성공적으로 구성되었습니다.
