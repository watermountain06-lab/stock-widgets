#!/usr/bin/env python3
"""Audit all widgets against the format conventions in
.claude/skills/stock-refresh/SKILL.md and docs/canonical_widget_spec.md that
validate_widget.py does NOT check. Read-only - reports findings, fixes nothing.

Usage:
  python3 scripts/audit_widgets.py [TICKER ...]   # default: all widgets

Output: one line per widget with every failing check, then a summary count of
how many widgets fail each check (to help decide which fixes are worth
batch-scripting first).
"""
import glob
import json
import os
import re
import sys

WIDGETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "widgets")


def section(s, tab):
    opener = rf'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid="{tab}")[^>]*>'
    next_section = r'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid=")[^>]*>'
    m = re.search(rf"{opener}(.*?)(?={next_section}|<div class=\"disclaimer\")", s, re.S)
    return m.group(1) if m else ""


def check_box_key(s):
    return [] if 'class="box-key"' in s else ["box-key missing"]


def check_gold_undefined(s):
    used = "var(--gold)" in s
    defined = re.search(r"--gold\s*:", s) is not None
    return ["--gold used but not defined"] if used and not defined else []


def check_max_width(s):
    issues = []
    for name in ["today-banner", "header", "nav", "section", "disclaimer"]:
        m = re.search(rf"\.{name}\s*{{([^}}]*)}}", s)
        if not m:
            m = re.search(rf"\.{name}\s*{{(.*?)}}", s, re.S)
        if m and "max-width" not in m.group(1):
            issues.append(f"{name} missing max-width")
    return issues


def check_bull_bear_colors(s):
    icons = re.findall(r'<span class="bb-icon"[^>]*>[▲▼]</span>', s)
    uncolored = [i for i in icons if "var(--bull)" not in i and "var(--bear)" not in i]
    return [f"{len(uncolored)}/{len(icons)} bb-icon spans uncolored"] if uncolored else []


def check_ma_row_layout(s):
    rows = re.findall(r'<div class="ma-row">.*?</div>\s*(?=<div class="ma-row"|<div style="margin-top:12px|</div>\s*</div>)', s, re.S)
    bad = 0
    for r in rows:
        if re.search(r'<span class="ma-val">.*?</span>\s*<span class="ma-status', r, re.S) and "gap:10px" not in r:
            bad += 1
    return [f"{bad}/4 ma-row price not wrapped with status badge"] if bad else []


def check_zone_val_colors(s):
    tech = section(s, "tech")
    issues = []
    for label_pat, tag, expect in [
        (r"52주 최고", "tag-resist", "--red"),
        (r"현재가", "tag-current", "--accent2"),
        (r"52주 최저", "tag-support", "--green"),
    ]:
        m = re.search(
            rf'<span class="zone-label">{label_pat}[^<]*</span>.{{0,20}}<span class="zone-val"([^>]*)>.*?class="zone-tag {tag}"',
            tech,
            re.S,
        )
        if m and expect not in m.group(1):
            issues.append(f"핵심가격대 {label_pat} zone-val not colored {expect}")
    return issues


def check_opinion_summary(s):
    idx = s.find("투자의견 요약")
    if idx == -1:
        return ["투자의견 요약 card missing"]
    chunk = s[idx : idx + 800]
    issues = []
    if "flex-direction:column" not in chunk:
        issues.append("투자의견 요약 not stacked layout")
    for field in ["다음 실적", "투자의견", "목표주가", "결론"]:
        if field not in chunk:
            issues.append(f"투자의견 요약 missing {field}")
    return issues


def check_news_order(s):
    news = section(s, "news")
    dates = re.findall(r'<div class="tl-date">([^<]+)</div>', news)
    if len(dates) < 2:
        return []

    def key(d):
        # handles "2026년 5월", "2026년 5~6월" (month range - use the first month),
        # and "2026년 4월 16일"
        m = re.search(r"(\d{4})년\s*(\d{1,2})(?:~\d{1,2})?월(?:\s*(\d{1,2})일)?", d)
        if not m:
            return (0, 0, 0)
        y, mo, day = m.groups()
        return (int(y), int(mo), int(day or 15))

    keys = [key(d) for d in dates]
    if keys != sorted(keys, reverse=True):
        return ["news timeline not newest-first"]
    return []


