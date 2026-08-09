#!/usr/bin/env python3
"""Read-only: check every widget for the class of bug found on NVDA -
the same valuation multiple (PER, PBR, PSR, PCR, EV/EBITDA, P/S, Forward PER,
FCF 수익률, 배당수익률...) quoted with a different number in prose elsewhere
in the widget (종합 밸류에이션, 피어 비교, 시나리오, 목표가 밴드, #invest's
5개 분석 종합...) than the canonical val-item badge, because the prose
mention never got resynced when the val-item was last recalculated. Also
checks EV/EBITDA footnote self-consistency (EV $X / EBITDA $Y should equal
the displayed multiple) and market cap vs price x shares outstanding.

Every finding carries a %-gap so results can be triaged - a 2% gap is
likely just rounding noise, a 30%+ gap is very likely a real stale/wrong
number worth fixing.

Usage: python3 scripts/audit_valuation_consistency.py [TICKER ...] [--min-gap N]
"""
import glob
import json
import os
import re
import sys

WIDGETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "widgets")

# Loose "keyword ... number x" patterns used to find prose mentions outside
# the val-item badges themselves (news-style sentences, other cards).
PROSE_PATTERNS = {
    # PER immediately preceded by an adjustment qualifier (GAAP, Non-GAAP,
    # 실질, 조정, Adjusted...) is a *different* metric from bare "PER" and
    # from *each other* - a ticker can legitimately carry both a GAAP figure
    # and a separately-labeled adjusted one (AVGO: GAAP 69.1x vs Non-GAAP
    # 50.9x; AMZN: bare 22.1x vs "실질" ~46x ex-Anthropic). Keep each
    # qualifier its own bucket so they're only checked for self-consistency,
    # never cross-compared against an unrelated qualifier's figure.
    "Non-GAAP PER":r"Non-GAAP\s*PER\s*(?:\([^)]*\))?\s*:?\s*(?:\$[\d,.]+÷\$[\d,.]+\([^)]*\)\s*=\s*)?([\d]+\.?\d*)x",
    "GAAP PER":   r"(?<!Non-)\bGAAP\s*PER\s*([\d]+\.?\d*)x",
    "실질 PER":    r"실질\s*PER\s*(?:기준)?\s*~?\s*([\d]+\.?\d*)x",
    "조정 PER":    r"조정후?\s*PER\s*~?\s*([\d]+\.?\d*)x",
    "PER":        r"(?<!Forward )(?<!EV/E)(?<!Non-GAAP )(?<!GAAP )(?<!실질 )(?<!조정 )(?<!조정후 )\bPER\s*(?:\((?:TTM|GAAP TTM)\))?\s*([\d]+\.?\d*)x",
    "Forward PER":r"Forward\s*P(?:ER|/E)(?:\([^)]*\))?\s*([\d]+\.?\d*)x",
    "PBR":        r"\bPBR\s*([\d]+\.?\d*)x",
    "PSR":        r"\bPSR\s*(?:\([^)]*\))?\s*([\d]+\.?\d*)x",
    "PCR":        r"\bPCR\s*(?:\([^)]*\))?\s*([\d]+\.?\d*)x",
    "EV/EBITDA":  r"EV[/／]EBITDA\s*([\d]+\.?\d*)x",
    "P/S":        r"(?<!F)\bP[/／]S\b\s*([\d]+\.?\d*)x",
}


def extract_val_items(s):
    """(name -> [numbers]) from the canonical val-item badges."""
    out = {}
    for m in re.finditer(
        r'<span class="val-name">([^<]+)</span>.*?<span class="val-number">([\d.]+)x',
        s, re.S,
    ):
        name = re.sub(r"\s*\([^)]*\)", "", m.group(1)).strip()
        out.setdefault(name, []).append(float(m.group(2)))
    return out


def strip_val_item_blocks(s):
    """Remove the val-header badge markup so prose scanning doesn't just
    re-find the val-items themselves."""
    return re.sub(r'<span class="val-name">.*?</span>\s*<div[^>]*>.*?</div>', "", s, flags=re.S)


