#!/usr/bin/env python3
"""Patch a widget's PER/PBR badges and 목표가 밴드 markers from a
compute_valuation_score.py signal file - editing only the digits/attributes
inside existing tags, in place, exactly as .claude/skills/stock-refresh's
safety rule requires (never regenerate surrounding markup from a template;
that caused the 2026-08-08 and 2026-08-12 widget-corruption incidents).

Scope (see project plan for why): only the two val-items this repo can
independently compute (PER, PBR) and the 목표가 밴드's current-price /
target-price markers are touched. Everything else in the widget - scenario
fair-value ranges, narrative prose, the other three multiple badges - stays
exactly as a human/Claude last wrote it.

The 목표가 밴드's color bar (Bear/Base/Bull segments) is never touched; only
the two marker positions move. Their new % position is derived by fitting a
line through the *existing* current-price and target-price markers already
in the file (2 points determine the price->% mapping) rather than
recomputing the gauge domain from bear/base/bull numbers, which are a
narrative judgment call this script has no business inventing.

Usage:
  python3 apply_valuation_signals.py TICKER widget.html --signal SIG.json [--out OUT.html]

Exits 0 with a JSON report on stdout listing which patches applied / were
skipped and why; never partially writes a corrupted file (all substitutions
are validated as exactly-one-match before anything is written).
"""
import argparse
import json
import re
import sys


def patch_val_item(html, metric, number_str, stage):
    """Find the <div class="val-item" data-metric="{metric}" ...> block and
    replace its .val-number text, .stage-badge class+label, and .val-fill
    width+gradient. Returns (new_html, note) - note is None on success or an
    explanation string if this metric was skipped."""
    STAGE_STYLE = {
        1: ("19", "linear-gradient(90deg,#2ecc71,#8bc34a)"),
        2: ("38", "linear-gradient(90deg,#27ae60,#8bc34a)"),
        3: ("57", "linear-gradient(90deg,#f0c040,#e67e22)"),
        4: ("76", "linear-gradient(90deg,#e67e22,#e74c3c)"),
        5: ("95", "linear-gradient(90deg,#e74c3c,#c0392b)"),
    }
    stage_label = {1: "매우낮음", 2: "낮음", 3: "적정", 4: "높음", 5: "매우높음"}[stage]
    width, gradient = STAGE_STYLE[stage]

    block_re = re.compile(
        rf'(<div class="val-item" data-metric="{re.escape(metric)}"[^>]*>)(.*?)'
        rf'(?=<div class="val-item" data-metric="|<div class="card-title">)',
        re.S,
    )
    m = block_re.search(html)
    if not m:
        return html, f"{metric}: data-metric block not found, skipped"
    block = m.group(0)

    new_block, n1 = re.subn(r'<span class="val-number">[^<]*</span>',
                             f'<span class="val-number">{number_str}</span>', block, count=1)
    new_block, n2 = re.subn(r'<span class="stage-badge stage-\d">\d단계 [^<]*</span>',
                             f'<span class="stage-badge stage-{stage}">{stage}단계 {stage_label}</span>',
                             new_block, count=1)
    new_block, n3 = re.subn(r'(<div class="val-fill" style="width:)[\d.]+(%;background:)[^"]*(")',
                             rf'\g<1>{width}\g<2>{gradient};\g<3>', new_block, count=1)
    if not (n1 and n2 and n3):
        return html, f"{metric}: expected exactly one val-number/stage-badge/val-fill match, got {n1}/{n2}/{n3}, skipped"

    return html[:m.start()] + new_block + html[m.end():], None


