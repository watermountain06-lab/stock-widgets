#!/usr/bin/env python3
"""Diagnose (read-only) the 목표가 밴드 cards on widgets flagged by
validate_widget.py / audit_widgets.py for a price mismatch. Prints, per
widget: detected segment mode (5 vs 7), the Bear/Base/Bull ranges as parsed,
the true current price (from the widget's own last DAILY bar), the target
price, and the recomputed marker positions + upside% - so results can be
sanity-checked before scripts/fix_target_band.py writes anything.

Usage: python3 scripts/diagnose_target_band.py TICKER [TICKER ...]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from target_band_gauge import compute  # noqa: E402


def section(s, tab):
    opener = rf'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid="{tab}")[^>]*>'
    next_section = r'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid=")[^>]*>'
    m = re.search(rf"{opener}(.*?)(?={next_section}|<div class=\"disclaimer\")", s, re.S)
    return m.group(1) if m else ""


def true_current_price(s, ticker):
    safe = ticker.replace(".", "_")
    m = re.search(rf"const {re.escape(safe)}_DAILY = (\[.*?\]);", s, re.S)
    if not m:
        return None
    data = json.loads(m.group(1))
    return data[-1][4]  # [date, open, high, low, close, volume]


def parse_num(s):
    return float(s.replace(",", ""))


def diagnose(ticker, path):
    s = open(path).read()
    inv = section(s, "invest")

    m = re.search(r'<div class="card-title">목표가 밴드[^<]*</div>', inv)
    if not m:
        print(f"{ticker}: no 목표가 밴드 card found (skip)")
        return

    # color-bar segment count = mode. The bar's own container div is followed
    # by N sibling `width:` divs, then the current-price marker (a div with
    # `top:10px;left:` positioning) - count width-divs up to that marker.
    bar_start = inv.find("overflow:hidden;display:flex;")
    marker_start = inv.find("top:10px;left:", bar_start) if bar_start != -1 else -1
    if bar_start != -1 and marker_start != -1:
        bar_body = inv[bar_start:marker_start]
        n_segments = len(re.findall(r'<div style="width:', bar_body))
    else:
        n_segments = 0
    mode = "no-pad (5-seg)" if n_segments == 5 else ("padded (7-seg)" if n_segments == 7 else f"UNKNOWN ({n_segments} segs)")

    bear = re.search(r"Bear\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", inv)
    base = re.search(r"Base\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", inv)
    bull = re.search(r"Bull\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", inv)

    cur_shown = re.search(r"현재 \$([\d,.]+)", inv)
    target_shown = re.search(r"목표 \$([\d,.]+)", inv)

    true_price = true_current_price(s, ticker)

    print(f"\n=== {ticker} ===")
    print(f"  segment mode: {mode}")
    print(f"  Bear/Base/Bull found: {bool(bear)}/{bool(base)}/{bool(bull)}")
    if not (bear and base and bull and target_shown):
        print("  -> INCOMPLETE PARSE, needs manual handling")
        if cur_shown:
            print(f"  shown current: ${cur_shown.group(1)}  |  true (last daily bar): {true_price}")
        return

    bear_r = (parse_num(bear.group(1)), parse_num(bear.group(2)))
    base_r = (parse_num(base.group(1)), parse_num(base.group(2)))
    bull_r = (parse_num(bull.group(1)), parse_num(bull.group(2)))
    target = parse_num(target_shown.group(1))

    print(f"  Bear {bear_r}  Base {base_r}  Bull {bull_r}  target ${target}")
    print(f"  shown current: ${cur_shown.group(1) if cur_shown else '?'}  |  true (last daily bar): ${true_price}")

    if true_price is None or "UNKNOWN" in mode:
        print("  -> cannot auto-compute, needs manual handling")
        return

    pad = mode.startswith("padded")
    r = compute(list(bear_r), list(base_r), list(bull_r), true_price, target, pad=pad)
    print(f"  RECOMPUTED: current_marker={r['current_marker_pct']:.1f}%  target_marker={r['target_marker_pct']:.1f}%  upside={r['upside_pct']:+.1f}%")


def main():
    manifest = json.load(open(os.path.join(ROOT, "data", "manifest.json")))
    paths = {x["ticker"]: os.path.join(ROOT, x["page"]) for x in manifest}
    for ticker in sys.argv[1:]:
        path = paths.get(ticker)
        if not path or not os.path.exists(path):
            print(f"{ticker}: no widget file")
            continue
        diagnose(ticker, path)


if __name__ == "__main__":
    main()