def check_metric_consistency(s):
    """Returns (gap_pct, message) tuples."""
    issues = []
    val_items = extract_val_items(s)
    prose = strip_val_item_blocks(s)
    for keyword, pat in PROSE_PATTERNS.items():
        prose_vals = sorted(set(re.findall(pat, prose)), key=float)
        if not prose_vals:
            continue
        canon = val_items.get(keyword)  # exact match only - "Forward PER" != "PER"
        if canon is None:
            if len(prose_vals) > 1:
                spread = (float(prose_vals[-1]) - float(prose_vals[0])) / float(prose_vals[0])
                if spread > 0.01:  # >1% - below that it's just decimal rounding (69 vs 69.1)
                    issues.append((spread, f"{keyword}: prose mentions disagree with each other: {prose_vals} ({spread*100:.0f}% spread)"))
            continue
        # A keyword can legitimately map to >1 val-item (e.g. ABBV's "PER
        # (GAAP TTM)" and "PER (Adjusted TTM)" both strip to "PER") - compare
        # each prose value against its *nearest* canon value, not the min.
        mismatched = [v for v in prose_vals if min(abs(float(v) - c) / c for c in canon) > 0.05]
        if mismatched:
            canon_str = [f"{v:g}" for v in canon]
            worst_gap = max(min(abs(float(v) - c) / c for c in canon) for v in mismatched)
            issues.append((worst_gap, f"{keyword}: val-item badge is {canon_str}x but prose says {mismatched}x ({worst_gap*100:.0f}% gap)"))
    return issues


def check_ev_ebitda_footnote(s):
    issues = []
    m = re.search(r"EV\s*\$([\d,.]+)([TB])\s*[÷/]\s*EBITDA\s*\$([\d,.]+)([TB])\(?TTM\)?", s)
    val_items = extract_val_items(s)
    canon = val_items.get("EV/EBITDA")
    if m and canon:
        ev = float(m.group(1).replace(",", "")) * (1000 if m.group(2) == "T" else 1)
        ebitda = float(m.group(3).replace(",", "")) * (1000 if m.group(4) == "T" else 1)
        implied = ev / ebitda
        shown = canon[0]
        gap = abs(implied - shown) / shown
        if gap > 0.03:
            issues.append((gap, f"EV/EBITDA footnote implies {implied:.1f}x but val-item badge shows {shown}x ({gap*100:.0f}% gap)"))
    return issues


def check_market_cap(s):
    issues = []
    price_m = re.search(r"현재가 \$([\d,.]+)", s)
    cap_m = re.search(r"시가총액[^\d]{0,10}\$([\d,.]+)([TB])", s)
    shares_m = re.search(r"([\d]+\.?\d*)B\s*주\)", s)
    if price_m and cap_m and shares_m:
        price = float(price_m.group(1).replace(",", ""))
        cap = float(cap_m.group(1).replace(",", "")) * (1000 if cap_m.group(2) == "T" else 1)
        shares = float(shares_m.group(1))
        implied_cap_b = price * shares
        if cap > 0:
            gap = abs(implied_cap_b - cap) / cap
            if gap > 0.03:
                issues.append((gap, f"시가총액 ${cap:.0f}B doesn't match 현재가(${price})x주식수({shares}B)=${implied_cap_b:.0f}B ({gap*100:.0f}% gap)"))
    return issues


CHECKS = [check_metric_consistency, check_ev_ebitda_footnote, check_market_cap]


def main():
    args = sys.argv[1:]
    min_gap = 0.0
    if "--min-gap" in args:
        i = args.index("--min-gap")
        min_gap = float(args[i + 1]) / 100
        del args[i:i + 2]
    tickers = set(t.upper() for t in args)

    manifest_path = os.path.join(os.path.dirname(WIDGETS_DIR), "data", "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    ticker_by_file = {os.path.basename(x["page"]): x["ticker"] for x in manifest}

    files = sorted(glob.glob(os.path.join(WIDGETS_DIR, "*.html")))
    total_issues = 0
    widgets_with_issues = 0
    scanned = 0
    all_findings = []  # (gap, ticker, message) across the whole fleet, for the top-offenders summary
    for path in files:
        name = os.path.basename(path)
        ticker = ticker_by_file.get(name, name)
        if tickers and ticker.upper() not in tickers:
            continue
        scanned += 1
        s = open(path, encoding="utf-8").read()
        findings = []
        for check in CHECKS:
            findings.extend(check(s))
        findings = [f for f in findings if f[0] >= min_gap]
        findings.sort(key=lambda x: -x[0])
        if findings:
            widgets_with_issues += 1
            total_issues += len(findings)
            print(f"\n{ticker} ({name}):")
            for gap, msg in findings:
                print(f"  - {msg}")
                all_findings.append((gap, ticker, msg))

    print(f"\n{'='*50}\n{widgets_with_issues}/{scanned} widgets have at least one issue, {total_issues} issues total")

    if not tickers and all_findings:
        print(f"\nTop 15 by gap size (most likely real errors, not rounding noise):")
        for gap, ticker, msg in sorted(all_findings, key=lambda x: -x[0])[:15]:
            print(f"  {ticker}: {msg}")


if __name__ == "__main__":
    main()
