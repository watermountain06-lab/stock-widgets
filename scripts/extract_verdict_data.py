#!/usr/bin/env python3
"""Read-only: extract existing 핵심 투자 논리 + stage-grid data per widget
to help draft box-key cards. Does not write anything."""
import re
import sys
from pathlib import Path

WIDGETS_DIR = Path(__file__).resolve().parent.parent / "widgets"

STAGE_LABELS = {
    "1": "매우 저평가",
    "2": "저평가",
    "3": "적정",
    "4": "고평가",
    "5": "매우 고평가",
}


def extract_fund_card(s):
    idx = s.find("핵심 투자 논리")
    if idx == -1:
        return None, None
    title_end = s.find("</div>", idx)
    title_suffix = s[idx + len("핵심 투자 논리"):title_end].strip()
    if title_suffix.startswith("—"):
        title_suffix = title_suffix.lstrip("—").strip()
    rest = s[title_end:title_end + 3000]
    m = re.search(r'<div class="tl-desc">(.*?)</div>', rest, re.S)
    if not m:
        m = re.search(r'<div style="[^"]*">(.*?)</div>', rest, re.S)
    body = m.group(1).strip() if m else None
    return title_suffix, body


def extract_stage_grid_tally(s):
    idx = s.find('<div class="stage-grid">')
    if idx == -1:
        return None
    end = s.find("\n", idx)
    # stage-grid is usually one line; grab up to 3000 chars to be safe
    chunk = s[idx: idx + 3000]
    # find matching close by counting divs from stage-grid open
    # simpler: extract each stage-mini block and its optional tag span
    minis = re.findall(
        r'<div class="stage-mini stage-(\d)">.*?<div class="stage-mini-label">([^<]*)</div>(?:<div[^>]*>([^<]*)</div>)?',
        chunk,
    )
    tally = {}
    for stage, label, tag in minis:
        tags = [t.strip() for t in tag.split("·")] if tag else []
        tally[stage] = tags
    return tally


def compute_verdict(tally):
    if not tally:
        return None
    counts = {"low": 0, "mid": 0, "high": 0}
    detail = []
    for stage, tags in tally.items():
        n = len(tags)
        if n == 0:
            continue
        if stage in ("1", "2"):
            counts["low"] += n
        elif stage == "3":
            counts["mid"] += n
        else:
            counts["high"] += n
        detail.append(f"stage{stage}:{tags}")
    if counts["high"] > counts["low"] and counts["high"] >= counts["mid"]:
        verdict = "고평가"
    elif counts["low"] > counts["high"] and counts["low"] >= counts["mid"]:
        verdict = "저평가"
    else:
        verdict = "적정"
    return verdict, counts, detail


def main():
    tickers = sys.argv[1:]
    if not tickers:
        tickers = ["AAPL","ABBV","AMAT","AMD","ASML","BAC","BRK_B","COST","CSCO","GE",
                   "GOOGL","HD","HSBC","INTC","JNJ","JPM","KO","LLY","LRCX","MA","MRK",
                   "MS","MU","ORCL","PG","RHHBY","SKHY","SPCX","TSLA","UNH","V","WMT","XOM"]
    for t in tickers:
        path = WIDGETS_DIR / f"{t}_analysis_widget.html"
        if not path.exists():
            print(f"{t}: FILE NOT FOUND")
            continue
        s = path.read_text(encoding="utf-8")
        title_suffix, body = extract_fund_card(s)
        tally = extract_stage_grid_tally(s)
        result = compute_verdict(tally) if tally else None
        print(f"=== {t} ===")
        print(f"  title_suffix: {title_suffix!r}")
        print(f"  body: {body[:200] if body else None!r}")
        if result:
            verdict, counts, detail = result
            print(f"  verdict: {verdict}  counts:{counts}")
            print(f"  detail: {detail}")
        else:
            print("  stage-grid: NOT PARSED")
        print()


if __name__ == "__main__":
    main()
