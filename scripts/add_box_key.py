#!/usr/bin/env python3
"""Add a box-key card (top-of-page 핵심 투자 논리 summary) to widgets that
are missing one, and add the (고평가/저평가/적정) verdict tag to the
existing 핵심 투자 논리 card in the fund tab.

Verdict per ticker comes from majority-vote over that widget's own
"밸류에이션 5단계" stage-grid (already-computed data in the file, see
scripts/extract_verdict_data.py). Body text is reused verbatim from the
existing fund-tab card - nothing new is fabricated, matching PM's own
box-key/fund-tab duplication pattern.
"""
import re
import sys
from pathlib import Path

WIDGETS_DIR = Path(__file__).resolve().parent.parent / "widgets"

VERDICT_COLOR = {
    "고평가": "var(--red)",
    "저평가": "var(--green)",
    "적정": "#f0c040",
}

# ticker -> (verdict, headline for box-key title)
DATA = {
    "AAPL": ("고평가", "TTM FCF $113B · ROE 141%"),
    "ABBV": ("적정", "GAAP PER 124.8x는 회계 왜곡, Adjusted PER 24.9x가 실질 밸류에이션"),
    "AMAT": ("고평가", "Q2 FY26 사상 최대 매출 vs 6/30 고점 후 -18.4% 급락"),
    "AMD": ("고평가", "OpenAI 6GW 공급계약·지분 10% 취득 — MI400 매출 전망이 관건"),
    "ASML": ("고평가", "EUV 리소그래피 100% 독점 · 수주잔고 €38.8B"),
    "BAC": ("적정", "트레이딩 +70%·IB 수수료 +50%, 17분기 연속 성장의 지속가능성"),
    "BRK_B": ("저평가", "역대 최대 현금 $397B · PBR 1.41x"),
    "COST": ("고평가", "Q3 순매출 +11.6% · PER 46.7x"),
    "CSCO": ("고평가", "AI 인프라 수주목표 $5B→$9B 상향, 6분기 연속 가속"),
    "GE": ("고평가", "LEAP 설치기반 2030년까지 2배 전망 · Forward PER 39.8x"),
    "GOOGL": ("적정", "PER 27.8x — 빅테크 최저 수준 · Cloud 백로그 $460B"),
    "HD": ("고평가", "Q1 FY26 매출 $41.77B(+4.8%) · TTM PER 23.6x"),
    "HSBC": ("고평가", "웰스 잔액 $1.6T · RoTE 17%+"),
    "INTC": ("고평가", "Non-GAAP EPS 흑자 전환 추세 vs GAAP은 여전히 적자"),
    "JNJ": ("고평가", "탈크 소송충당금發 GAAP 변동성, 최근 4개 분기는 우상향"),
    "JPM": ("고평가", "Q1 트레이딩 $11.6B 역대최고 · CET1 14.3%"),
    "KO": ("고평가", "Q2 매출 $13.37B(+7%) · 2026 가이던스 상향"),
    "LLY": ("적정", "GLP-1 듀얼 플랫폼 $36.5B · 오르포글리프론 하반기 출시"),
    "LRCX": ("고평가", "Q4 FY26 매출 $6.72B·GAAP EPS $1.81 확정"),
    "MA": ("저평가", "펀더멘털 +12%/+21% 견조 vs 스테이블코인 잠식 우려로 -5.8% 급락"),
    "MRK": ("고평가", "Keytruda Q1 +12% · Cidara 인수비용發 TTM PER 36.9x 왜곡"),
    "MS": ("고평가", "Q2 매출 +27%·EPS +62% · ROTCE 26.6%"),
    "MU": ("저평가", "HBM 완판·2027 대부분 예약 vs Forward PER 10x"),
    "ORCL": ("고평가", "RPO $638B(연매출 9.5배) · OCI Q4 FY26 +93%"),
    "PG": ("적정", "방어적 FCF 생산성 100% vs Q4 유기매출 보합"),
    "RHHBY": ("고평가", "상위 신약 5종 Q1 CER +14% · PER·P/S 4단계"),
    "SKHY": ("저평가", "HBM 시장점유율 57% 세계 1위 · 영업이익률 72%"),
    "TSLA": ("고평가", "EV 단독 PER 200x, Robotaxi·Optimus 옵션가치 반영 여부가 핵심"),
    "UNH": ("고평가", "2025 비용충격 후 정상화 — 의료비율 86.7% 안정 여부가 관건"),
    "V": ("고평가", "OPM 60%+ 네트워크 마진 vs 스테이블코인 잠식 리스크"),
    "WMT": ("고평가", "이커머스·광고 사업 전환 vs 전통 유통 밸류에이션 프리미엄"),
    "XOM": ("고평가", "GAAP EPS -43%는 파생상품 타이밍효과, Non-GAAP은 컨센서스 상회"),
}


