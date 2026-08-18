# 정기 밸류에이션 업데이트 — 2026-08-18

- 총 47개 종목 중 26개 자동 반영, 21개 제외 (아래 참고)
- 배지-프로즈 불일치 발견: NVDA(2건), LLY(2건), JPM(1건), WMT(1건), AMD(2건), V(2건), XOM(1건), JNJ(1건), MA(1건), CSCO(2건), BAC(1건), AMAT(2건), HD(1건) — stock-refresh로 서술문 갱신 권장

## 자동 반영된 종목

| 티커 | PER | PBR | 목표가 괴리율 | 종합 | 프로즈 동기화 |
|---|---|---|---|---|---|
| NVDA | 45.95x (stage 2) | 34.78x (stage 5) | 34.5% | 2 낮음 | ⚠️ 2건 |
| LLY | 51.42x (stage 2) | 41.96x (stage 3) | 11.1% | 2 낮음 | ⚠️ 2건 |
| JPM | 18.12x (stage 5) | 2.7x (stage 5) | 3.2% | 4 높음 | ⚠️ 1건 |
| WMT | 42.22x (stage 5) | 9.23x (stage 5) | 19.7% | 3 적정 | ⚠️ 1건 |
| AMD | 194.11x (stage 5) | 13.31x (stage 5) | 19.1% | 3 적정 | ⚠️ 2건 |
| V | -x (stage -) | -x (stage -) | 14.3% | -  | ⚠️ 2건 |
| XOM | 23.9x (stage 5) | 2.57x (stage 5) | 5.3% | 4 높음 | ⚠️ 1건 |
| JNJ | 23.6x (stage 4) | 7.69x (stage 5) | 4.7% | 4 높음 | ⚠️ 1건 |
| MA | 34.46x (stage 2) | -x (stage -) | 16.9% | 2 낮음 | ⚠️ 1건 |
| INTC | -x (stage -) | 4.48x (stage 5) | 12.1% | 4 높음 | ✓ |
| ABBV | 105.7x (stage 5) | -x (stage -) | 10.8% | 4 높음 | ✓ |
| CSCO | 43.8x (stage 5) | 9.42x (stage 5) | 20.7% | 3 적정 | ⚠️ 2건 |
| BAC | 16.93x (stage 5) | 1.53x (stage 5) | 6.6% | 4 높음 | ⚠️ 1건 |
| AMAT | 58.57x (stage 5) | 19.7x (stage 5) | 26.4% | 3 적정 | ⚠️ 2건 |
| COST | 52.78x (stage 4) | 14.6x (stage 4) | 12.1% | 3 적정 | ✓ |
| CAT | 45.54x (stage 5) | 18.7x (stage 5) | 14.3% | 4 높음 | ✓ |
| UNH | 30.37x (stage 4) | 3.64x (stage 1) | 18.3% | 2 낮음 | ✓ |
| GE | 45.26x (stage 1) | 20.69x (stage 5) | 9.9% | 3 적정 | ✓ |
| KO | 28.85x (stage 4) | 11.73x (stage 4) | 8.0% | 3 적정 | ✓ |
| PG | 21.84x (stage 2) | 6.19x (stage 2) | 11.1% | 2 낮음 | ✓ |
| MS | 21.29x (stage 5) | 3.09x (stage 5) | 8.9% | 4 높음 | ✓ |
| HD | 23.81x (stage 3) | 26.34x (stage 1) | 10.4% | 2 낮음 | ⚠️ 1건 |
| MRK | 18.66x (stage 1) | 6.38x (stage 4) | 1.4% | 3 적정 | ✓ |
| PM | 26.22x (stage 5) | -x (stage -) | 7.0% | 4 높음 | ✓ |
| NFLX | 30.89x (stage 4) | 12.4x (stage 5) | 20.3% | 3 적정 | ✓ |
| RTX | 44.95x (stage 5) | 4.59x (stage 5) | 4.2% | 4 높음 | ✓ |

### 배지-프로즈 불일치 상세

- **NVDA**:
  - PER: val-item badge is ['45.95']x but prose says ['34.1']x (26% gap)
  - PBR: val-item badge is ['34.78']x but prose says ['27.7']x (20% gap)
- **LLY**:
  - PBR: val-item badge is ['41.96']x but prose says ['31.3']x (25% gap)
  - PER: val-item badge is ['51.42']x but prose says ['39.7']x (23% gap)
- **JPM**:
  - PER: val-item badge is ['18.12']x but prose says ['15.3', '16.4']x (16% gap)
- **WMT**:
  - PSR: val-item badge is ['1.2']x but prose says ['1.28']x (7% gap)
- **AMD**:
  - PER: val-item badge is ['194.11']x but prose says ['124.3']x (36% gap)
  - PBR: val-item badge is ['13.31']x but prose says ['11.7']x (12% gap)
- **V**:
  - PER: val-item badge is ['30.6']x but prose says ['10.6', '22.6']x (65% gap)
  - EV/EBITDA: val-item badge is ['22.7']x but prose says ['18.8', '24.2']x (17% gap)
