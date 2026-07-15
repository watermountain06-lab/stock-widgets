# stock-widgets

미국 시가총액 상위 종목 인터랙티브 분석 위젯. GitHub Pages로 배포.

## 구조

```
index.html          갤러리 페이지 (검색 + 섹터 필터)
widgets/             종목별 완성 위젯 (독립 HTML)
data/manifest.json   갤러리에 표시되는 종목 메타데이터
data/sp500.json       S&P500 종목 목록 캐시 (ticker/name/sector/CIK)
templates/            index.html 생성용 템플릿
scripts/              데이터 수집 및 publish 자동화 스크립트
```

## 위젯 추가하기

1. 재무제표 + 주가 데이터 수집 (선택, 위젯 작성 시 참고용)
   ```
   python3 scripts/fetch_financials.py TICKER --sp500 data/sp500.json
   python3 scripts/fetch_price.py TICKER
   ```
2. 위젯 HTML을 완성한 뒤 publish
   ```
   python3 scripts/publish_widget.py . path/to/widget.html \
     --rank 11 --ticker BRK.B --name "Berkshire Hathaway" \
     --sector Financials --accent "#c8a84b"
   ```
   `publish_widget.py`가 자동으로: 위젯을 `widgets/`에 복사 → `data/manifest.json` 갱신 →
   `index.html` 재생성 → git pull/commit/push까지 처리한다. 원격에 새 커밋이 있으면 병합 후
   재시도하며, 강제 push는 하지 않는다.

## 데이터 출처

- 재무제표: [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation) (공식, 무료)
- 주가: Yahoo Finance chart API (비공식, 무료)
- S&P500 구성종목: [datasets/s-and-p-500-companies](https://github.com/datasets/s-and-p-500-companies)

⚠ 투자 권고가 아닙니다.