def extract_fund_card(s):
    idx = s.find("핵심 투자 논리")
    if idx == -1:
        return None
    title_start = idx
    title_end = s.find("</div>", idx)
    title_suffix = s[idx + len("핵심 투자 논리"):title_end].strip()
    if title_suffix.startswith("—"):
        title_suffix = title_suffix.lstrip("—").strip()
    rest = s[title_end:title_end + 3000]
    m = re.search(r'<div class="tl-desc">(.*?)</div>', rest, re.S)
    body_tag = "tl-desc"
    if not m:
        m = re.search(r'<div style="([^"]*)">(.*?)</div>', rest, re.S)
        body_style = m.group(1) if m else None
        body_tag = "inline"
    body = m.group(2 if body_tag == "inline" else 1).strip() if m else None
    body_end = title_end + m.end() if m else None
    return {
        "title_start": title_start,
        "title_end": title_end,
        "title_suffix": title_suffix,
        "body": body,
        "body_tag": body_tag,
        "body_style": body_style if body_tag == "inline" else None,
    }


def build_box_key(verdict, headline, body):
    color = VERDICT_COLOR[verdict]
    return (
        f'<div class="box-key">\n'
        f'<div style="font-size:13px;font-weight:500;color:var(--accent2);margin-bottom:4px;">'
        f'핵심 투자 논리 <span style="color:{color};">({verdict})</span> — {headline}</div>\n'
        f'<div style="font-size:12px;color:var(--text2);line-height:1.6;">{body}</div>\n'
        f'</div>\n'
    )


BOX_KEY_CSS = (
    "  .box-key { background: rgba(56,189,248,0.1); border: 1px solid var(--accent3); "
    "border-radius: var(--radius); padding: 12px 16px; max-width: 1100px; margin: 0 auto 16px; }\n"
)


def process(ticker):
    path = WIDGETS_DIR / f"{ticker}_analysis_widget.html"
    s = path.read_text(encoding="utf-8")

    if 'class="box-key"' in s:
        return "SKIP: box-key already present"
    if ticker not in DATA:
        return "SKIP: no data drafted"

    verdict, headline = DATA[ticker]
    color = VERDICT_COLOR[verdict]

    fund = extract_fund_card(s)
    if fund is None or fund["body"] is None:
        return "ABORT: could not extract fund-tab 핵심 투자 논리 card"

    box_key_html = build_box_key(verdict, headline, fund["body"])

    # 0. insert missing .box-key CSS rule before the first `.nav {` rule
    if ".box-key {" not in s:
        nav_css_idx = s.find(".nav {")
        if nav_css_idx == -1:
            return "ABORT: .nav { CSS rule not found"
        s = s[:nav_css_idx] + BOX_KEY_CSS + s[nav_css_idx:]
        # re-extract fund card offsets since s changed
        fund = extract_fund_card(s)

    nav_idx = s.find('<div class="nav">')
    if nav_idx == -1:
        return "ABORT: <div class=\"nav\"> not found"

    # 1. insert box-key right before nav
    new_s = s[:nav_idx] + box_key_html + s[nav_idx:]

    # 2. add tag to the fund-tab card title (offset shifts by len(box_key_html)
    #    only if fund card is after nav_idx, which it always is here)
    shift = len(box_key_html)
    old_title_start = fund["title_start"] + shift
    old_title_end = fund["title_end"] + shift
    tag_span = f' <span style="color:{color};">({verdict})</span>'
    new_s = new_s[:old_title_end] + tag_span + new_s[old_title_end:]
    # note: title text itself (핵심 투자 논리 + optional — suffix) stays as-is,
    # tag is appended right before the closing </div> of the title

    if new_s.count("<div") != s.count("<div") + box_key_html.count("<div"):
        return "ABORT: div-open count mismatch after edit"
    if new_s.count("</div>") != s.count("</div>") + box_key_html.count("</div>"):
        return "ABORT: div-close count mismatch after edit"

    path.write_text(new_s, encoding="utf-8")
    return "FIXED"


def main():
    tickers = sys.argv[1:] or list(DATA.keys())
    for t in tickers:
        print(f"{t}: {process(t)}")


if __name__ == "__main__":
    main()
