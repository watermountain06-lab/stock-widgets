# Canonical Widget Spec

Single source of truth for the 6-tab structure every `widgets/{TICKER}_analysis_widget.html`
must follow. Extracted from `widgets/PM_analysis_widget.html` (2026-08-07), which is also the
structural contract `scripts/validate_widget.py` enforces. When this doc and
`progress_log.md`'s older "Codex Handoff Checklist" disagree, **this doc wins** — see
"Superseded guidance" at the bottom for what changed and why.

Use this doc, not PM's raw HTML, as the thing to read before building or fixing a widget.
Still copy PM's actual markup verbatim for anything not spelled out here (exact CSS, inline
styles, class names) — this doc describes *what* goes where, not full markup.

## Common header (outside the 6 tabs)

- `back-bar`: brand link back to `index.html` (left) + bidirectional rank-neighbor nav (`◀ PREV` / `NEXT ▶`, right). Every publish of a new ticker must patch both rank-neighbor widgets' nav, not just the new file.
- `today-banner`: one-line latest-earnings/news flag, only shown when there's something dated and current.
- `header`: ticker badge + exchange/sector, company name + one-line description, price block (current price, day change %, 52-week range), 6-item `header-meta` grid (시가총액, 섹터, 최근분기 매출, 핵심 지표, EPS, 배당수익률 — the middle two vary by business model).
- `box-key`: one restated "핵심 투자 논리" line, mirrors the `#fund` tab's card of the same name. Title carries a colored verdict tag from the 5-tier scale `(초저평가|저평가|적정|고평가|초고평가)` — see `stock-refresh/SKILL.md`'s "Format conventions" section for the color mapping (2026-08-08: expanded from the original 3-tier 고평가/적정/저평가 set to match the 5-stage `stage-badge` system already used in `#valuation`).

**Every price shown anywhere in the file must trace back to the same number** (see "목표가 밴드 가격 동기화" below) — this was the PM bug fixed 2026-08-07.

## Tab order (fixed): `tech` → `fund` → `valuation` → `us` → `news` → `invest`

## `#tech` — 기술적 분석

1. Candlestick chart: period toggle (1개월/3개월/6개월/1년) + MA5/20/60/120 toggle buttons. **Each MA button needs `style="color:var(--maN);border-color:var(--maN)"` inline** — otherwise all four render gray and disconnect visually from the correctly-colored chart lines.
2. 52주 최저→최고→현재 one-liner below the chart.
3. Card: **핵심 가격대** — `zone-list`, 5 rows: 52주 최고(저항선) → 현재가(현재) → MA120(지지선) → 52주 최저(강지지) → 52주 수익률.
4. Card: **이동평균선 현황** — 4 `ma-row`s (MA5/20/60/120), each `.ma-name` needs a `<span class="ma-dot" style="background:var(--maN)">` plus a period label ("MA5 (단기)" etc. — PM omits the period label; add it for new widgets). Summary box below explaining the current alignment in plain language (정배열/역배열/혼조 + which MAs price is above/below), computed correctly from the real numbers, not templated.
5. Card: **구간별 패턴 분석** — `grid-4`, 4 dated periods (1개월/3개월/6개월/1년), each showing start→end price and %.
6. Tag-pills row (end of tab, outside any card) — 6 colored `<span>` badges, roughly 3 positive facts + 1 upcoming-earnings date + 2 risk flags. Raw inline-style spans (`background:rgba(...);color:var(--green/red/gold)`) copied from PM — **do not** reuse `.zone-tag`/`tag-support`/`tag-resist`/`tag-current`, those classes have no yellow/gold variant so an "upcoming" pill silently loses its color.

## `#fund` — 기본적 분석

