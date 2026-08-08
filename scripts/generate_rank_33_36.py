#!/usr/bin/env python3
"""Generate ranks 33-36 from the current canonical widget structure."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "widgets/UNH_analysis_widget.html").read_text()
STYLE = re.search(r"<style>(.*?)</style>", TEMPLATE, re.S).group(1)
STANDARD_ACCENT2 = "#38bdf8"
STANDARD_ACCENT3 = "#4a0e1c"

COMPANIES = [
    dict(rank=33, ticker="GE", yahoo="GE", name="GE Aerospace", sector="Industrials",
         color="#38bdf8", accent="#075985",
         exchange="NYSE", subtitle="상업·방산 항공기 엔진과 고마진 애프터마켓 서비스의 글로벌 선도기업",
         marketcap="$371.5B", pe="52.4x", eps="$6.83", dividend="$0.36",
         next_date="2026년 10월 중순", quote_name="H. Lawrence Culp Jr.",
         quote="상업 서비스의 견조한 성장이 매출과 EPS의 20% 이상 성장을 이끌었다",
         quote_source="https://www.geaerospace.com/news/investor-relations/ir-updates/ge-aerospace-releases-its-2q26-results",
         thesis="상업 엔진의 방대한 설치 기반은 장기 서비스 계약과 부품 수요를 반복매출로 전환하고, LEAP 설치 기반이 2025~2030년 두 배 이상 늘어날 전망은 다음 서비스 사이클을 키운다. 다만 Forward PER 39.8x와 EV/EBITDA 31.5x는 이 성장의 상당 부분을 이미 반영하므로, 공급망 병목으로 엔진 납품·마진이 흔들리면 멀티플 압축 위험이 크다.",
         valuation_title="고평가 3개·매우 고평가 2개 — 서비스 성장 기대를 대부분 반영",
         valuation_text="Forward PER·FCF Yield·PEG가 4단계, P/S·EV/EBITDA가 5단계다. 적정 이하 지표가 하나도 없는 것은 데이터 누락이 아니라, 항공 애프터마켓의 희소성과 이익 성장 기대가 모든 가격 지표에 반영된 결과다.",
         position="NYSE 상장 미국 순수 항공우주 기업으로, 상업·방산 엔진과 글로벌 애프터마켓 서비스에 직접 투자하는 대형주다. 미국 제조 투자와 국방 예산의 수혜를 받는 동시에 Boeing·Airbus 생산 및 전 세계 항공 운항 사이클에 노출된다.",
         checkpoints="① Commercial Engines & Services의 유기매출과 서비스 이익률 ② LEAP 납품 증가율 및 부품 투입 개선 ③ 2026 조정 EPS $7.65~7.85·FCF 가이던스 달성 경로 ④ 공급망 병목과 고유가가 항공사 정비 수요에 미치는 영향",
         pills=["Q2 매출 +21%","Q2 조정 EPS +22%","2026 EPS 가이던스 $7.65~7.85"],
         synthesis_fund="서비스 매출·EPS 20%대 성장", synthesis_val="4~5단계만 존재", opinion="성장 최고 수준, 안전마진은 낮음",
         ps_sub=["TTM GAAP · 2026.07","최근 분기 장부가 기준","2026 FCF 가이던스/주식수","연환산 · $0.36×4"],
         qlabels=["Q3'24","Q4'24","Q1'25","Q2'25","Q3'25","Q4'25","Q1'26","Q2'26"],
         revenue=[9.84,10.81,9.94,10.15,11.31,12.74,11.90,13.35],
         profit=[1.85,1.89,1.49,1.90,2.08,2.42,2.10,2.54],
         qeps=[1.15,1.32,1.49,1.66,1.66,1.57,1.82,2.30],
         peers=[["GE",52.4],["RTX",35.2],["RR.L",31.0],["SAF.PA",34.5]],
         vals=[("Forward PER","39.8x",4,"높음","저 22x","적정 30x","고 45x","서비스 성장 프리미엄 반영"),
               ("P/S","6.8x",5,"매우높음","저 2x","적정 4x","고 6x","산업재 평균 대비 높은 매출 배수"),
               ("EV/EBITDA","31.5x",5,"매우높음","저 14x","적정 22x","고 30x","항공 애프터마켓 희소성 반영"),
               ("FCF Yield","1.9%",4,"높음","저 5%","적정 3%","고 2%","현 주가의 현금흐름 수익률은 낮음"),
               ("PEG","2.1x",4,"높음","저 1x","적정 1.5x","고 2.5x","성장률 대비 프리미엄")],
         ps=["$6.83","$16.90","$6.95","$1.44"],
         scenarios=[["Bear","$285–320","공급망 병목과 마진 압박"],["Base","$345–390","서비스 성장과 가이던스 달성"],["Bull","$410–455","LEAP 램프와 FCF 상향"]],
         target=390, bull=455, bear=285,
         drivers=[("서비스 믹스","상업 엔진 설치기반 확대<br>장기 서비스 계약의 반복매출"),
                  ("LEAP 램프","항공기 생산 정상화<br>향후 서비스 풀 확대"),
                  ("방산 수요","국방 예산과 교체 수요<br>대형 수주잔고 가시성")],
         risks=["공급망 병목이 납품과 마진을 제한","높은 밸류에이션은 실적 미스에 민감"],
         news=[("2026.07.16","Q2 실적과 연간 가이던스 상향","항공사 애프터마켓 지출이 견조해 GE는 2026 이익 전망을 높였다.","https://www.sahmcapital.com/news/content/update-2-ge-aerospace-lifts-2026-forecast-as-airlines-keep-up-maintenance-spending-2026-07-16","Reuters·Sahm","green"),
               ("2026.06.16","BofA, 장기 성장 엔진 평가","BofA는 견조한 수요와 실행력을 근거로 2026 두 자릿수 성장을 전망했다.","https://www.kiplinger.com/investing/analysts-top-sandp-500-stocks-to-buy-now","Kiplinger","green"),
               ("2026.03.09","미국 공장에 $1B 투자","$200B 수주잔고 대응을 위해 미국 공장 투자와 5,000명 채용을 발표했다.","https://www.axios.com/local/raleigh/2026/03/09/ge-aerospace-will-invest-more-than-160m-across-north-carolina","Axios",""),
               ("2026.04.21","Q1 주문 87% 증가","Q1 조정 EPS가 예상치를 웃돌았지만 고유가·성장 둔화를 위험으로 제시했다.","https://qz.com/ge-aerospace-q1-2026-earnings-profit-outlook-oil-prices-042126","Quartz","green"),
               ("2026.01.22","엔진 가격·공급망 긴장","항공사 불만 속에서 LEAP 내구성 개선과 정비 수요의 가격 결정력이 동시에 부각됐다.","https://www.postandcourier.com/ge-aerospace-ceo-pushes-back-as-airlines-decry-engine-pricing-power/article_b71b819b-46c0-4cc6-970a-9744af4fd8c2.html","Reuters·Post and Courier","neutral")]),
    dict(rank=34, ticker="HSBC", yahoo="HSBC", name="HSBC Holdings plc", sector="Financials",
         color="#ef4444", accent="#991b1b",
         exchange="NYSE ADR", subtitle="아시아 중심 글로벌 은행·자산관리·기업금융 프랜차이즈",
         marketcap="$354.2B", pe="13.4x", eps="$7.70", dividend="$3.40",
         next_date="2026년 7월 29일", quote_name="Georges Elhedery",
         quote="네 개 사업부 모두 전사 매출 성장에 기여했고, 특이항목 제외 연환산 RoTE가 각각 17%를 웃돌았다",
         quote_source="https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2026/1q/pdfs/hsbc-holdings-plc/260505-1q-2026-earnings-release.pdf",
         thesis="아시아·중동 웰스 잔액 $1.6T와 네 사업부 모두 17%를 웃돈 연환산 RoTE가 수수료 성장과 자본환원의 기반이다. Forward PER 11.8x는 글로벌 은행 대비 과하지 않지만 P/TBV 1.8x는 이미 높은 수익성을 반영한다. 금리 하락에 따른 banking NII 둔화와 홍콩 상업용 부동산 신용비용이 핵심 하방 변수다.",
         valuation_title="적정 3개·고평가 1개, ROTCE 최우수 — 수익성 프리미엄은 일부 반영",
         valuation_text="Forward PER·배당수익률·TTM P/E는 3단계, P/TBV는 4단계이며 ROTCE 17%+는 수익성 기준 1단계 최우수다. 2·5단계가 비어 있는 것은 누락이 아니라, 가격은 대체로 적정권이되 유형자본 프리미엄만 높은 현재 분포를 뜻한다.",
         position="런던 본사의 영국 은행이며 보통주는 London·Hong Kong에 상장된다. 미국 투자자는 NYSE의 HSBC ADR로 접근하며, 이 ADR은 미국 기업 지분이 아니라 아시아 중심 글로벌 은행의 예탁증서다.",
         checkpoints="① banking NII의 연간 가이던스와 금리 민감도 ② 특이항목 제외 RoTE 17%+ 유지 여부 ③ Wealth fee·기타 수수료 성장과 $1.6T 웰스 잔액 ④ 홍콩 상업용 부동산 ECL 및 Hang Seng 민영화의 CET1 영향",
         pills=["4개 사업부 RoTE 17%+","2025 웰스 잔액 $1.6T","20개 신규 Wealth Centre"],
         synthesis_fund="RoTE 17%+·웰스 수수료 성장", synthesis_val="가격 적정, P/TBV만 높음", opinion="수익성 우수, 부동산 ECL 확인 필요",
         ps_sub=["ADR 환산 TTM · 2026.07","최근 공시 TBV 환산","최근 12개월 추정치","ADR 연간 지급액 기준"],
         qlabels=["Q2'24","Q3'24","Q4'24","Q1'25","Q2'25","Q3'25","Q4'25","Q1'26"],
         revenue=[16.54,17.00,15.87,17.65,16.80,17.23,16.40,17.96],
         profit=[6.40,6.48,1.97,6.70,5.11,5.48,3.02,5.80],
         qeps=[1.71,1.75,0.55,1.82,1.39,1.51,0.84,1.61],
         peers=[["HSBC",13.4],["JPM",18.0],["BAC",16.2],["C",14.1]],
         vals=[("Forward PER","11.8x",3,"적정","저 8x","적정 12x","고 16x","글로벌 은행 대비 중간 수준"),
               ("P/TBV","1.8x",4,"높음","저 0.9x","적정 1.3x","고 1.8x","높은 RoTE를 선반영"),
               ("배당수익률","3.3%",3,"적정","저 2%","적정 4%","고 6%","특별배당 제외 보통 수준"),
               ("ROTCE","17%+",1,"최우수","저 8%","적정 13%","고 17%","회사가 제시한 2026 목표"),
               ("P/E TTM","13.4x",3,"적정","저 9x","적정 13x","고 18x","수익 정상화 기준 적정")],
         ps=["$7.70","$57.20","$8.10","$3.40"],
         scenarios=[["Bear","$78–88","금리 하락과 신용비용 상승"],["Base","$94–108","RoTE 17%와 자본환원 유지"],["Bull","$115–128","아시아 자산관리 가속"]],
         target=108, bull=128, bear=78,
         drivers=[("아시아 부의 성장","홍콩·싱가포르 웰스 허브<br>수수료 기반 수익 확대"),
                  ("자본 환원","강한 CET1과 배당<br>자사주 매입 여력"),
                  ("단순화","비핵심 지역 축소<br>그룹 비용 효율 개선")],
         risks=["금리 하락은 은행 NII를 압박","중국·홍콩 부동산 신용위험"],
         news=[("2026.07.10","홍콩 디지털 구조화상품 발행","블록체인 기반 증권 인프라를 활용한 디지털 네이티브 발행을 완료했다.","https://www.marketnode.com/news/hsbc-completes-first-digitally-native-structured-product-issuance-in-hong-kong","Marketnode",""),
               ("2026.05.05","Q1 네 사업부 RoTE 17% 상회","세전이익 $9.4B, 웰스 수수료와 banking NII 증가가 신용비용 상승을 상쇄했다.","https://www.sec.gov/Archives/edgar/data/1089113/000108911326000016/livedocq12026earningsrelea.htm","SEC 6-K","green"),
               ("2026.02.27","싱가포르 최대 Wealth Centre 개장","싱가포르에서 2024년 이후 네 번째 웰스 센터를 열었다.","https://www.about.hsbc.com.sg/news-and-media/hsbc-singapore-unveils-its-largest-wealth-centre","HSBC Singapore","green"),
               ("2026.02.25","2025 웰스 잔액 $1.6T 공개","아시아·중동 중심으로 20개 Wealth Centre를 추가했다고 연차보고서에서 밝혔다.","https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2025/annual/pdfs/hsbc-holdings-plc/sea-260225-annual-report-and-accounts-2025-hk.pdf","HSBC Annual Report","green"),
               ("2026.01.08","Asia-for-Asia 기업금융 확대","싱가포르에서 혁신기업·VC·고액자산가를 연결하는 지역 전략을 강화했다.","https://www.business.hsbc.com.sg/en-sg/insights/growing-my-business/hsbc-steps-up-asia-for-asia-strategy-with-its-corporate-and-institutional-banking-business-in-sg","HSBC Business","neutral")]),
    dict(rank=35, ticker="RHHBY", yahoo="RHHBY", name="Roche Holding AG", sector="Health Care",
         color="#38bdf8", accent="#1d4ed8",
         exchange="OTCQX ADR", subtitle="제약과 진단을 결합한 스위스 정밀의학·종양학 선도기업",
         marketcap="$353.6B", pe="25.6x", eps="$1.73", dividend="$0.86",
         next_date="2026년 10월 중순", quote_name="Thomas Schinecker",
         quote="환율 변동은 회사의 근본적인 건전성을 반영하지 않는다",
         quote_source="https://ch.marketscreener.com/boerse-nachrichten/blockbuster-treiben-roche-an-waehrungs-gegenwind-flaut-ab-ce7f51dedb8bf72d",
         thesis="Ocrevus·Vabysmo·Phesgo 등 상위 신약 5종의 Q1 합산 매출이 CER 기준 14% 늘어 기존 블록버스터의 바이오시밀러 침식을 상쇄하고 있다. EV/EBITDA와 배당수익률은 적정권이지만 PER·P/S 세 지표는 4단계여서 신약 성장 회복을 상당 부분 반영한다. 후기 임상 실패와 스위스프랑 강세가 이익·ADR 수익률을 흔드는 핵심 위험이다.",
         valuation_title="적정 2개·고평가 3개 — 신약 회복은 반영됐지만 극단적 과열은 아님",
         valuation_text="EV/EBITDA 17.8x와 배당수익률 1.9%는 3단계, Forward PER 21.9x·P/S 5.2x·TTM P/E 25.6x는 4단계다. 1·2·5단계가 비어 있는 것은 누락이 아니라, 현금창출 지표는 적정하고 주가 배수는 성장 프리미엄 영역에 모인 분포다.",
         position="스위스 SIX에 상장된 Roche의 무의결권 증권을 기초로 한 RHHBY ADR이 OTCQX에서 거래된다. 미국 정규거래소 상장 기업은 아니며, ADR을 통해 스위스 제약·진단 사업과 CHF 환율에 함께 노출된다.",
         checkpoints="① Group 매출의 CER 성장률과 CHF 환산 격차 ② Vabysmo 미국 매출 안정화 및 CHF 6B 피크 목표 ③ Ocrevus 피하주사 제형과 2029 CHF 9B 목표 진척 ④ giredestrant 등 후기 임상 결과와 2026 중단위 매출 성장 가이던스",
         pills=["Q1 CER 매출 +6%","신약 5종 매출 CHF 5.3B","Vabysmo Q1 +13% CER"],
         synthesis_fund="신약 5종 +14% CER", synthesis_val="적정 2·고평가 3", opinion="신약 성장 유효, CHF·임상 리스크 병존",
         ps_sub=["ADR 환산 TTM · 2026.07","최근 자본/ADR 환산","최근 12개월 추정치","ADR 2026 지급 환산"],
         qlabels=["H1'23","H2'23","H1'24","H2'24","H1'25","H2'25","H1'26","H2'26E"],
         revenue=[33.0,32.3,33.8,34.4,36.1,36.7,38.0,39.0],
         profit=[7.1,6.5,7.6,7.8,8.1,8.4,8.8,9.0],
         qeps=[0.79,0.73,0.84,0.87,0.91,0.95,1.00,1.03],
         peers=[["RHHBY",25.6],["NVS",18.4],["JNJ",29.3],["MRK",16.8]],
         vals=[("Forward PER","21.9x",4,"높음","저 15x","적정 20x","고 27x","신약 파이프라인 프리미엄"),
               ("P/S","5.2x",4,"높음","저 3x","적정 4x","고 6x","대형 제약 상단"),
               ("EV/EBITDA","17.8x",3,"적정","저 12x","적정 17x","고 23x","현금창출력 기준 중간"),
               ("배당수익률","1.9%",3,"적정","저 1%","적정 2.5%","고 4%","ADR 환산 추정"),
               ("P/E TTM","25.6x",4,"높음","저 16x","적정 21x","고 28x","성장 회복을 선반영")],
         ps=["$1.73","$8.90","$2.05","$0.86"],
         scenarios=[["Bear","$34–38","임상 실패와 환율 역풍"],["Base","$41–47","중단위 매출 성장 유지"],["Bull","$50–56","신약 블록버스터 가속"]],
         target=47, bull=56, bear=34,
         drivers=[("신약 포트폴리오","Vabysmo·Ocrevus 성장<br>후기 임상 파이프라인"),
                  ("진단 시너지","제약과 동반진단 결합<br>정밀의학 데이터 우위"),
                  ("특허절벽 대응","신제품 비중 확대<br>바이오시밀러 충격 흡수")],
         risks=["후기 임상 실패와 규제 지연","스위스프랑 강세의 환산 부담"],
         news=[("2026.07.23","상반기 실적과 환율 역풍","블록버스터 성장으로 실적이 개선됐지만 강한 CHF가 보고액을 눌렀다.","https://ch.marketscreener.com/boerse-nachrichten/blockbuster-treiben-roche-an-waehrungs-gegenwind-flaut-ab-ce7f51dedb8bf72d","Reuters·MarketScreener","green"),
               ("2026.07.23","Vabysmo 피크 매출 목표 방어","미국 시장 안정화를 근거로 CHF 6B 피크 매출 목표를 유지했다.","https://www.fiercepharma.com/pharma/roche-defends-chf-6b-vabysmo-peak-sales-target-despite-another-quarterly-miss","Fierce Pharma","neutral"),
               ("2026.04.24","Q1 매출 CHF 14.7B","CER +6% 성장과 Ocrevus·Vabysmo 등 신약 성장이 연간 전망을 지지했다.","https://uk.investing.com/news/earnings/roche-first-quarter-sales-meet-expectations-4624279","Investing.com","green"),
               ("2026.03.20","Emugrobart 개발 범위 축소","FSHD 효능 부족 뒤 체중감량 중 근육 보존 연구는 계속하기로 했다.","https://news.bloomberglaw.com/health-law-and-business/roche-pursues-muscle-study-for-obesity-after-halting-other-work","Bloomberg Law","neutral"),
               ("2026.03.09","Giredestrant 3상 목표 미달","유방암 후보물질이 우월성 목표를 충족하지 못해 주가가 하락했다.","https://www.marketscreener.com/news/roche-shares-fall-after-breast-cancer-treatment-misses-goal-in-late-stage-study-update-ce7e5fded98ef727","MarketScreener","red")]),
    dict(rank=36, ticker="KO", yahoo="KO", name="The Coca-Cola Company", sector="Consumer Staples",
         color="#ef4444", accent="#b91c1c",
         exchange="NYSE", subtitle="200여 개 국가에서 음료 브랜드와 농축액 플랫폼을 운영하는 글로벌 소비재 기업",
         marketcap="$352.2B", pe="28.9x", eps="$2.83", dividend="$2.12",
         next_date="2026년 7월 28일", quote_name="Henrique Braun",
         quote="올해를 강하게 출발했다",
         quote_source="https://www.coca-colacompany.com/media-center/coca-cola-reports-first-quarter-2026-results",
         thesis="농축액·브랜드 중심의 자산경량 모델, Q1 Coca-Cola Zero Sugar 13% 성장, 64년 연속 배당 증가는 가격력과 현금흐름의 질을 뒷받침한다. 그러나 P/S·PEG는 5단계, Forward PER·EV/EBITDA는 4단계로 방어적 품질에 높은 프리미엄을 지불하는 구간이다. 판매량 둔화, 원재료·환율 부담과 fairlife 생산 중단의 영향이 성장률을 낮추면 멀티플 부담이 커진다.",
         valuation_title="고평가 2개·매우 고평가 2개 — 배당 안정성만으로는 프리미엄 설명 부족",
         valuation_text="배당수익률 2.6%만 3단계이며 Forward PER·EV/EBITDA는 4단계, P/S·PEG는 5단계다. 1·2단계가 비어 있는 것은 누락이 아니라, 64년 연속 배당과 브랜드 가격력이 이미 주가에 강하게 반영된 결과다.",
         position="NYSE에 보통주가 상장된 미국 소비재 기업으로, 미국 투자자는 ADR 없이 직접 보유한다. 매출은 전 세계 200여 국가의 브랜드·농축액 네트워크에서 발생해 미국 방어주 성격과 신흥시장·환율 노출을 동시에 가진다.",
         checkpoints="① Q2 유기매출 성장 4~5% 연간 가이던스 유지 여부 ② 단위 케이스 볼륨과 가격·믹스의 기여도 ③ Comparable EPS 8~9% 성장 및 약 $12.2B FCF 전망 ④ fairlife 미국 생산 재개 시점과 CCBA 매각의 2026 하반기 종결 여부",
         pills=["Coke Zero Sugar Q1 +13%","2026 FCF 약 $12.2B","64년 연속 배당 증가"],
         synthesis_fund="가격력·Zero Sugar·배당", synthesis_val="4~5단계 4개", opinion="품질 우수, 현 가격 안전마진 제한",
         ps_sub=["TTM GAAP · 2026 Q1","2026 Q1 자본 기준","2026 FCF 전망/주식수","연환산 · $0.53×4"],
         qlabels=["Q2'24","Q3'24","Q4'24","Q1'25","Q2'25","Q3'25","Q4'25","Q1'26"],
         revenue=[12.36,11.85,11.54,11.13,12.54,12.41,11.86,11.20],
         profit=[2.41,2.85,2.20,3.33,3.81,3.69,3.05,3.54],
         qeps=[0.56,0.66,0.51,0.77,0.88,0.86,0.71,0.91],
         peers=[["KO",28.9],["PEP",21.5],["KDP",19.8],["MNST",31.2]],
         vals=[("Forward PER","24.9x",4,"높음","저 18x","적정 23x","고 29x","방어주 프리미엄"),
               ("P/S","7.1x",5,"매우높음","저 3x","적정 5x","고 7x","자산경량 농축액 모델 반영"),
               ("EV/EBITDA","22.4x",4,"높음","저 14x","적정 19x","고 25x","필수소비재 상단"),
               ("배당수익률","2.6%",3,"적정","저 2%","적정 3%","고 4%","64년 연속 배당 증가"),
               ("PEG","3.2x",5,"매우높음","저 1.5x","적정 2.2x","고 3x","성장 대비 높은 가격")],
         ps=["$2.83","$7.35","$2.84","$2.12"],
         scenarios=[["Bear","$66–72","볼륨 둔화와 원가 압박"],["Base","$76–84","4~5% 유기매출 성장"],["Bull","$88–94","가격·믹스와 환율 호조"]],
         target=84, bull=94, bear=66,
         drivers=[("가격·믹스","글로벌 브랜드 가격력<br>프리미엄·소형 패키지"),
                  ("제로 슈거","Coke Zero Sugar 성장<br>소비자 선택지 확대"),
                  ("자산경량 모델","보틀러 재프랜차이징<br>높은 마진과 FCF")],
         risks=["소비 둔화 시 판매량 압박","설탕·알루미늄·환율 비용 변동"],
         news=[("2026.07.17","fairlife 랜섬웨어로 미국 생산 중단","제품 안전 문제는 없지만 복구 기간과 공급 차질의 재무 영향은 아직 불확실하다.","https://apnews.com/article/e3a5574043f58a7340500c89d74c2ba6","AP","red"),
               ("2026.07.23","Q2 실적 발표 전 점검","7월 28일 실적에서 북미 수요·가격·마진과 가이던스 유지 여부가 핵심이다.","https://www.zacks.com/stock/news/2959652/coca-cola-q2-earnings-should-you-buy-the-stock-ahead-of-the-release","Zacks","neutral"),
               ("2026.04.28","Q1 실적·연간 가이던스 상향","Comparable EPS +18%, Zero Sugar +13%와 약 $12.2B FCF 전망을 제시했다.","https://www.coca-colacompany.com/media-center/coca-cola-reports-first-quarter-2026-results","Coca-Cola","green"),
               ("2026.02.19","64년 연속 배당 인상","분기 배당을 3.9% 올린 $0.53로 승인했다.","https://www.marketscreener.com/news/coca-cola-boosts-quarterly-dividend-by-3-9-ce7e5ddcde89f526","MarketScreener","green"),
               ("2025.12.11","Henrique Braun CEO 승계 발표","Braun이 2026년 3월 31일 CEO에 취임하고 James Quincey는 회장으로 전환했다.","https://apnews.com/article/0ffbf2d1953657a652f0a8856498c995","AP","")]),
]

def price_data(c):
    raw = json.loads(Path(f"/private/tmp/{c['yahoo']}_2y.json").read_text())
    r = raw["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    bars = []
    for i, ts in enumerate(r["timestamp"]):
        vals = [q[k][i] for k in ("open","high","low","close")]
        if any(v is None for v in vals):
            continue
        bars.append([datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d"),
                     *[round(v,2) for v in vals], int(q["volume"][i] or 0)])
    # Exclude a likely incomplete current-day bar.
    if len(bars) > 21 and bars[-1][5] < sum(x[5] for x in bars[-21:-1]) / 20 * .15:
        bars.pop()
    closes = [x[4] for x in bars]
    def ma(n):
        return [round(sum(closes[i-n+1:i+1])/n,2) if i >= n-1 else None for i in range(len(closes))]
    arrays = {f"MA{n}":ma(n)[-252:] for n in (5,20,60,120)}
    arrays["DAILY"] = bars[-252:]
    return arrays

def nav(c, prev, nxt):
    n = f'<a class="peer-nav-link" href="{nxt}_analysis_widget.html">다음 {nxt} ▶</a>' if nxt else '<span class="peer-nav-link disabled">다음 ▶</span>'
    return f'''<div class="back-bar"><a href="../index.html"><span class="brand-icon">◧</span>US Stock Widgets · 전체 종목 목록</a><div class="back-bar-nav"><a class="peer-nav-link" href="{prev}_analysis_widget.html">◀ {prev}</a><span class="back-bar-ticker">{c["ticker"]} · 시총 {c["rank"]}위</span>{n}</div></div>'''

def cards(c, p):
    cur=p["DAILY"][-1][4]; hi=max(p["DAILY"],key=lambda x:x[2]); lo=min(p["DAILY"],key=lambda x:x[3])
    mas={k:p[k][-1] for k in ("MA5","MA20","MA60","MA120")}
    ordered=sorted([("현재가",cur),*[(k,v) for k,v in mas.items()]], key=lambda x:x[1], reverse=True)
    order=">".join(x[0] for x in ordered)
    ma_rows="".join(f'<div class="ma-row"><span class="ma-name"><span class="ma-dot" style="background:var(--ma{k[2:]})"></span>{k} ({lab})</span><div style="display:flex;align-items:center;gap:10px;"><div style="display:flex;align-items:center;gap:10px;"><span class="ma-val">${v:.2f}</span><span class="ma-status {"status-above" if cur>=v else "status-below"}">현재가 {"상회" if cur>=v else "하회"}</span></div></div></div>' for k,v,lab in [("MA5",mas["MA5"],"단기"),("MA20",mas["MA20"],"중단기"),("MA60",mas["MA60"],"중기"),("MA120",mas["MA120"],"장기")])
    pills=[*[("green", text) for text in c["pills"]],("yellow",c["next_date"]),("red",c["risks"][0]),("red",c["risks"][1])]
    pill_html="".join(f'<span style="font-size:11px;padding:3px 10px;border-radius:999px;font-weight:600;background:rgba({("46,204,113" if col=="green" else "241,196,15" if col=="yellow" else "231,76,60")},.15);color:var(--{col if col!="yellow" else "event-neutral"});">{txt}</span>' for col,txt in pills)
    vals="".join(f'''<div class="val-item"><div class="val-header"><span class="val-name">{n}</span><span class="val-number">{num}</span><span class="stage-badge stage-{st}">{st}단계 {lab}</span></div><div class="val-track"><div class="val-fill" style="width:{st*19}%;background:linear-gradient(90deg,var(--green),var(--accent2),var(--red));"></div></div><div class="val-labels"><span class="val-low">{low}</span><span class="val-mid">{mid}</span><span class="val-high">{high}</span></div><div style="font-size:11px;color:var(--text3);">{note}</div></div>''' for n,num,st,lab,low,mid,high,note in c["vals"])
    stages=[]
    for st,label in enumerate(["매우 저평가","저평가","적정","고평가","매우 고평가"],1):
        names="·".join(x[0] for x in c["vals"] if x[2]==st)
        chip=f'<div style="font-size:10px;padding:2px 6px;margin-top:5px;">{names}</div>' if names else ""
        stages.append(f'<div class="stage-mini stage-{st}"><div class="stage-mini-num">{st}</div><div class="stage-mini-label">{label}</div>{chip}</div>')
    ps="".join(f'<div class="ps-card"><div class="ps-icon">{ic}</div><div class="ps-label">{lab}</div><div class="ps-value">{v}</div><div class="ps-sub">{sub}</div></div>' for ic,lab,v,sub in zip(["💵","📘","💰","🎁"],["EPS","BPS","FCF/Share","Dividend"],c["ps"],c["ps_sub"]))
    sc="".join(f'<div class="scenario-card" style="background:var(--bg3);"><b>{n}</b><div class="ps-value">{rng}</div><div class="ps-sub">{txt}</div></div>' for n,rng,txt in c["scenarios"])
    drivers="".join(f'<div style="background:var(--bg3);padding:12px;border-radius:8px;"><div style="color:var(--accent2);font-size:11px;font-weight:700;text-align:left;">{n}</div><div style="color:var(--text2);font-size:12px;line-height:1.7;">{t}</div></div>' for n,t in c["drivers"])
    stats=[("최근 매출",f"${c['revenue'][-1]:.2f}B"),("최근 순이익",f"${c['profit'][-1]:.2f}B"),("최근 EPS",f"${c['qeps'][-1]:.2f}"),("시가총액",c["marketcap"]),("P/E",c["pe"]),("연간 배당",c["dividend"]),("52주 최고",f"${hi[2]:.2f}"),("52주 최저",f"${lo[3]:.2f}"),("현재가",f"${cur:.2f}")]
    stat_html="".join(f'<div class="stat-box"><div class="stat-label">{n}</div><div class="stat-value">{v}</div><div class="stat-sub">2026.07.23 기준</div></div>' for n,v in stats)
    news="".join(f'<div class="tl-item"><div class="tl-dot {cl}"></div><div class="tl-date">{d}</div><div class="tl-title">{t}</div><div class="tl-desc">{desc}</div><a class="tl-source" href="{url}" target="_blank" rel="noopener">관련 뉴스 보기 ({site}) →</a></div>' for d,t,desc,url,site,cl in c["news"])
    maxv,minv=c["bull"],c["bear"]; tgt_pct=(c["target"]-cur)/cur*100; curpos=max(0,min(100,(cur-minv)/(maxv-minv)*100)); tgtpos=(c["target"]-minv)/(maxv-minv)*100
    scenario_edges=[[int(x) for x in re.findall(r"\d+", row[1])] for row in c["scenarios"]]
    spans=[scenario_edges[0][1]-scenario_edges[0][0],
           scenario_edges[1][0]-scenario_edges[0][1],
           scenario_edges[1][1]-scenario_edges[1][0],
           scenario_edges[2][0]-scenario_edges[1][1],
           scenario_edges[2][1]-scenario_edges[2][0]]
    widths=[x/(maxv-minv)*100 for x in spans]
    return f'''
<div class="today-banner">📌 <strong>{c["next_date"]} 다음 실적 체크</strong> · 데이터 기준일 2026.07.23 · 저장소 연속 순위 {c["rank"]}위</div>
<div class="header"><div class="header-top"><div class="ticker-block"><div><div style="display:flex;gap:10px;"><span class="ticker-badge">{c["ticker"]}</span><span style="font-size:11px;color:var(--accent2);">{c["exchange"]} · {c["sector"]}</span></div><div class="company-name">{c["name"]}</div><div class="company-sub">{c["subtitle"]}</div></div></div><div class="price-block"><div class="price-main">${cur:.2f}</div><div class="price-change">2026.07.23 완료 거래일</div><div style="font-size:11px;color:var(--text3);">52주 ${lo[3]:.2f}–${hi[2]:.2f}</div></div></div><div class="header-meta"><div class="meta-item"><span class="meta-label">시가총액</span><span class="meta-value highlight">{c["marketcap"]}</span></div><div class="meta-item"><span class="meta-label">섹터</span><span class="meta-value">{c["sector"]}</span></div><div class="meta-item"><span class="meta-label">P/E</span><span class="meta-value">{c["pe"]}</span></div><div class="meta-item"><span class="meta-label">EPS TTM</span><span class="meta-value">{c["eps"]}</span></div><div class="meta-item"><span class="meta-label">연간 배당</span><span class="meta-value">{c["dividend"]}</span></div></div></div>
<div class="nav"><button class="nav-btn active" onclick="showSection('tech')">📈 기술적 분석</button><button class="nav-btn" onclick="showSection('fund')">📊 기본적 분석</button><button class="nav-btn" onclick="showSection('valuation')">⚖️ 밸류에이션</button><button class="nav-btn" onclick="showSection('us')">🇺🇸 US 특화</button><button class="nav-btn" onclick="showSection('news')">📰 시계열 뉴스</button><button class="nav-btn" onclick="showSection('invest')">🎯 투자 포인트</button></div>
<div id="tech" class="section active"><div class="section-title">기술적 분석 — 최신 252 거래일</div><div class="price-chart-container"><div style="display:flex;justify-content:space-between;margin-bottom:10px;"><div class="range-toggle" id="{c['ticker'].lower()}RangeToggle"><button class="range-btn" data-range="1M">1개월</button><button class="range-btn" data-range="3M">3개월</button><button class="range-btn" data-range="6M">6개월</button><button class="range-btn active" data-range="1Y">1년</button></div><div id="{c['ticker'].lower()}MaToggle" style="display:flex;gap:8px;"><button class="ma-toggle-btn" data-ma="ma5" style="color:var(--ma5);border-color:var(--ma5);">● MA5</button><button class="ma-toggle-btn" data-ma="ma20" style="color:var(--ma20);border-color:var(--ma20);">● MA20</button><button class="ma-toggle-btn" data-ma="ma60" style="color:var(--ma60);border-color:var(--ma60);">● MA60</button><button class="ma-toggle-btn" data-ma="ma120" style="color:var(--ma120);border-color:var(--ma120);">● MA120</button></div></div><svg id="{c['ticker'].lower()}CandleSvg" viewBox="0 0 720 240"></svg><svg id="{c['ticker'].lower()}VolumeSvg" viewBox="0 0 720 70"></svg></div><div class="grid-2"><div class="card"><div class="card-title">핵심 가격대</div><div class="zone-list"><div class="zone-item"><span class="zone-label">52주 최고</span><span class="zone-val">${hi[2]:.2f} ({hi[0]})</span></div><div class="zone-item"><span class="zone-label">현재가</span><span class="zone-val">${cur:.2f}</span></div><div class="zone-item"><span class="zone-label">52주 최저</span><span class="zone-val">${lo[3]:.2f} ({lo[0]})</span></div></div></div><div class="card"><div class="card-title">이동평균선 현황</div>{ma_rows}<div style="margin-top:10px;background:var(--bg3);padding:12px;border-radius:8px;font-size:12px;">현재 배열: {order} 순 — 실제 표시값 기준 {"정배열" if order.startswith("현재가>MA5>MA20") else "혼조"}</div></div></div><div class="card"><div class="card-title">구간별 패턴 분석</div><div class="grid-4">{''.join(f'<div class="stat-box"><div class="stat-label">{lab}</div><div class="stat-value">{p["DAILY"][-n][4]:.2f}→{cur:.2f}</div><div class="stat-sub">{n}거래일 변화</div></div>' for lab,n in [("1개월",21),("3개월",63),("6개월",126),("1년",252)])}</div></div><div style="display:flex;gap:8px;flex-wrap:wrap;">{pill_html}</div></div>
<div id="fund" class="section"><div class="section-title">기본적 분석</div><div class="card"><div class="card-title">분기 매출·순이익·EPS</div><div class="chart-wrap" style="height:300px;"><canvas id="revProfitChart"></canvas></div></div><div class="info-box">최근 실적 · CEO {c["quote_name"]} “{c["quote"]}” <a href="{c["quote_source"]}" target="_blank" rel="noopener" style="color:var(--accent2);margin-left:6px;">발언 출처 →</a></div><div class="grid-3">{stat_html}</div><div class="card"><div class="card-title">핵심 성장 동력</div><div class="grid-3">{drivers}</div></div><div class="card"><div class="card-title">핵심 투자 논리</div><div class="tl-desc">{c["thesis"]}</div></div><div class="card"><div class="card-title">다음 실적 체크포인트</div><div class="tl-desc">{c["checkpoints"]}</div></div></div>
<div id="valuation" class="section"><div class="section-title">밸류에이션</div><div class="grid-2"><div class="card"><div class="card-title">멀티플 5단계 평가</div>{vals}</div><div class="card"><div class="card-title">피어 비교 (P/E)</div><div class="chart-wrap" style="height:270px;"><canvas id="peerChart"></canvas></div><div style="margin-top:14px;background:var(--bg3);padding:14px;border-radius:8px;font-size:12px;color:var(--text2);line-height:1.7;">{c["ticker"]} {c["pe"]}는 {c["peers"][1][0]} {c["peers"][1][1]}x, {c["peers"][2][0]} {c["peers"][2][1]}x와 비교해 현재 프리미엄 수준을 보여준다.</div></div></div><div class="card"><div class="card-title">밸류에이션 5단계</div><div class="stage-grid">{''.join(stages)}</div><div style="margin-top:10px;font-size:11px;color:var(--text3);">{'; '.join(f'{x[0]} {x[1]}는 {x[2]}단계' for x in c["vals"])}. 빈 단계는 누락 데이터가 아니라 현재 해당 밴드에 속한 지표가 없다는 뜻이다.</div></div><div class="card"><div class="card-title">Per-Share 지표</div><div class="per-share-grid">{ps}</div></div><div class="card"><div class="card-title">시나리오별 공정가치 분석</div><div class="grid-3">{sc}</div></div><div class="card"><div class="card-title">종합 밸류에이션 — {c["valuation_title"]}</div><div class="tl-desc">{c["valuation_text"]}</div></div></div>
<div id="us" class="section"><div class="section-title">US 특화 분석</div><div class="grid-2"><div class="card"><div class="card-title">전략적 위치</div><div class="tl-desc">{c["position"]}</div></div><div class="card"><div class="card-title">정책·매크로 리스크</div><div class="tl-desc">{c["risks"][0]} · {c["risks"][1]}</div></div></div><div class="rel-container"><div class="rel-title">S&P 500 대비 상대 수익률</div><div class="grid-3"><div class="stat-box"><div class="stat-label">1년 출발</div><div class="stat-value">${p["DAILY"][0][4]:.2f}</div></div><div class="stat-box"><div class="stat-label">현재</div><div class="stat-value">${cur:.2f}</div></div><div class="stat-box"><div class="stat-label">변화율</div><div class="stat-value">{(cur/p["DAILY"][0][4]-1)*100:+.1f}%</div></div></div><div class="zone-list"><div class="zone-item"><span class="zone-label">시가총액순위</span><span class="zone-val">{c["rank"]}위 (저장소 순위)</span></div><div class="zone-item"><span class="zone-label">배당</span><span class="zone-val">{c["dividend"]}</span></div><div class="zone-item"><span class="zone-label">섹터</span><span class="zone-val">{c["sector"]}</span></div></div></div><div class="card"><div class="card-title">경쟁 구도 — 실제 피어 P/E</div><div class="zone-list">{''.join(f'<div class="zone-item"><span class="zone-label">{n}</span><span class="zone-val">{v}x</span></div>' for n,v in c["peers"])}</div></div></div>
<div id="news" class="section"><div class="section-title">시계열 뉴스</div><div class="card"><div class="timeline">{news}</div><div style="font-size:11px;color:var(--text3);">🔵 주요 · 🟡 중립/예정 · 🟢 긍정 · 🔴 위험</div></div></div>
<div id="invest" class="section"><div class="section-title">투자 포인트</div><div class="card"><div class="card-title">Bull / Bear</div><div class="bull-bear"><div class="bb-box"><div class="bb-title bb-bull">Bull</div>{''.join(f'<div class="bb-item"><span>✓</span>{x[1]}</div>' for x in c["drivers"])}</div><div class="bb-box"><div class="bb-title bb-bear">Bear</div>{''.join(f'<div class="bb-item"><span>!</span>{x}</div>' for x in c["risks"])}</div></div></div><div class="card"><div class="card-title">목표가 밴드</div><div style="position:relative;padding-top:30px;"><div style="display:flex;height:14px;border-radius:7px;overflow:hidden;"><div style="width:{widths[0]:.2f}%;background:var(--green);"></div><div style="width:{widths[1]:.2f}%;background:#27ae60;"></div><div style="width:{widths[2]:.2f}%;background:var(--event-neutral);"></div><div style="width:{widths[3]:.2f}%;background:#e67e22;"></div><div style="width:{widths[4]:.2f}%;background:var(--red);"></div></div><div style="position:absolute;left:{curpos:.1f}%;top:10px;border-left:2px solid white;height:34px;"><span style="font-size:10px;">현재 ${cur:.0f}</span></div><div style="position:absolute;left:{tgtpos:.1f}%;top:0;border-left:2px solid var(--accent2);height:44px;"><span style="font-size:10px;color:var(--accent2);">▲ Base 목표 ${c["target"]} ({tgt_pct:+.1f}%)</span></div></div><div style="display:flex;justify-content:space-between;margin-top:16px;"><span>Bear ${minv}</span><span>Base ${c["target"]}</span><span>Bull ${maxv}</span></div><div style="margin-top:10px;font-size:12px;color:var(--text2);">기술적 현재가와 기본 시나리오의 간격을 실제 달러 폭에 비례해 표시했다. Base 목표는 외부 컨센서스가 아니라 본 위젯의 시나리오 기준값이다.</div></div><div class="card"><div class="card-title">5개 분석 종합</div><div class="zone-list"><div class="zone-item"><span>📈 기술</span><span class="zone-val">{order}</span></div><div class="zone-item"><span>📊 펀더멘털</span><span class="zone-val">{c["synthesis_fund"]}</span></div><div class="zone-item"><span>⚖️ 밸류에이션</span><span class="zone-val">{c["synthesis_val"]}</span></div><div class="zone-item"><span>🇺🇸 포지션</span><span class="zone-val">{c["sector"]}</span></div><div class="zone-item"><span>📰 촉매</span><span class="zone-val">{c["next_date"]}</span></div></div></div><div class="card"><div class="card-title">투자의견 요약</div><div style="display:flex;gap:16px;"><div class="stat-box" style="flex:1;"><div class="stat-label">다음 실적</div><div class="stat-value" style="font-size:15px;">{c["next_date"]}</div></div><div class="stat-box" style="flex:1;"><div class="stat-label">결론</div><div class="stat-value" style="font-size:15px;">{c["opinion"]}</div></div></div></div></div>
<div class="disclaimer">본 자료는 정보 제공 목적이며 투자 권유가 아닙니다. 가격·컨센서스·환율은 변동될 수 있습니다.</div>'''

def script(c,p):
    t=c["ticker"]; lo=t.lower()
    arr="\n".join(f"const {t}_{k} = {json.dumps(v,separators=(',',':'))};" for k,v in p.items())
    return f'''<script>
function showSection(id){{document.querySelectorAll('.section').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');event.currentTarget.classList.add('active');}}
{arr}
new Chart(document.getElementById('revProfitChart'),{{type:'bar',data:{{labels:{json.dumps(c["qlabels"])},datasets:[{{label:'매출 ($B)',data:{json.dumps(c["revenue"])},backgroundColor:'rgba(56,189,248,.45)',yAxisID:'y'}},{{label:'순이익 ($B)',data:{json.dumps(c["profit"])},backgroundColor:'rgba(46,204,113,.45)',yAxisID:'y'}},{{label:'EPS',data:{json.dumps(c["qeps"])},type:'line',borderColor:'#f1c40f',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{y:{{beginAtZero:true}},y1:{{position:'right',grid:{{drawOnChartArea:false}}}}}}}}}});
new Chart(document.getElementById('peerChart'),{{type:'bar',data:{{labels:{json.dumps([x[0] for x in c["peers"]])},datasets:[{{data:{json.dumps([x[1] for x in c["peers"]])},backgroundColor:['{STANDARD_ACCENT2}','#5c6282','#5c6282','#5c6282']}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}}}}}}}});
(function(){{const D={t}_DAILY,M={{ma5:{t}_MA5,ma20:{t}_MA20,ma60:{t}_MA60,ma120:{t}_MA120}},C=document.getElementById('{lo}CandleSvg'),V=document.getElementById('{lo}VolumeSvg'),T=document.getElementById('{lo}RangeToggle'),B=document.getElementById('{lo}MaToggle'),R={{'1M':21,'3M':63,'6M':126,'1Y':252}},S={{ma5:true,ma20:true,ma60:true,ma120:true}},N='http://www.w3.org/2000/svg';function el(n,a){{let x=document.createElementNS(N,n);Object.entries(a).forEach(([k,v])=>x.setAttribute(k,v));return x}}function draw(r){{let n=R[r],d=D.slice(-n),off=D.length-d.length;C.innerHTML='';V.innerHTML='';let W=720,H=240,L=45,RR=12,top=10,bot=20,cw=W-L-RR,ch=H-top-bot,vals=d.flatMap(x=>[x[2],x[3]]);Object.keys(S).forEach(k=>{{if(S[k]) vals.push(...M[k].slice(off).filter(x=>x!=null))}});let mx=Math.max(...vals),mn=Math.min(...vals),pad=(mx-mn)*.06,py=v=>top+ch*(1-(v-(mn-pad))/(mx-mn+2*pad)),col=cw/d.length;for(let i=0;i<d.length;i++){{let x=L+(i+.5)*col,[,o,h,l,c]=d[i],up=c>=o,co=up?'#2ecc71':'#e74c3c';C.appendChild(el('line',{{x1:x,x2:x,y1:py(h),y2:py(l),stroke:co}}));C.appendChild(el('rect',{{x:x-Math.max(1,col*.6)/2,y:Math.min(py(o),py(c)),width:Math.max(1,col*.6),height:Math.max(1,Math.abs(py(o)-py(c))),fill:co}}))}}let colors={{ma5:'#ff6b9d',ma20:'#9b59b6',ma60:'#f0c040',ma120:'#22d3ee'}};Object.keys(S).forEach(k=>{{if(!S[k])return;let pts=M[k].slice(off).map((v,i)=>v==null?null:`${{L+(i+.5)*col}},${{py(v)}}`).filter(Boolean).join(' ');C.appendChild(el('polyline',{{points:pts,fill:'none',stroke:colors[k],'stroke-width':'1.6'}}))}});let vm=Math.max(...d.map(x=>x[5]));d.forEach((x,i)=>V.appendChild(el('rect',{{x:L+i*col,y:65-55*x[5]/vm,width:Math.max(1,col*.7),height:55*x[5]/vm,fill:x[4]>=x[1]?'#2ecc71':'#e74c3c',opacity:'.6'}})))}}T.addEventListener('click',e=>{{if(!e.target.dataset.range)return;T.querySelectorAll('button').forEach(x=>x.classList.remove('active'));e.target.classList.add('active');draw(e.target.dataset.range)}});B.addEventListener('click',e=>{{let k=e.target.dataset.ma;if(!k)return;S[k]=!S[k];e.target.classList.toggle('ma-off');draw(T.querySelector('.active').dataset.range)}});draw('1Y')}})();
</script>'''

for i,c in enumerate(COMPANIES):
    p=price_data(c)
    prev="UNH" if i==0 else COMPANIES[i-1]["ticker"]
    nxt=COMPANIES[i+1]["ticker"] if i+1<len(COMPANIES) else None
    css=re.sub(r"--accent:\s*#[0-9a-fA-F]{6}", f'--accent: {c["accent"]}', STYLE)
    css=re.sub(r"--accent2:\s*#[0-9a-fA-F]{6}", f"--accent2: {STANDARD_ACCENT2}", css)
    css=re.sub(r"--accent3:\s*#[0-9a-fA-F]{6}", f"--accent3: {STANDARD_ACCENT3}", css)
    html=f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{c["ticker"]} 종합 분석 위젯</title><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script><style>{css}</style></head><body>{nav(c,prev,nxt)}{cards(c,p)}{script(c,p)}</body></html>'''
    (ROOT/"widgets"/f'{c["ticker"]}_analysis_widget.html').write_text(html)
