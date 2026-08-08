#!/usr/bin/env python3
"""Wrap the ma-val/ma-status pair in each 이동평균선 현황 row with a
display:flex;gap:10px container, matching the convention already used
by about half the widgets (e.g. PM/GE). Fixes cramped spacing where
the price and status badge render with no gap between them.

Two cases exist in the wild:
  1. "never wrapped": <span ma-val>..</span><span ma-status>..</span></div>
     - one trailing </div> (closes ma-row only). Self-contained fix:
       add matching open+close wrapper divs around the span pair.
  2. "broken by refresh regression": same span pair but followed by
     </div></div></div> (3 trailing closes) - a leftover from a widget
     that HAD the double-wrap fix applied, then had an automated
     refresh script regenerate the row using the old unwrapped
     template, stripping the two wrapper <div> opens but leaving their
     closing tags in place (real div-count corruption, confirmed via
     git history on AAPL/AMZN/GOOGL/META/MSFT). Fix: add ONLY the two
     opening wrapper divs before the span pair - the 3 pre-existing
     closes already correctly account for wrapper+wrapper+ma-row once
     the opens are restored. Adding new closes here would double-break it.
"""
import re
import sys
from pathlib import Path

WIDGETS_DIR = Path(__file__).resolve().parent.parent / "widgets"

WRAP_OPEN = (
    '<div style="display:flex;align-items:center;gap:10px;">'
    '<div style="display:flex;align-items:center;gap:10px;">'
)
WRAP_CLOSE = "</div></div>"

# case 2 first (more specific: pair + 3 trailing closes)
PATTERN_BROKEN = re.compile(
    r'<span class="ma-val">([^<]*)</span><span class="ma-status ([^"]*)">([^<]*)</span>'
    r"(?=</div></div></div>)"
)
PATTERN_NORMAL = re.compile(
    r'<span class="ma-val">([^<]*)</span><span class="ma-status ([^"]*)">([^<]*)</span>'
    r"(?!</div></div>)"
)


def fix_file(path: Path) -> str:
    s = path.read_text(encoding="utf-8")
    before_open = s.count("<div")
    before_close = s.count("</div>")

    n_broken = 0
    n_normal = 0

    def repl_broken(m):
        nonlocal n_broken
        n_broken += 1
        val, status_cls, status_txt = m.group(1), m.group(2), m.group(3)
        return (
            f"{WRAP_OPEN}"
            f'<span class="ma-val">{val}</span>'
            f'<span class="ma-status {status_cls}">{status_txt}</span>'
        )

    def repl_normal(m):
        nonlocal n_normal
        n_normal += 1
        val, status_cls, status_txt = m.group(1), m.group(2), m.group(3)
        return (
            f"{WRAP_OPEN}"
            f'<span class="ma-val">{val}</span>'
            f'<span class="ma-status {status_cls}">{status_txt}</span>'
            f"{WRAP_CLOSE}"
        )

    s2 = PATTERN_BROKEN.sub(repl_broken, s)
    new_s = PATTERN_NORMAL.sub(repl_normal, s2)

    if n_broken == 0 and n_normal == 0:
        return "SKIP: no unwrapped ma-val/ma-status pairs found"

    after_open = new_s.count("<div")
    after_close = new_s.count("</div>")
    expect_open_delta = n_broken * 2 + n_normal * 2
    expect_close_delta = n_normal * 2
    if (after_open - before_open) != expect_open_delta or (
        after_close - before_close
    ) != expect_close_delta:
        return (
            f"ABORT: div balance mismatch (broken={n_broken} normal={n_normal}, "
            f"open_delta={after_open - before_open} close_delta={after_close - before_close})"
        )

    path.write_text(new_s, encoding="utf-8")
    return f"FIXED (broken-regression={n_broken}, never-wrapped={n_normal})"


def main():
    tickers = sys.argv[1:]
    if tickers:
        files = [WIDGETS_DIR / f"{t}_analysis_widget.html" for t in tickers]
    else:
        files = sorted(WIDGETS_DIR.glob("*_analysis_widget.html"))

    for f in files:
        if not f.exists():
            print(f"{f.name}: SKIP: file not found")
            continue
        print(f"{f.name}: {fix_file(f)}")


if __name__ == "__main__":
    main()