1. Card: **분기 매출/영업이익/OPM 차트** (or 매출·순이익·EPS depending on business — Chart.js bar/line, 8 quarters). Net income as its own series from the start, not retrofitted later.
2. **9-box `grid-3` stat block** directly below the chart — one dense grid (revenue, operating income/net income, EPS, margin, prior-FY revenue, prior-FY net income, prior-FY EPS, shareholder-return/cashflow figure, next-earnings date), not split into a smaller grid plus a separate "사업 구성" card.
3. Card: **핵심 성장 동력** (3개) — `driver-item`/`driver-num`/`driver-title`/`driver-desc` numbered-circle style (PM's actual markup — this is the majority convention, 30/45 widgets). Optional CEO quote line above it: "분기 수치 · CEO 이름 "실제 발언(한국어 번역)"" — must be a real, WebSearch-verified quote, translated into Korean like the rest of the document.
4. Card: **핵심 투자 논리** — narrative paragraph, same text as the header `box-key`.
5. Card: **다음 실적 체크포인트** — "①②③④" checklist tied to real guidance numbers, not plain stat-boxes. Must be the *last* card in `#fund` (`validate_widget.py` enforces `fund` ending with 핵심투자논리 → 다음실적체크포인트).

## `#valuation` — 밸류에이션

Fixed 6-card order (`validate_widget.py`-enforced, do not reorder):

1. **멀티플 5단계 평가** — 5 `val-item`s, each with `stage-badge stage-N` (1–5), a `val-fill` gauge (green→gold→red 3-stop gradient, width = position on the low/mid/high scale), and numeric `val-labels` (never generic "낮음/적정/높음").
2. **peer 비교** — chart + one paragraph comparing the ticker to its named peer group.
3. **밸류에이션 5단계** (`.stage-grid`, exactly one per widget) — 5 mini boxes (매우저평가/저평가/적정/고평가/매우고평가), each metric's name tagged into the box matching its own `stage-badge`. Summary sentence below **must restate the same numbers and stages as the 5 val-items above it** — this is where NVDA drifted out of sync (2026-08-07 finding: summary cited different multiples and a wrong stage for PBR/PSR than the val-items actually showed). Regenerate this sentence, don't hand-edit it, whenever the val-items change.
4. **Per-Share 지표** (`per-share-grid`, 4 cards: EPS/BPS-or-매출/주/FCF-or-영업CF/주/DPS) — title states the share count and as-of quarter.
5. **종합 밸류에이션** — one narrative paragraph. Title format: `종합 밸류에이션 — {짧은 결론}`. Content must be consistent with card 3's stage distribution (same rule as above).
6. **시나리오별 공정가치 분석** — 3 vertical `scenario-card`s (Bear/Base/Bull), never `grid-3`. Each states the driving assumption and a fair-value $ range vs. current price %.

## `#us` — US 특화

- `rel-container` (not `.card`): **S&P 500 대비 상대 수익률** — `grid-3` (자사 52주 수익률/S&P500 52주 수익률/알파) + `zone-list` (S&P500 내 비중, 베타).
- Exactly 2 further dense cards, ticker-specific (not a fixed title contract — content should be whatever US-market-relevant story matters most for that company: e.g. PM uses 제품 판매 현황 + 제품 믹스 차트; other tickers might use 정책 리스크 + 경쟁 구도). `data-us-visual="chart"` on the section tag requires an actual `<canvas>`/`<svg>`/`.us-visual`; use `data-us-visual="not-applicable"` + a `US_VISUAL_EXCEPTION:` comment only when a chart genuinely doesn't apply.

## `#news` — 시계열 뉴스

- Legend row: `--event-major` (sky blue, default dot) / `--event-neutral` (yellow, `.tl-dot.neutral`) / `.tl-dot.green` positive / `.tl-dot.red` negative. Never ad-hoc `.tl-dot.blue/orange/teal/yellow`, never the ticker's own `--accent`/`--accent2`.
- At least 5 `tl-item`s, real third-party news coverage (not just IR press releases — mix in analyst commentary, earnings-call coverage, market news). Every item needs a working link, `target="_blank" rel="noopener"`, and label text exactly `관련 뉴스 보기 (사이트명) →`.

## `#invest` — 투자 포인트

Fixed 4-block order:

1. **Bull/Bear box** (`bb-box` × 2, `bb-item` × 5 each).
2. **목표가 밴드** — the single most error-prone card. See formula below; never hand-type the gauge percentages again.
3. **5개 분석 종합** — 5-row `zone-list` (📈기술적/📊펀더멘털/⚖️밸류에이션/🇺🇸US/📰뉴스), not a paragraph.
4. **투자의견 요약** — simple flex row (다음실적일 · 투자의견 비중 · 목표주가+상승여력% · 한줄결론), not a 4-row zone-list.

### 목표가 밴드 가격 동기화 (critical, 2026-08-07 fix)

The gauge's "현재가" marker position was historically hand-typed and drifted out of sync with
the real current price every time the widget's price data was refreshed (found stale in PM, NVDA,
GOOGL, AAPL, JNJ — likely most/all widgets). **Always compute it, never type it by hand:**

```
python3 scripts/target_band_gauge.py \
    --bear BEAR_LO BEAR_HI --base BASE_LO BASE_HI --bull BULL_LO BULL_HI \
    --current CURRENT_PRICE --target TARGET_PRICE
```

This prints the 7 color-bar segment widths, both marker `left:%` positions, and the "현재가 대비
+N%" upside line — apply all of them together. The gauge domain is
`[bear_lo − (base_lo − bear_hi), bull_hi + (bull_lo − base_hi)]` (each side padded by its own
adjacent scenario gap) — this reproduces PM's original, correct segment widths exactly.
Cross-check the input current price against the widget's own last `{TICKER}_DAILY` bar close, not
just whatever number is already in the file.

## Known, acceptable exceptions

Recently-listed tickers (SPCX, SKHY-class IPOs with <252 trading days of history) will
legitimately fail the 252-length `DAILY`/`MAn` array checks and can't show a real MA120 or
full 1-year 구간별 패턴 분석. Don't force-fill these — show the real, shorter history and say so,
per `progress_log.md`'s existing "recent IPOs/ADRs" note. Fill in everything else that doesn't
depend on 1-year history.

## Superseded guidance (progress_log.md "Codex Handoff Checklist", 2026-07-22)

Two points in that checklist no longer match PM's actual (later) structure and should be treated
as historical, not current:

- It says 핵심 성장 동력 must be raw `grid-3` divs, "not driver-item style." PM and 30/45 existing
  widgets use `driver-item`/`driver-num` — that's the real majority convention now. Use `driver-item`.
- It says 종합 밸류에이션 "must come after scenario cards, not right after stage-grid." PM's actual
  order (and `validate_widget.py`'s enforced order) is 종합 밸류에이션 *before* 시나리오별 공정가치.
  Use the order in this doc's `#valuation` section above.

Both of these checklist notes were written when JNJ, not PM, was the reference implementation;
PM superseded JNJ as the canonical contract at some later point without the checklist being
updated. This doc reconciles that drift.