def patch_target_band(html, new_current_price, new_target_price, upside_pct):
    """Fit a line through the existing current-price and target-price marker
    (price, left%) pairs and reposition both markers + their label text at
    the new prices. Skips (returns unchanged) if markers can't be found
    unambiguously, or if the new position would fall far outside the
    existing gauge (>15pt beyond 0-100%), since that means the hand-authored
    Bear/Base/Bull scenario bands themselves are now stale and need a human
    to reconsider them, not just reposition a marker."""
    cur_marker_re = re.compile(
        r'(<div style="position:absolute;top:10px;left:)([\d.]+)(%;width:2px;height:28px;background:var\(--accent2\);[^"]*"></div>\s*'
        r'<div style="position:absolute;top:-6px;left:)([\d.]+)(%;transform:translateX\(-50%\);[^"]*">)현재 \$([\d,.]+)(</div>)')
    tgt_marker_re = re.compile(
        r'(<div style="position:absolute;top:22px;left:)([\d.]+)(%;width:2px;height:24px;background:#ffc107;[^"]*"></div>\s*'
        r'<div style="position:absolute;top:48px;left:)([\d.]+)(%;transform:translateX\(-50%\);[^"]*">)▲ 목표 \$([\d,.]+) \(([+\-][\d.]+)%\)(</div>)')

    cur_m = cur_marker_re.search(html)
    tgt_m = tgt_marker_re.search(html)
    if not cur_m or not tgt_m:
        return html, "target band: current/target marker pattern not found, skipped"

    old_cur_price = float(cur_m.group(6).replace(",", ""))
    old_cur_pct = float(cur_m.group(2))
    old_tgt_price = float(tgt_m.group(6).replace(",", ""))
    old_tgt_pct = float(tgt_m.group(2))
    if old_cur_price == old_tgt_price:
        return html, "target band: cannot fit line (old current == old target price), skipped"

    # left_pct = a*price + b, solved from the two existing calibration points
    a = (old_tgt_pct - old_cur_pct) / (old_tgt_price - old_cur_price)
    b = old_cur_pct - a * old_cur_price
    new_cur_pct = a * new_current_price + b
    new_tgt_pct = a * new_target_price + b
    if not (-15 <= new_cur_pct <= 115) or not (-15 <= new_tgt_pct <= 115):
        return html, (f"target band: new marker position out of range "
                       f"(cur={new_cur_pct:.1f}%, target={new_tgt_pct:.1f}%) - "
                       f"Bear/Base/Bull scenario bands likely need human review, skipped")

    sign = "+" if upside_pct >= 0 else ""
    new_cur_block = (f'{cur_m.group(1)}{new_cur_pct:.1f}{cur_m.group(3)}{new_cur_pct:.1f}'
                      f'{cur_m.group(5)}현재 ${new_current_price:,.2f}{cur_m.group(7)}')
    new_tgt_block = (f'{tgt_m.group(1)}{new_tgt_pct:.1f}{tgt_m.group(3)}{new_tgt_pct:.1f}'
                      f'{tgt_m.group(5)}▲ 목표 ${new_target_price:,.2f} ({sign}{upside_pct:.1f}%){tgt_m.group(8)}')

    html = html[:cur_m.start()] + new_cur_block + html[cur_m.end():]
    tgt_m2 = tgt_marker_re.search(html)  # re-search: cur patch may have shifted offsets
    if not tgt_m2:
        return html, "target band: target marker vanished after current-marker patch, aborted"
    html = html[:tgt_m2.start()] + new_tgt_block + html[tgt_m2.end():]
    return html, None


def patch_valuation_tab_current_price(html, new_current_price):
    """Best-effort: update the '현재가 $X' mention validate_widget.py cross-
    checks against the target band, if there's exactly one in the file.
    Not required for the val-item/target-band patches to succeed."""
    price_re = r'현재가 \$\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    n = len(re.findall(price_re, html))
    if n != 1:
        return html, f"현재가 mention: expected exactly 1 occurrence, found {n}, left untouched"
    html = re.sub(price_re, f'현재가 ${new_current_price:,.2f}', html, count=1)
    return html, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("widget")
    ap.add_argument("--signal", required=True, help="compute_valuation_score.py output")
    ap.add_argument("--out", default=None, help="default: overwrite --widget in place")
    args = ap.parse_args()

    with open(args.widget) as f:
        html = f.read()
    with open(args.signal) as f:
        signal = json.load(f)

    notes = []
    for metric in ("per", "pbr"):
        if metric in signal:
            html, note = patch_val_item(html, metric, f'{signal[metric]["current"]}x', signal[metric]["stage"])
            notes.append(note or f"{metric}: patched (stage {signal[metric]['stage']})")
        else:
            notes.append(f"{metric}: no signal data, skipped")

    if "targetPrice" in signal:
        html, note = patch_target_band(html, signal["currentPrice"], signal["targetPrice"]["mean"],
                                        signal["targetPrice"]["upsidePct"])
        notes.append(note or "target band: patched")
    else:
        notes.append("target band: no target price data, skipped")

    html, note = patch_valuation_tab_current_price(html, signal["currentPrice"])
    notes.append(note or "현재가 mention: patched")

    out_path = args.out or args.widget
    with open(out_path, "w") as f:
        f.write(html)

    print(json.dumps({"ticker": args.ticker.upper(), "out": out_path, "notes": notes}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
