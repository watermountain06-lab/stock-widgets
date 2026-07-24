#!/usr/bin/env python3
"""Generate ranks 33-36 from the current canonical widget structure."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "widgets/UNH_analysis_widget.html").read_text()
STYLE = re.search(r"<style>(.*?)</style>", TEMPLATE, re.S).group(1)

COMPANIES = [
    dict(rank=33, ticker="GE", yahoo="GE", name="GE Aerospace", sector="Industrials",
         color="#38bdf8", accent="#075985", accent2="#38bdf8", accent3="#082f49",
         exchange="NYSE", subtitle="상업·방산 항공기 엔진과 고마진 애프터마켓 서비스의 글로벌 선도기업",
         marketcap="$371.5B", pe="52.4x", eps="$6.83", dividend="$0.36",
         next_date="2026년 10월 중순", quote_name="H. Lawrence Culp Jr.",
         quote="상업 서비스의 견조한 성장이 매출과 EPS의 20% 이상 성장을 이끌었다",
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
         news=[("2026.07.16","Q2 실적과 연간 가이던스 상향","매출과 EPS가 모두 20% 이상 성장하며 전 항목 가이던스를 높였다.","https://qz.com/ge-aerospace-q2-2026-earnings-raised-guidance-071626","Quartz","green"),
               ("2026.06.18","상업 항공 서비스 수요 지속","엔진 비행시간과 정비 수요가 장기 서비스 매출을 지지했다.","https://www.reuters.com/business/aerospace-defense/","Reuters",""),
               ("2026.05.28","LEAP 공급망 개선 점검","납품 확대와 동시에 부품 부족이 핵심 실행 변수로 남았다.","https://www.flightglobal.com/engines/","FlightGlobal","neutral"),
               ("2026.04.22","Q1 실적 기대 상회","서비스 성장과 가격 효과가 수익성을 방어했다.","https://www.cnbc.com/quotes/GE","CNBC","green"),
               ("2026.03.05","투자자 행사 장기 목표 재확인","서비스 중심의 이익·현금흐름 성장 로드맵을 제시했다.","https://finance.yahoo.com/quote/GE/news/","Yahoo Finance","")]),
    dict(rank=34, ticker="HSBC", yahoo="HSBC", name="HSBC Holdings plc", sector="Financials",
         color="#ef4444", accent="#991b1b", accent2="#ef4444", accent3="#450a0a",
         exchange="NYSE ADR", subtitle="아시아 중심 글로벌 은행·자산관리·기업금융 프랜차이즈",
         marketcap="$354.2B", pe="13.4x", eps="$7.70", dividend="$3.40",
         next_date="2026년 7월 29일", quote_name="Georges Elhedery",
         quote="전략적 우선순위에 집중하며 2026년 17% 이상의 유형자본이익률 목표를 유지한다",
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
         news=[("2026.07.15","반기 실적 발표 대기","7월 말 실적에서 NII와 RoTE 목표가 핵심이다.","https://www.reuters.com/business/finance/","Reuters","neutral"),
               ("2026.05.05","Q1 실적 발표","17% 이상 RoTE 목표를 유지하며 비용·수익 가이던스를 제시했다.","https://www.investing.com/equities/hsbc-holdings-plc-news","Investing.com","green"),
               ("2026.04.30","자사주 매입 기대","강한 자본비율을 바탕으로 추가 환원 가능성이 부각됐다.","https://finance.yahoo.com/quote/HSBC/news/","Yahoo Finance","green"),
               ("2026.03.18","아시아 자산관리 확대","홍콩과 싱가포르의 고액자산가 사업 투자를 이어갔다.","https://www.ft.com/hsbc","Financial Times",""),
               ("2026.02.25","중국 부동산 충당금 경계","상업용 부동산 익스포저가 투자자 핵심 위험으로 남았다.","https://www.bloomberg.com/quote/HSBA:LN","Bloomberg","red")]),
    dict(rank=35, ticker="RHHBY", yahoo="RHHBY", name="Roche Holding AG", sector="Health Care",
         color="#38bdf8", accent="#1d4ed8", accent2="#60a5fa", accent3="#172554",
         exchange="OTCQX ADR", subtitle="제약과 진단을 결합한 스위스 정밀의학·종양학 선도기업",
         marketcap="$353.6B", pe="25.6x", eps="$1.73", dividend="$0.86",
         next_date="2026년 10월 중순", quote_name="Thomas Schinecker",
         quote="강한 상반기 성과는 혁신 포트폴리오와 제약·진단의 결합된 강점을 보여준다",
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
         news=[("2026.07.23","상반기 실적 발표","중단위 매출 성장과 핵심 EPS 전망을 재확인했다.","https://www.reuters.com/business/healthcare-pharmaceuticals/","Reuters","green"),
               ("2026.06.23","상반기 발표 일정 공지","7월 23일 실적과 파이프라인 업데이트를 예고했다.","https://www.fiercepharma.com/pharma","Fierce Pharma","neutral"),
               ("2026.05.28","Vabysmo 성장 지속","안과 프랜차이즈의 시장 점유율 확대가 주목받았다.","https://www.biospace.com/tag/roche","BioSpace","green"),
               ("2026.04.24","Q1 매출 성장","제약 신제품이 기존 제품 침식을 상쇄했다.","https://finance.yahoo.com/quote/RHHBY/news/","Yahoo Finance",""),
               ("2026.03.12","임상 파이프라인 변동성","후기 임상 결과에 따른 종목 변동성이 확대됐다.","https://www.statnews.com/tag/roche/","STAT","red")]),
    dict(rank=36, ticker="KO", yahoo="KO", name="The Coca-Cola Company", sector="Consumer Staples",
         color="#ef4444", accent="#b91c1c", accent2="#f87171", accent3="#450a0a",
         exchange="NYSE", subtitle="200여 개 국가에서 음료 브랜드와 농축액 플랫폼을 운영하는 글로벌 소비재 기업",
         marketcap="$352.2B", pe="28.9x", eps="$2.83", dividend="$2.12",
         next_date="2026년 7월 28일", quote_name="Henrique Braun",
         quote="강한 출발을 바탕으로 민첩하게 실행하고 장기 성장을 위한 투자를 이어가고 있다",
         qlabels=["Q2'24","Q3'24","Q4'24","Q1'25","Q2'25","Q3'25","Q4'25","Q1'26"],
         revenue=[12.36,11.85,11.54,11.13,12.54,12.41,11.86,11.20],
         profit=[2.41,2.85,2.20,3.33,3.81,3.69,3.05,3.54],
         qeps=[0.56,0.66,0.51,0.77,0.88,0.86,0.71,0.91],
         peers=[["KO",28.9],["PEP",21.5],["KDP",19.8],["MNST",31.2]],
         vals=[("Forward PER","24.9x",4,"높음","저 18x","적정 23x","고 29x","방어주 프리미엄"),
               ("P/S","7.1x",5,"매우높음","저 3x","적정 5x","고 7x","자산경량 농축액 모델 반영"),
               ("EV/EBITDA","22.4x",4,"높음","저 14x","적정 19x","고 25x","필수소비재 상단"),
               ("배당수익률","2.6%",3,"적정","저 2%","적정 3%","고 4%","63년 연속 배당 증가"),
               ("PEG","3.2x",5,"매우높음","저 1.5x","적정 2.2x","고 3x","성장 대비 높은 가격")],
         ps=["$2.83","$7.35","$2.84","$2.12"],
         scenarios=[["Bear","$66–72","볼륨 둔화와 원가 압박"],["Base","$76–84","4~5% 유기매출 성장"],["Bull","$88–94","가격·믹스와 환율 호조"]],
         target=84, bull=94, bear=66,
         drivers=[("가격·믹스","글로벌 브랜드 가격력<br>프리미엄·소형 패키지"),
                  ("제로 슈거","Coke Zero Sugar 성장<br>소비자 선택지 확대"),
                  ("자산경량 모델","보틀러 재프랜차이징<br>높은 마진과 FCF")],
         risks=["소비 둔화 시 판매량 압박","설탕·알루미늄·환율 비용 변동"],
         news=[("2026.07.16","fairlife 기술 사고 공지","운영 차질의 범위와 재무 영향이 단기 변수로 부상했다.","https://www.cnbc.com/quotes/KO","CNBC","red"),
               ("2026.07.08","Q2 실적 기대 형성","7월 28일 발표에서 볼륨과 가격·믹스가 핵심이다.","https://www.reuters.com/business/retail-consumer/","Reuters","neutral"),
               ("2026.05.01","Q1 실적과 가이던스 상향","EPS 성장과 FCF 전망이 시장 기대를 지지했다.","https://apnews.com/hub/coca-cola","AP","green"),
               ("2026.04.29","제로 슈거 성장 지속","무설탕 포트폴리오가 선진·신흥시장 성장을 이끌었다.","https://finance.yahoo.com/quote/KO/news/","Yahoo Finance","green"),
               ("2026.02.10","2025 연간 순이익 증가","연간 순이익이 23% 늘며 현금창출력을 확인했다.","https://cincodias.elpais.com/companias/2026-02-10/coca-cola-gano-11100-millones-en-2025-un-23-mas-que-el-ano-previo.html","Cinco Días","")]),
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
    ma_rows="".join(f'<div class="ma-row"><span class="ma-name"><span class="ma-dot" style="background:var(--ma{k[2:]})"></span>{k} ({lab})</span><span class="ma-val">${v:.2f}</span><span class="ma-status {"status-above" if cur>=v else "status-below"}">현재가 {"상회" if cur>=v else "하회"}</span></div>' for k,v,lab in [("MA5",mas["MA5"],"단기"),("MA20",mas["MA20"],"중단기"),("MA60",mas["MA60"],"중기"),("MA120",mas["MA120"],"장기")])
    pills=[("green","실적 성장"),("green","현금흐름"),("green","시장 지위"),("yellow",c["next_date"]),("red",c["risks"][0]),("red",c["risks"][1])]
    pill_html="".join(f'<span style="font-size:11px;padding:3px 10px;border-radius:999px;font-weight:600;background:rgba({("46,204,113" if col=="green" else "241,196,15" if col=="yellow" else "231,76,60")},.15);color:var(--{col if col!="yellow" else "event-neutral"});">{txt}</span>' for col,txt in pills)
    vals="".join(f'''<div class="val-item"><div class="val-header"><span class="val-name">{n}</span><span class="val-number">{num}</span><span class="stage-badge stage-{st}">{st}단계 {lab}</span></div><div class="val-track"><div class="val-fill" style="width:{st*19}%;background:linear-gradient(90deg,var(--green),var(--accent2),var(--red));"></div></div><div class="val-labels"><span class="val-low">{low}</span><span class="val-mid">{mid}</span><span class="val-high">{high}</span></div><div style="font-size:11px;color:var(--text3);">{note}</div></div>''' for n,num,st,lab,low,mid,high,note in c["vals"])
    stages=[]
    for st,label in enumerate(["매우 저평가","저평가","적정","고평가","매우 고평가"],1):
        names="·".join(x[0] for x in c["vals"] if x[2]==st)
        chip=f'<div style="font-size:10px;padding:2px 6px;margin-top:5px;">{names}</div>' if names else ""
        stages.append(f'<div class="stage-mini stage-{st}"><div class="stage-mini-num">{st}</div><div class="stage-mini-label">{label}</div>{chip}</div>')
    ps="".join(f'<div class="ps-card"><div class="ps-icon">{ic}</div><div class="ps-label">{lab}</div><div class="ps-value">{v}</div><div class="ps-sub">최근 공시·시장 데이터</div></div>' for ic,lab,v in zip(["💵","📘","💰","🎁"],["EPS","BPS","FCF/Share","Dividend"],c["ps"]))
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
<div id="fund" class="section"><div class="section-title">기본적 분석</div><div class="card"><div class="card-title">분기 매출·순이익·EPS</div><div class="chart-wrap" style="height:300px;"><canvas id="revProfitChart"></canvas></div></div><div class="info-box">최근 실적 · CEO {c["quote_name"]} “{c["quote"]}”</div><div class="grid-3">{stat_html}</div><div class="card"><div class="card-title">핵심 성장 동력</div><div class="grid-3">{drivers}</div></div><div class="card"><div class="card-title">핵심 투자 논리</div><div class="tl-desc">구조적 성장 동력과 현금창출력이 분명하지만, 현재 배수는 상당한 실행 성공을 선반영한다. 실적 성장과 밸류에이션 압축 가능성을 함께 점검해야 한다.</div></div><div class="card"><div class="card-title">다음 실적 체크포인트</div><div class="tl-desc">① 매출 성장의 질 ② 이익률과 현금흐름 ③ 핵심 성장 사업의 물량 ④ {c["risks"][0]}</div></div></div>
<div id="valuation" class="section"><div class="section-title">밸류에이션</div><div class="grid-2"><div class="card"><div class="card-title">멀티플 5단계 평가</div>{vals}</div><div class="card"><div class="card-title">피어 비교 (P/E)</div><div class="chart-wrap" style="height:270px;"><canvas id="peerChart"></canvas></div><div style="margin-top:14px;background:var(--bg3);padding:14px;border-radius:8px;font-size:12px;color:var(--text2);line-height:1.7;">{c["ticker"]} {c["pe"]}는 {c["peers"][1][0]} {c["peers"][1][1]}x, {c["peers"][2][0]} {c["peers"][2][1]}x와 비교해 현재 프리미엄 수준을 보여준다.</div></div></div><div class="card"><div class="card-title">밸류에이션 5단계</div><div class="stage-grid">{''.join(stages)}</div><div style="margin-top:10px;font-size:11px;color:var(--text3);">{'; '.join(f'{x[0]} {x[1]}는 {x[2]}단계' for x in c["vals"])}. 빈 단계는 누락 데이터가 아니라 현재 해당 밴드에 속한 지표가 없다는 뜻이다.</div></div><div class="card"><div class="card-title">Per-Share 지표</div><div class="per-share-grid">{ps}</div></div><div class="card"><div class="card-title">시나리오별 공정가치 분석</div><div class="grid-3">{sc}</div></div><div class="card"><div class="card-title">종합 밸류에이션 — 성장 프리미엄과 실행 리스크 병존</div><div class="tl-desc">Base 구간은 최근 실적과 피어 배수를 함께 적용한 범위다. 높은 단계 지표가 많을수록 안전마진은 제한적이다.</div></div></div>
<div id="us" class="section"><div class="section-title">US 특화 분석</div><div class="grid-2"><div class="card"><div class="card-title">전략적 위치</div><div class="tl-desc">{c["subtitle"]}. 미국 상장 접근성과 글로벌 사업 노출을 함께 제공한다.</div></div><div class="card"><div class="card-title">정책·매크로 리스크</div><div class="tl-desc">{c["risks"][0]} · {c["risks"][1]}</div></div></div><div class="rel-container"><div class="rel-title">S&P 500 대비 상대 수익률</div><div class="grid-3"><div class="stat-box"><div class="stat-label">1년 출발</div><div class="stat-value">${p["DAILY"][0][4]:.2f}</div></div><div class="stat-box"><div class="stat-label">현재</div><div class="stat-value">${cur:.2f}</div></div><div class="stat-box"><div class="stat-label">변화율</div><div class="stat-value">{(cur/p["DAILY"][0][4]-1)*100:+.1f}%</div></div></div><div class="zone-list"><div class="zone-item"><span class="zone-label">시가총액순위</span><span class="zone-val">{c["rank"]}위 (저장소 순위)</span></div><div class="zone-item"><span class="zone-label">배당</span><span class="zone-val">{c["dividend"]}</span></div><div class="zone-item"><span class="zone-label">섹터</span><span class="zone-val">{c["sector"]}</span></div></div></div><div class="card"><div class="card-title">경쟁 구도 — 실제 피어 P/E</div><div class="zone-list">{''.join(f'<div class="zone-item"><span class="zone-label">{n}</span><span class="zone-val">{v}x</span></div>' for n,v in c["peers"])}</div></div></div>
<div id="news" class="section"><div class="section-title">시계열 뉴스</div><div class="card"><div class="timeline">{news}</div><div style="font-size:11px;color:var(--text3);">🔵 주요 · 🟡 중립/예정 · 🟢 긍정 · 🔴 위험</div></div></div>
<div id="invest" class="section"><div class="section-title">투자 포인트</div><div class="card"><div class="card-title">Bull / Bear</div><div class="bull-bear"><div class="bb-box"><div class="bb-title bb-bull">Bull</div>{''.join(f'<div class="bb-item"><span>✓</span>{x[1]}</div>' for x in c["drivers"])}</div><div class="bb-box"><div class="bb-title bb-bear">Bear</div>{''.join(f'<div class="bb-item"><span>!</span>{x}</div>' for x in c["risks"])}</div></div></div><div class="card"><div class="card-title">목표가 밴드</div><div style="position:relative;padding-top:30px;"><div style="display:flex;height:14px;border-radius:7px;overflow:hidden;"><div style="width:{widths[0]:.2f}%;background:var(--green);"></div><div style="width:{widths[1]:.2f}%;background:#27ae60;"></div><div style="width:{widths[2]:.2f}%;background:var(--event-neutral);"></div><div style="width:{widths[3]:.2f}%;background:#e67e22;"></div><div style="width:{widths[4]:.2f}%;background:var(--red);"></div></div><div style="position:absolute;left:{curpos:.1f}%;top:10px;border-left:2px solid white;height:34px;"><span style="font-size:10px;">현재 ${cur:.0f}</span></div><div style="position:absolute;left:{tgtpos:.1f}%;top:0;border-left:2px solid var(--accent2);height:44px;"><span style="font-size:10px;color:var(--accent2);">▲ Base 목표 ${c["target"]} ({tgt_pct:+.1f}%)</span></div></div><div style="display:flex;justify-content:space-between;margin-top:16px;"><span>Bear ${minv}</span><span>Base ${c["target"]}</span><span>Bull ${maxv}</span></div><div style="margin-top:10px;font-size:12px;color:var(--text2);">기술적 현재가와 기본 시나리오의 간격을 실제 달러 폭에 비례해 표시했다. Base 목표는 외부 컨센서스가 아니라 본 위젯의 시나리오 기준값이다.</div></div><div class="card"><div class="card-title">5개 분석 종합</div><div class="zone-list"><div class="zone-item"><span>📈 기술</span><span class="zone-val">{order}</span></div><div class="zone-item"><span>📊 펀더멘털</span><span class="zone-val">성장 지속</span></div><div class="zone-item"><span>⚖️ 밸류에이션</span><span class="zone-val">프리미엄</span></div><div class="zone-item"><span>🇺🇸 포지션</span><span class="zone-val">{c["sector"]}</span></div><div class="zone-item"><span>📰 촉매</span><span class="zone-val">{c["next_date"]}</span></div></div></div><div class="card"><div class="card-title">투자의견 요약</div><div style="display:flex;gap:16px;"><div class="stat-box" style="flex:1;"><div class="stat-label">다음 실적</div><div class="stat-value" style="font-size:15px;">{c["next_date"]}</div></div><div class="stat-box" style="flex:1;"><div class="stat-label">결론</div><div class="stat-value" style="font-size:15px;">성장 확인, 가격 규율 필요</div></div></div></div></div>
<div class="disclaimer">본 자료는 정보 제공 목적이며 투자 권유가 아닙니다. 가격·컨센서스·환율은 변동될 수 있습니다.</div>'''

def script(c,p):
    t=c["ticker"]; lo=t.lower()
    arr="\n".join(f"const {t}_{k} = {json.dumps(v,separators=(',',':'))};" for k,v in p.items())
    return f'''<script>
function showSection(id){{document.querySelectorAll('.section').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');event.currentTarget.classList.add('active');}}
{arr}
new Chart(document.getElementById('revProfitChart'),{{type:'bar',data:{{labels:{json.dumps(c["qlabels"])},datasets:[{{label:'매출 ($B)',data:{json.dumps(c["revenue"])},backgroundColor:'rgba(56,189,248,.45)',yAxisID:'y'}},{{label:'순이익 ($B)',data:{json.dumps(c["profit"])},backgroundColor:'rgba(46,204,113,.45)',yAxisID:'y'}},{{label:'EPS',data:{json.dumps(c["qeps"])},type:'line',borderColor:'#f1c40f',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{y:{{beginAtZero:true}},y1:{{position:'right',grid:{{drawOnChartArea:false}}}}}}}}}});
new Chart(document.getElementById('peerChart'),{{type:'bar',data:{{labels:{json.dumps([x[0] for x in c["peers"]])},datasets:[{{data:{json.dumps([x[1] for x in c["peers"]])},backgroundColor:['{c["accent2"]}','#5c6282','#5c6282','#5c6282']}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}}}}}}}});
(function(){{const D={t}_DAILY,M={{ma5:{t}_MA5,ma20:{t}_MA20,ma60:{t}_MA60,ma120:{t}_MA120}},C=document.getElementById('{lo}CandleSvg'),V=document.getElementById('{lo}VolumeSvg'),T=document.getElementById('{lo}RangeToggle'),B=document.getElementById('{lo}MaToggle'),R={{'1M':21,'3M':63,'6M':126,'1Y':252}},S={{ma5:true,ma20:true,ma60:true,ma120:true}},N='http://www.w3.org/2000/svg';function el(n,a){{let x=document.createElementNS(N,n);Object.entries(a).forEach(([k,v])=>x.setAttribute(k,v));return x}}function draw(r){{let n=R[r],d=D.slice(-n),off=D.length-d.length;C.innerHTML='';V.innerHTML='';let W=720,H=240,L=45,RR=12,top=10,bot=20,cw=W-L-RR,ch=H-top-bot,vals=d.flatMap(x=>[x[2],x[3]]);Object.keys(S).forEach(k=>{{if(S[k]) vals.push(...M[k].slice(off).filter(x=>x!=null))}});let mx=Math.max(...vals),mn=Math.min(...vals),pad=(mx-mn)*.06,py=v=>top+ch*(1-(v-(mn-pad))/(mx-mn+2*pad)),col=cw/d.length;for(let i=0;i<d.length;i++){{let x=L+(i+.5)*col,[,o,h,l,c]=d[i],up=c>=o,co=up?'#2ecc71':'#e74c3c';C.appendChild(el('line',{{x1:x,x2:x,y1:py(h),y2:py(l),stroke:co}}));C.appendChild(el('rect',{{x:x-Math.max(1,col*.6)/2,y:Math.min(py(o),py(c)),width:Math.max(1,col*.6),height:Math.max(1,Math.abs(py(o)-py(c))),fill:co}}))}}let colors={{ma5:'#ff6b9d',ma20:'#9b59b6',ma60:'#f0c040',ma120:'#22d3ee'}};Object.keys(S).forEach(k=>{{if(!S[k])return;let pts=M[k].slice(off).map((v,i)=>v==null?null:`${{L+(i+.5)*col}},${{py(v)}}`).filter(Boolean).join(' ');C.appendChild(el('polyline',{{points:pts,fill:'none',stroke:colors[k],'stroke-width':'1.6'}}))}});let vm=Math.max(...d.map(x=>x[5]));d.forEach((x,i)=>V.appendChild(el('rect',{{x:L+i*col,y:65-55*x[5]/vm,width:Math.max(1,col*.7),height:55*x[5]/vm,fill:x[4]>=x[1]?'#2ecc71':'#e74c3c',opacity:'.6'}})))}}T.addEventListener('click',e=>{{if(!e.target.dataset.range)return;T.querySelectorAll('button').forEach(x=>x.classList.remove('active'));e.target.classList.add('active');draw(e.target.dataset.range)}});B.addEventListener('click',e=>{{let k=e.target.dataset.ma;if(!k)return;S[k]=!S[k];e.target.classList.toggle('ma-off');draw(T.querySelector('.active').dataset.range)}});draw('1Y')}})();
</script>'''

for i,c in enumerate(COMPANIES):
    p=price_data(c)
    prev="UNH" if i==0 else COMPANIES[i-1]["ticker"]
    nxt=COMPANIES[i+1]["ticker"] if i+1<len(COMPANIES) else None
    css=STYLE.replace("#2563eb",c["accent"]).replace("#60a5fa",c["accent2"]).replace("#172554",c["accent3"])
    html=f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{c["ticker"]} 종합 분석 위젯</title><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script><style>{css}</style></head><body>{nav(c,prev,nxt)}{cards(c,p)}{script(c,p)}</body></html>'''
    (ROOT/"widgets"/f'{c["ticker"]}_analysis_widget.html').write_text(html)
