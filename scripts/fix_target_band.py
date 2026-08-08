#!/usr/bin/env python3
"""Fix the 목표가 밴드 card for widgets that match the PM/CAT-style pattern
(5- or 7-segment bar, full "Bear $X~Y / Base $X~Y / Bull $X~Y" text nearby).
Confirmed applicable to: AAPL AMZN AVGO GOOGL LRCX META MU MSFT NVS PLTR RTX
- do not run on AMAT/MS/GE/KO/PG/RHHBY, which use different markup/data
shapes (see diagnose_target_band.py output).

Isolates just the small target-band card snippet, edits that copy with plain
string replacement (same approach as hand-editing with Edit - no index
arithmetic on the full file, which is what corrupted a file the first time
this script was written), then splices it back with a single str.replace.

Usage: python3 scripts/fix_target_band.py TICKER [TICKER ...]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from target_band_gauge import compute  # noqa: E402


def parse_num(s):
    return float(s.replace(",", ""))


def fmt(x):
    s = f"{x:,.2f}"
    return s[:-3] if s.endswith(".00") else s.rstrip("0").rstrip(".") if "." in s else s


def fix(ticker, path):
    s = open(path).read()

    card_start = s.find('<div class="card-title">목표가 밴드')
    if card_start == -1:
        print(f"SKIP {ticker}: no 목표가 밴드 card")
        return
    # card ends right before the next sibling <div class="card"> at the same
    # level, which in every PM/CAT-style widget is "5개 분석 종합"
    card_end = s.find('5개 분석 종합', card_start)
    if card_end == -1:
        print(f"SKIP {ticker}: could not bound the card (no 5개 분석 종합 after it)")
        return
    # back up to the start of that sibling card's own <div class="card">
    card_end = s.rfind('<div class="card"', card_start, card_end)
    card = s[card_start:card_end]

    bar_start = card.find("overflow:hidden;display:flex;")
    marker_start = card.find("top:10px;left:", bar_start)
    bar_body = card[bar_start:marker_start]
    n_segments = len(re.findall(r'<div style="width:', bar_body))
    pad = n_segments == 7
    if n_segments not in (5, 7):
        print(f"SKIP {ticker}: unrecognized segment count {n_segments}")
        return

    bear = re.search(r"Bear\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", card)
    base = re.search(r"Base\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", card)
    bull = re.search(r"Bull\D*\$?([\d,.]+)\s*[~-]\s*\$?([\d,.]+)", card)
    target_shown = re.search(r"목표 \$([\d,.]+)", card)
    cur_shown = re.search(r"현재 \$([\d,.]+)", card)
    if not (bear and base and bull and target_shown and cur_shown):
        print(f"SKIP {ticker}: could not parse Bear/Base/Bull/target/current")
        return

    safe = ticker.replace(".", "_")
    dm = re.search(rf"const {re.escape(safe)}_DAILY = (\[.*?\]);", s, re.S)
    true_price = json.loads(dm.group(1))[-1][4]

    bear_r = [parse_num(bear.group(1)), parse_num(bear.group(2))]
    base_r = [parse_num(base.group(1)), parse_num(base.group(2))]
    bull_r = [parse_num(bull.group(1)), parse_num(bull.group(2))]
    target = parse_num(target_shown.group(1))
    old_cur = cur_shown.group(1)

    r = compute(bear_r, base_r, bull_r, true_price, target, pad=pad)

    new_card = card

    # 1) segment widths, in order
    seg_iter = iter(r["segments_pct"])
    new_bar_body = re.sub(r"width:[\d.]+%", lambda m: f"width:{next(seg_iter):.1f}%", bar_body)
    new_card = new_card.replace(bar_body, new_bar_body, 1)

    # 2) current marker: find its OLD percentage from the accent2 marker line
    #    (the bar-line div: width:2px;height:28px;background:var(--accent2))
    old_pct_m = re.search(r"left:([\d.]+)%;width:2px;height:28px;background:var\(--accent2\)", new_card)
    if not old_pct_m:
        print(f"SKIP {ticker}: could not find current-marker percentage")
        return
    old_pct = old_pct_m.group(1)
    n_before = new_card.count(f"left:{old_pct}%")
    new_card = new_card.replace(f"left:{old_pct}%", f"left:{r['current_marker_pct']:.1f}%")
    n_after_check = new_card.count(f"left:{r['current_marker_pct']:.1f}%")
    if n_before != 2:
        print(f"WARN {ticker}: expected 2 occurrences of current-marker left:{old_pct}%, found {n_before}")

    # 3) current price text
    new_card = new_card.replace(f"현재 ${old_cur}", f"현재 ${fmt(true_price)}", 1)

    # 4) upside % and its arrow (▲ for positive, ▼ for negative - must agree
    #    with the recomputed sign, not just carry over the old arrow)
    old_upside_m = re.search(rf"([▲▼])\s*목표 \${re.escape(target_shown.group(1))}\s*\(([+\-][\d.]+)%\)", new_card)
    if old_upside_m:
        sign = "+" if r["upside_pct"] >= 0 else ""
        new_arrow = "▲" if r["upside_pct"] >= 0 else "▼"
        new_card = (
            new_card[: old_upside_m.start(1)]
            + new_arrow
            + new_card[old_upside_m.end(1) : old_upside_m.start(2)]
            + f"{sign}{r['upside_pct']:.1f}"
            + new_card[old_upside_m.end(2) :]
        )

    if new_card == card:
        print(f"NOCHANGE {ticker}")
        return

    new_s = s.replace(card, new_card, 1)
    if new_s.count("<div") != new_s.count("</div>"):
        print(f"ABORT {ticker}: div balance would break, not writing")
        return

    open(path, "w").write(new_s)
    print(f"FIXED {ticker}: current ${old_cur} -> ${fmt(true_price)}, marker {old_pct}%->{r['current_marker_pct']:.1f}%, upside -> {r['upside_pct']:+.1f}%")

    old_upside_str = old_upside_m.group(1) if old_upside_m else None
    hits = []
    if old_cur != fmt(true_price):
        hits += re.findall(r".{30}" + re.escape(old_cur) + r".{10}", new_s)
    if old_upside_str:
        hits += re.findall(r".{30}" + re.escape(old_upside_str) + r"%.{10}", new_s)
    if hits:
        print(f"  ! {len(hits)} other spot(s) may still reference the old numbers (check manually):")
        for h in hits[:8]:
            print(f"    ...{h}...")


def main():
    manifest = json.load(open(os.path.join(ROOT, "data", "manifest.json")))
    paths = {x["ticker"]: os.path.join(ROOT, x["page"]) for x in manifest}
    for ticker in sys.argv[1:]:
        path = paths.get(ticker)
        if not path or not os.path.exists(path):
            print(f"SKIP {ticker}: no widget file")
            continue
        fix(ticker, path)


if __name__ == "__main__":
    main()