def check_news_min_events(s):
    news = section(s, "news")
    n = news.count('class="tl-item"')
    return [f"only {n} news events (<5)"] if n < 5 else []


def check_kpi_count(s):
    fund = section(s, "fund")
    n = fund.count('class="stat-box"')
    return [f"#fund has {n} KPI stat-boxes (need 9)"] if n != 9 else []


def check_quarter_count(s):
    m = re.search(r"labels:\s*\[\s*[\"']Q[1-4]", s)
    if not m:
        return []
    line_start = s.rfind("labels:", 0, m.start())
    close = s.find("]", m.start())
    labels_str = s[line_start:close]
    n = labels_str.count("Q")
    return [f"#fund quarterly chart has {n} quarters (need 8)"] if n and n != 8 else []


def check_alpha_beta_labels(s):
    issues = []
    m = re.search(r'<div class="stat-label">알파[^<]*</div>', s)
    if m and "(" not in m.group(0):
        issues.append("알파 label has no explanation")
    m = re.search(r'<span class="zone-label">베타[^<]*</span>', s)
    if m and "(" not in m.group(0):
        issues.append("베타 label has no explanation")
    return issues


def check_valuation_verdict_tag(s):
    idx = s.find("핵심 투자 논리")
    if idx == -1:
        return ["핵심 투자 논리 not found"]
    chunk = s[idx : idx + 60]
    if not re.search(r"\((초고평가|초저평가|고평가|저평가|적정가?)\)", chunk):
        return ["핵심 투자 논리 missing (초저평가/저평가/적정/고평가/초고평가) tag"]
    return []


def check_us_bar_width(s):
    us = section(s, "us")
    if "type:'bar'" not in us and 'type:"bar"' not in us:
        return []
    if "maxBarThickness" not in us:
        return ["#us bar chart missing maxBarThickness (may render too wide)"]
    return []


def check_target_band_price_sync(s):
    val = section(s, "valuation")
    inv = section(s, "invest")
    vm = re.search(r"현재가 \$([\d,.]+)", val)
    bm = re.search(r"현재 \$([\d,.]+)", inv)
    if vm and bm:
        vp = float(vm.group(1).replace(",", ""))
        bp = float(bm.group(1).replace(",", ""))
        if vp and abs(vp - bp) / vp > 0.005:
            return [f"목표가밴드 price ${bp} != valuation-tab ${vp}"]
    return []


CHECKS = [
    check_box_key,
    check_gold_undefined,
    check_max_width,
    check_bull_bear_colors,
    check_ma_row_layout,
    check_zone_val_colors,
    check_opinion_summary,
    check_news_order,
    check_news_min_events,
    check_kpi_count,
    check_quarter_count,
    check_alpha_beta_labels,
    check_valuation_verdict_tag,
    check_us_bar_width,
    check_target_band_price_sync,
]


def load_manifest_tickers():
    manifest_path = os.path.join(os.path.dirname(WIDGETS_DIR), "data", "manifest.json")
    with open(manifest_path) as f:
        m = json.load(f)
    return {os.path.basename(x["page"]): x["ticker"] for x in m}


def main():
    requested = set(sys.argv[1:])
    ticker_by_file = load_manifest_tickers()
    files = sorted(glob.glob(os.path.join(WIDGETS_DIR, "*_analysis_widget.html")))

    all_issues = {}
    counts = {}
    for path in files:
        fname = os.path.basename(path)
        ticker = ticker_by_file.get(fname, fname.split("_")[0])
        if requested and ticker not in requested:
            continue
        s = open(path).read()
        issues = []
        for check in CHECKS:
            issues.extend(check(s))
        if issues:
            all_issues[ticker] = issues
            for i in issues:
                key = re.sub(r"[\d.$,%]+", "#", i)
                counts[key] = counts.get(key, 0) + 1

    for ticker, issues in all_issues.items():
        print(f"\n=== {ticker} ({len(issues)}) ===")
        for i in issues:
            print(f"  - {i}")

    print(f"\n{'=' * 50}")
    print(f"{len(all_issues)}/{len(files) if not requested else len(requested)} widgets have at least one issue\n")
    print("Issue frequency (for prioritizing batch fixes):")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {v:3d}x  {k}")


if __name__ == "__main__":
    main()
