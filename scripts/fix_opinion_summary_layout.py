#!/usr/bin/env python3
"""Convert 투자의견 요약 card's wrapper div from horizontal wrap to PM's
canonical stacked (flex-direction:column) layout.

Only touches widgets whose 투자의견 요약 wrapper matches the known
row-layout string exactly. Widgets using a different card design
entirely (consensus-bar + quote box, e.g. AMD/ASML/JPM) or missing the
card (BRK_B/LLY) are skipped and reported for manual handling.
"""
import re
import sys
from pathlib import Path

WIDGETS_DIR = Path(__file__).resolve().parent.parent / "widgets"

OLD = '<div style="display:flex;gap:14px;flex-wrap:wrap;font-size:13px;">'
NEW = '<div style="display:flex;flex-direction:column;gap:10px;font-size:13px;">'


def fix_file(path: Path) -> str:
    s = path.read_text(encoding="utf-8")
    idx = s.find("투자의견 요약")
    if idx == -1:
        return "SKIP: card missing"

    window_end = idx + 400
    window = s[idx:window_end]

    if "flex-direction:column" in window:
        return "SKIP: already stacked"

    if OLD not in window:
        return "SKIP: non-standard card markup (needs manual review)"

    new_window = window.replace(OLD, NEW, 1)
    new_s = s[:idx] + new_window + s[window_end:]

    if new_s.count("<div") != s.count("<div") or new_s.count("</div>") != s.count("</div>"):
        return "ABORT: div balance would change, not writing"

    path.write_text(new_s, encoding="utf-8")
    return "FIXED"


def main():
    tickers = sys.argv[1:]
    if tickers:
        files = [WIDGETS_DIR / f"{t}_analysis_widget.html" for t in tickers]
    else:
        files = sorted(WIDGETS_DIR.glob("*_analysis_widget.html"))

    results = {}
    for f in files:
        if not f.exists():
            results[f.name] = "SKIP: file not found"
            continue
        results[f.name] = fix_file(f)

    fixed = [k for k, v in results.items() if v == "FIXED"]
    skipped = [(k, v) for k, v in results.items() if v != "FIXED"]

    print(f"Fixed: {len(fixed)}")
    for k in fixed:
        print(f"  {k}")
    print(f"\nSkipped/needs review: {len(skipped)}")
    for k, v in skipped:
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
