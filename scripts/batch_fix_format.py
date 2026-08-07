#!/usr/bin/env python3
"""Apply the purely mechanical format fixes from audit_widgets.py to one or
more widgets in place. Every fix here is a structural/CSS transformation that
needs no per-company research or judgment call - see
.claude/skills/stock-refresh/SKILL.md for what each one is and why.

Fixes applied (each is a no-op if the widget already has it):
  - max-width:1100px + centered margin on today-banner/header/nav/section/disclaimer
  - --gold CSS var defined (if var(--gold) is used but undefined)
  - Bull/Bear bb-icon triangles colored via var(--bull)/var(--bear)
  - MA-row: wrap .ma-val + .ma-status together so price sits left of the badge
  - 시계열 뉴스 timeline reordered newest-first
  - 알파/베타 US-tab labels given a short inline explanation

Does NOT touch: box-key content, 핵심 투자 논리 verdict tag, 목표가 밴드 price
sync, KPI/quarter counts, 핵심가격대 zone-val colors (too few instances to be
worth a general rule - fix those by hand) - all of those need real content or
per-widget judgment.

Usage:
  python3 scripts/batch_fix_format.py TICKER [TICKER ...]
  python3 scripts/batch_fix_format.py --all
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDGETS_DIR = os.path.join(ROOT, "widgets")


def fix_margin_for_maxwidth(block):
    """Given a CSS rule body (the part between { }), ensure max-width:1100px
    and a centered margin are present, preserving any existing vertical
    margin values."""
    if "max-width" in block:
        return block
    m = re.search(r"margin\s*:\s*([^;]+);", block)
    if m:
        parts = m.group(1).split()
        if len(parts) == 1:
            new_margin = f"{parts[0]} auto"
        elif len(parts) == 2:
            new_margin = f"{parts[0]} auto"
        elif len(parts) == 3:
            new_margin = f"{parts[0]} auto {parts[2]}"
        else:
            new_margin = f"{parts[0]} auto {parts[2]} auto"
        new_block = block[: m.start()] + f"margin: {new_margin};" + block[m.end() :]
        new_block = new_block.rstrip()
        if not new_block.endswith(";"):
            new_block += ";"
        new_block += " max-width: 1100px;"
        return new_block
    b = block.rstrip()
    if not b.endswith(";"):
        b += ";"
    return b + " max-width: 1100px; margin: 0 auto;"


def apply_max_width(s):
    for name in ["today-banner", "header", "nav", "section", "disclaimer"]:
        m = re.search(rf"(\.{re.escape(name)}\s*{{)(.*?)(}})", s, re.S)
        if not m:
            continue
        new_body = fix_margin_for_maxwidth(m.group(2))
        if new_body != m.group(2):
            s = s[: m.start()] + m.group(1) + new_body + m.group(3) + s[m.end() :]
    return s


def apply_gold_var(s):
    if "var(--gold)" not in s or re.search(r"--gold\s*:", s):
        return s
    m = re.search(r"(--red\s*:\s*#[0-9a-fA-F]{3,6}\s*;)", s)
    if m:
        return s[: m.end()] + " --gold: #f0c040;" + s[m.end() :]
    return s


def apply_bull_bear_colors(s):
    s = re.sub(
        r'<span class="bb-icon">▲</span>',
        '<span class="bb-icon" style="color:var(--bull);">▲</span>',
        s,
    )
    s = re.sub(
        r'<span class="bb-icon">▼</span>',
        '<span class="bb-icon" style="color:var(--bear);">▼</span>',
        s,
    )
    return s


def apply_ma_row_layout(s):
    def wrap(m):
        return (
            '<div style="display:flex;align-items:center;gap:10px;">'
            + m.group(1)
            + m.group(2)
            + "</div>"
        )

    return re.sub(
        r'(<span class="ma-val">[^<]*</span>)(<span class="ma-status[^"]*">[^<]*</span>)',
        wrap,
        s,
    )


def split_top_level(text, class_name):
    """Split `text` into chunks starting at each <div class="{class_name}">,
    using div-depth counting so nested divs inside each chunk don't confuse
    the split. Returns (prefix_before_first_match, [chunk, chunk, ...]).
    Whitespace between chunks (indentation/newlines in the source) is
    dropped rather than preserved - harmless for block-level divs."""
    marker = f'<div class="{class_name}">'
    first = text.find(marker)
    if first == -1:
        return text, []
    prefix = text[:first]
    chunks = []
    pos = first
    while True:
        idx = text.find(marker, pos)
        if idx == -1:
            break
        depth = 1
        j = idx + len("<div")
        while depth > 0 and j < len(text):
            nxt_open = text.find("<div", j)
            nxt_close = text.find("</div>", j)
            if nxt_close == -1:
                j = len(text)
                break
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                j = nxt_open + 4
            else:
                depth -= 1
                j = nxt_close + 6
        chunks.append(text[idx:j])
        pos = j
    return prefix, chunks


def apply_news_order(s):
    news_start = s.find('id="news"')
    if news_start == -1:
        return s
    timeline_marker = '<div class="timeline">'
    tl_start = s.find(timeline_marker, news_start)
    if tl_start == -1:
        return s
    body_start = tl_start + len(timeline_marker)
    close_marker = "</div>"
    depth = 1
    j = body_start
    while depth > 0 and j < len(s):
        nxt_open = s.find("<div", j)
        nxt_close = s.find("</div>", j)
        if nxt_close == -1:
            return s
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            j = nxt_open + 4
        else:
            depth -= 1
            j = nxt_close + 6
    tl_end = j - len(close_marker)
    body = s[body_start:tl_end]
    prefix, items = split_top_level(body, "tl-item")
    if len(items) < 2:
        return s

    def key(item):
        dm = re.search(r'<div class="tl-date">([^<]+)</div>', item)
        if not dm:
            return (0, 0, 0)
        m = re.search(r"(\d{4})년\s*(\d{1,2})(?:~\d{1,2})?월(?:\s*(\d{1,2})일)?", dm.group(1))
        if not m:
            return (0, 0, 0)
        y, mo, day = m.groups()
        return (int(y), int(mo), int(day or 15))

    keys = [key(it) for it in items]
    if keys == sorted(keys, reverse=True):
        return s
    order = sorted(range(len(items)), key=lambda i: keys[i], reverse=True)
    new_body = prefix + "".join(items[i] for i in order)
    return s[:body_start] + new_body + s[tl_end:]


def apply_alpha_beta_labels(s):
    def alpha_sub(m):
        if "(" in m.group(0):
            return m.group(0)
        return m.group(1) + "알파 (S&amp;P 500 대비 초과수익률)" + m.group(2)

    s = re.sub(
        r'(<div class="stat-label">)알파[^<]*(</div>)',
        alpha_sub,
        s,
    )

    def beta_sub(m):
        whole = m.group(0)
        if "(" in m.group(0):
            return whole
        tail = s[m.end() : m.end() + 200]
        vm = re.search(r'class="zone-val"[^>]*>\s*([\d.]+)', tail)
        beta_val = float(vm.group(1)) if vm else None
        if beta_val is not None and beta_val < 1:
            expl = "1보다 낮으면 덜 흔들림"
        else:
            expl = "1보다 높으면 더 흔들림"
        return m.group(1) + f"베타 (시장 대비 주가 변동성, {expl})" + m.group(2)

    s = re.sub(
        r'(<span class="zone-label">)베타(</span>)',
        beta_sub,
        s,
    )
    return s


FIXES = [
    apply_max_width,
    apply_gold_var,
    apply_bull_bear_colors,
    apply_ma_row_layout,
    apply_news_order,
    apply_alpha_beta_labels,
]


def load_manifest_tickers():
    manifest_path = os.path.join(ROOT, "data", "manifest.json")
    with open(manifest_path) as f:
        m = json.load(f)
    return {x["ticker"]: os.path.join(ROOT, x["page"]) for x in m}


def main():
    if not sys.argv[1:]:
        print(__doc__)
        return
    ticker_paths = load_manifest_tickers()
    if sys.argv[1] == "--all":
        targets = sorted(ticker_paths.keys())
    else:
        targets = sys.argv[1:]

    for ticker in targets:
        path = ticker_paths.get(ticker)
        if not path or not os.path.exists(path):
            print(f"SKIP {ticker}: no widget file")
            continue
        s = open(path).read()
        original = s
        for fix in FIXES:
            s = fix(s)
        if s != original:
            open(path, "w").write(s)
            print(f"FIXED {ticker}")
        else:
            print(f"CLEAN {ticker} (no mechanical fixes needed)")


if __name__ == "__main__":
    main()
