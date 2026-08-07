#!/usr/bin/env python3
"""Compute the 목표가 밴드 (target price band) gauge geometry so the current-price
marker never drifts from the widget's actual current price again.

Two markup conventions exist in the repo - check which one a widget actually
uses (count the flex divs in its color bar) before picking a mode:

- PM-style, 7 segments (pad-left/bear/gap/base/gap/bull/pad-right): domain_min =
  bear_lo - (base_lo - bear_hi), domain_max = bull_hi + (bull_lo - base_hi) --
  each side padded by its own adjacent scenario gap. This is the default here.
- CAT-style, 5 segments (bear/gap/base/gap/bull, no end padding): domain is
  just [bear_lo, bull_hi]. Pass --no-pad for this one. (CAT's own card was
  built this way; using the 7-segment default on it silently misplaces the
  current-price marker relative to its own color bar - caught 2026-08-07.)

Usage:
  python3 scripts/target_band_gauge.py \\
      --bear 165 180 --base 195 220 --bull 230 250 \\
      --current 188.05 --target 210 [--no-pad]

Prints the segment widths (%), the current-price and target-price marker
positions (%), and the current-vs-target upside percentage -- ready to drop
into the card's existing markup (see widgets/PM_analysis_widget.html for the
7-segment scaffold, widgets/CAT_analysis_widget.html for the 5-segment one).
"""
import argparse


def compute(bear, base, bull, current, target, pad=True):
    bear_lo, bear_hi = bear
    base_lo, base_hi = base
    bull_lo, bull_hi = bull

    if pad:
        gap_left = base_lo - bear_hi
        gap_right = bull_lo - base_hi
        domain_min = bear_lo - gap_left
        domain_max = bull_hi + gap_right
    else:
        domain_min = bear_lo
        domain_max = bull_hi
    width = domain_max - domain_min

    def pct(lo, hi):
        return (hi - lo) / width * 100

    def marker_pct(price):
        return (price - domain_min) / width * 100

    segments = []
    if pad:
        segments.append(pct(domain_min, bear_lo))
    segments += [
        pct(bear_lo, bear_hi),
        pct(bear_hi, base_lo),
        pct(base_lo, base_hi),
        pct(base_hi, bull_lo),
        pct(bull_lo, bull_hi),
    ]
    if pad:
        segments.append(pct(bull_hi, domain_max))

    return {
        "domain_min": domain_min,
        "domain_max": domain_max,
        "segments_pct": segments,
        "current_marker_pct": marker_pct(current),
        "target_marker_pct": marker_pct(target),
        "upside_pct": (target - current) / current * 100,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bear", type=float, nargs=2, required=True, metavar=("LO", "HI"))
    ap.add_argument("--base", type=float, nargs=2, required=True, metavar=("LO", "HI"))
    ap.add_argument("--bull", type=float, nargs=2, required=True, metavar=("LO", "HI"))
    ap.add_argument("--current", type=float, required=True)
    ap.add_argument("--target", type=float, required=True)
    ap.add_argument("--no-pad", action="store_true", help="CAT-style 5-segment domain (no pad-left/pad-right); default is PM-style 7-segment padded domain")
    a = ap.parse_args()

    pad = not a.no_pad
    r = compute(a.bear, a.base, a.bull, a.current, a.target, pad=pad)

    labels = (["pad-left"] if pad else []) + ["bear", "gap", "base", "gap", "bull"] + (["pad-right"] if pad else [])
    print(f"게이지 범위: ${r['domain_min']:.0f}~{r['domain_max']:.0f}")
    print()
    print(f"색상바 {len(labels)}분할 (width%):")
    for label, seg in zip(labels, r["segments_pct"]):
        print(f"  {label:10s} {seg:5.1f}%")
    print()
    print(f"현재가 마커 left: {r['current_marker_pct']:.1f}%   (현재 ${a.current:.2f})")
    print(f"목표가 마커 left: {r['target_marker_pct']:.1f}%   (▲ 목표 ${a.target:.2f})")
    print()
    sign = "+" if r["upside_pct"] >= 0 else ""
    print(f"평균 목표가 ${a.target:.2f}은 현재가 대비 {sign}{r['upside_pct']:.1f}%")


if __name__ == "__main__":
    main()
