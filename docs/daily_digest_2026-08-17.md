# 정기 밸류에이션 업데이트 — 2026-08-17

- 총 47개 종목 중 28개 자동 반영, 19개 제외 (아래 참고)

## 자동 반영된 종목

| 티커 | PER | PBR | 목표가 괴리율 | 종합 |
|---|---|---|---|---|
| NVDA | 45.92x (stage 2) | 34.76x (stage 5) | 34.6% | 2 낮음 |
| GOOGL | 31.82x (stage 5) | 10.01x (stage 5) | 24.3% | 3 적정 |
| LLY | 51.64x (stage 2) | 42.13x (stage 3) | 10.6% | 2 낮음 |
| JPM | 18.03x (stage 5) | 2.69x (stage 5) | 3.8% | 4 높음 |
| WMT | 41.88x (stage 4) | 9.15x (stage 5) | 20.7% | 3 적정 |
| AMD | 190.94x (stage 5) | 13.1x (stage 5) | 21.1% | 3 적정 |
| V | -x (stage -) | 4.45x (stage 4) | 16.0% | 3 적정 |
| XOM | 24.11x (stage 5) | 2.59x (stage 5) | 4.3% | 4 높음 |
| JNJ | 23.79x (stage 4) | 7.75x (stage 5) | 3.9% | 4 높음 |
| MA | 34.04x (stage 2) | 8.03x (stage 3) | 18.3% | 2 낮음 |
| INTC | -x (stage -) | 4.52x (stage 5) | 11.0% | 4 높음 |
| ABBV | 106.12x (stage 5) | -x (stage -) | 10.3% | 4 높음 |
| CSCO | 44.27x (stage 5) | 9.53x (stage 5) | 19.4% | 3 적정 |
| BAC | 16.77x (stage 5) | 1.51x (stage 5) | 7.6% | 4 높음 |
| AMAT | 61.81x (stage 5) | 20.79x (stage 5) | 19.2% | 3 적정 |
| COST | 52.36x (stage 4) | 14.49x (stage 4) | 13.0% | 3 적정 |
| CAT | 46.87x (stage 5) | 19.24x (stage 5) | 11.1% | 4 높음 |
| UNH | 29.9x (stage 4) | 3.59x (stage 1) | 20.1% | 2 낮음 |
| GE | 45.38x (stage 1) | 20.75x (stage 5) | 9.6% | 3 적정 |
| KO | 28.61x (stage 4) | 11.63x (stage 4) | 8.9% | 3 적정 |
| PG | 21.62x (stage 2) | 6.13x (stage 2) | 12.2% | 2 낮음 |
| MS | 21.38x (stage 5) | 3.1x (stage 5) | 8.4% | 4 높음 |
| HD | 23.74x (stage 3) | 26.26x (stage 1) | 10.7% | 2 낮음 |
| MRK | 18.68x (stage 1) | 6.39x (stage 4) | 1.3% | 3 적정 |
| PM | 25.42x (stage 5) | -x (stage -) | 10.4% | 4 높음 |
| NFLX | 30.05x (stage 4) | 12.06x (stage 5) | 23.7% | 3 적정 |
| PLTR | 273.89x (stage 2) | 55.85x (stage 5) | 11.1% | 3 적정 |
| RTX | 44.69x (stage 5) | 4.56x (stage 5) | 4.8% | 4 높음 |

## 제외된 종목 (수동 확인 필요)

- **AAPL** (validation_failed): FAIL: 목표가 밴드 current price $305.59 does not match valuation-tab current price $302.25 - run scripts/target_band_gauge.py
- **MSFT** (validation_failed): FAIL: 목표가 밴드 current price $480.35 does not match valuation-tab current price $492.43 - run scripts/target_band_gauge.py
- **AMZN** (validation_failed): FAIL: 목표가 밴드 current price $261.31 does not match valuation-tab current price $267.28 - run scripts/target_band_gauge.py
- **TSM** (fetch_financials_failed): error: TSM not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **AVGO** (validation_failed): FAIL: us section missing data-us-visual="chart|not-applicable" attribute (declaration was optional before - TSM shipped without one)
FAIL: 목표가 밴드 current price $392.43 does not match valuation-tab current price $416.05 - run scripts/target_band_gauge.py
FAIL: technical price-zone card must have exactly 5 PM rows
- **SPCX** (fetch_financials_failed): error: SPCX not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **META** (validation_failed): FAIL: 목표가 밴드 current price $568.97 does not match valuation-tab current price $578.85 - run scripts/target_band_gauge.py
- **TSLA** (validation_failed): FAIL: missing block: 다음 실적 체크포인트
FAIL: missing block: S&P 500 대비
FAIL: fund tab must end with core thesis then earnings checkpoints, matching NVDA/PM
FAIL: us section missing data-us-visual="chart|not-applicable" attribute (declaration was optional before - TSM shipped without one)
- **BRK.B** (validation_failed): FAIL: missing array: DAILY
FAIL: missing array: MA5
FAIL: missing array: MA20
FAIL: missing array: MA60
FAIL: missing array: MA120
- **MU** (validation_failed): FAIL: 목표가 밴드 current price $1011.75 does not match valuation-tab current price $911.29 - run scripts/target_band_gauge.py
- **SKHY** (fetch_financials_failed): error: SKHY not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **ASML** (fetch_financials_failed): error: ASML not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **LRCX** (validation_failed): FAIL: 목표가 밴드 current price $343.84 does not match valuation-tab current price $326.11 - run scripts/target_band_gauge.py
- **RHHBY** (fetch_financials_failed): error: RHHBY not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **HSBC** (fetch_financials_failed): error: HSBC not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **ORCL** (validation_failed): FAIL: 목표가 밴드 current price $146.71 does not match valuation-tab current price $153.28 - run scripts/target_band_gauge.py
- **NVS** (fetch_financials_failed): error: NVS not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **CRM** (validation_failed): FAIL: 목표가 밴드 current price $190.97 does not match valuation-tab current price $193.32 - run scripts/target_band_gauge.py
- **ADBE** (validation_failed): FAIL: 목표가 밴드 current price $254.04 does not match valuation-tab current price $258.75 - run scripts/target_band_gauge.py

## 참고
- 이 파이프라인은 PER/PBR 배지와 목표가 밴드 마커만 자동 갱신합니다. Forward P/E, EV/EBITDA, PSR, 시나리오별 공정가치, 서술형 텍스트는 여전히 수작업입니다.
- PER/PBR이 바뀐 종목은 '종합 밸류에이션', '5개 분석 종합' 등 서술형 문단이 새 숫자와 어긋날 수 있으니, 변동폭이 큰 종목은 stock-refresh로 한 번 더 훑어보세요.
