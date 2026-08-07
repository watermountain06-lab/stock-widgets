#!/usr/bin/env python3
"""Compute the 목표가 밴드 (target price band) gauge geometry so the current-price
marker never drifts from the widget's actual current price again.

The gauge domain and left-padding formula were reverse-engineered from PM's
existing (correct) card: domain_min = bear_lo - (base_lo - bear_hi), domain_max =
bull_hi + (bull_lo - base_hi) -- i.e. each side is padded by its own adjacent
scenario gap. This matches the PM card's own stated range ("게이지 범위는
$150~260") and reproduces its already-correct segment widths and target-marker
position exactly.

Usage:
  python3 scripts/target_band_gauge.py \\
      --bear 165 180 --base 195 220 --bull 230 250 \\
      --current 188.05 --target 210

Prints the seven segment widths (%), the current-price and target-price marker
positions (%), and the current-vs-target upside percentage -- ready to drop
into the card's existing markup (see widgets/PM_analysis_widget.html for the
exact scaffold: 7 flex divs for the color bar, two marker/label pairs, one
narrative sentence with the domain and upside%).
"""
import argparse


def compute(bear, base, bull, current, target):
    bear_lo, bear_hi = bear
    base_lo, base_hi = base
    bull_lo, bull_hi = bull

    gap_left = base_lo - bear_hi
    gap_right = bull_lo - base_hi
    domain_min = bear_lo - gap_left
    domain_max = bull_hi + gap_right
    width = domain_max - domain_min

    def pct(lo, hi):
        return (hi - lo) / width * 100

    def marker_pct(price):
        return (price - domain_min) / width * 100

    segments = [
        pct(domain_min, bear_lo),
        pct(bear_lo, bear_hi),
        pct(bear_hi, base_lo),
        pct(base_lo, base_hi),
        pct(base_hi, bull_lo),
        pct(bull_lo, bull_hi),
        pct(bull_hi, domain_max),
    ]

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
    a = ap.parse_args()

    r = compute(a.bear, a.base, a.bull, a.current, a.target)

    labels = ["pad-left", "bear", "gap", "base", "gap", "bull", "pad-right"]
    print(f"게이지 범위: ${r['domain_min']:.0f}~{r['domain_max']:.0f}")
    print()
    print("색상바 7분할 (width%):")
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