- **XOM**:
  - PER: val-item badge is ['23.9']x but prose says ['15.0', '19.8', '20.6', '31.5']x (37% gap)
- **JNJ**:
  - PER: val-item badge is ['23.6']x but prose says ['29.3']x (24% gap)
- **MA**:
  - PER: val-item badge is ['34.46']x but prose says ['31.0']x (10% gap)
- **CSCO**:
  - PER: val-item badge is ['43.8']x but prose says ['40.2']x (8% gap)
  - PBR: val-item badge is ['9.42']x but prose says ['10.0']x (6% gap)
- **BAC**:
  - PER: val-item badge is ['16.93']x but prose says ['14.6']x (14% gap)
- **AMAT**:
  - PER: val-item badge is ['58.57']x but prose says ['50.7', '51']x (13% gap)
  - PBR: val-item badge is ['19.7']x but prose says ['17.9']x (9% gap)
- **HD**:
  - P/S: val-item badge is ['1.9']x but prose says ['2.0']x (5% gap)

## 제외된 종목 (수동 확인 필요)

- **AAPL** (validation_failed): FAIL: 목표가 밴드 current price $305.93 does not match valuation-tab current price $302.25 - run scripts/target_band_gauge.py
- **GOOGL** (validation_failed): FAIL: 목표가 밴드 current price $345.9 does not match valuation-tab current price $343.54 - run scripts/target_band_gauge.py
- **MSFT** (validation_failed): FAIL: 목표가 밴드 current price $495.4 does not match valuation-tab current price $492.43 - run scripts/target_band_gauge.py
- **AMZN** (validation_failed): FAIL: 목표가 밴드 current price $262.65 does not match valuation-tab current price $267.28 - run scripts/target_band_gauge.py
- **TSM** (fetch_financials_failed): error: TSM not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **AVGO** (validation_failed): FAIL: us section missing data-us-visual="chart|not-applicable" attribute (declaration was optional before - TSM shipped without one)
FAIL: 목표가 밴드 current price $392.99 does not match valuation-tab current price $416.05 - run scripts/target_band_gauge.py
FAIL: technical price-zone card must have exactly 5 PM rows
- **SPCX** (fetch_financials_failed): error: SPCX not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **META** (validation_failed): FAIL: 목표가 밴드 current price $589.85 does not match valuation-tab current price $578.85 - run scripts/target_band_gauge.py
- **TSLA** (validation_failed): FAIL: missing block: 다음 실적 체크포인트
FAIL: missing block: S&P 500 대비
FAIL: fund tab must end with core thesis then earnings checkpoints, matching NVDA/PM
FAIL: us section missing data-us-visual="chart|not-applicable" attribute (declaration was optional before - TSM shipped without one)
- **BRK.B** (validation_failed): FAIL: missing array: DAILY
FAIL: missing array: MA5
FAIL: missing array: MA20
FAIL: missing array: MA60
FAIL: missing array: MA120
- **MU** (validation_failed): FAIL: 목표가 밴드 current price $971.66 does not match valuation-tab current price $911.29 - run scripts/target_band_gauge.py
- **SKHY** (fetch_financials_failed): error: SKHY not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **ASML** (fetch_financials_failed): error: ASML not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **LRCX** (validation_failed): FAIL: 목표가 밴드 current price $332.36 does not match valuation-tab current price $326.11 - run scripts/target_band_gauge.py
- **RHHBY** (fetch_financials_failed): error: RHHBY not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **HSBC** (fetch_financials_failed): error: HSBC not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **ORCL** (validation_failed): FAIL: 목표가 밴드 current price $150.52 does not match valuation-tab current price $153.28 - run scripts/target_band_gauge.py
- **NVS** (fetch_financials_failed): error: NVS not found in /home/runner/work/stock-widgets/stock-widgets/data/sp500.json; pass --cik CIK (look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- **PLTR** (validation_failed): FAIL: 목표가 밴드 current price $174.04 does not match valuation-tab current price $172.01 - run scripts/target_band_gauge.py
- **CRM** (validation_failed): FAIL: 목표가 밴드 current price $196.21 does not match valuation-tab current price $193.32 - run scripts/target_band_gauge.py
- **ADBE** (validation_failed): FAIL: 목표가 밴드 current price $264.02 does not match valuation-tab current price $258.75 - run scripts/target_band_gauge.py

## 참고
- 이 파이프라인은 PER/PBR 배지와 목표가 밴드 마커만 자동 갱신합니다. Forward P/E, EV/EBITDA, PSR, 시나리오별 공정가치, 서술형 텍스트는 여전히 수작업입니다.
- PER/PBR이 바뀐 종목은 '종합 밸류에이션', '5개 분석 종합' 등 서술형 문단이 새 숫자와 어긋날 수 있으니, 변동폭이 큰 종목은 stock-refresh로 한 번 더 훑어보세요.
