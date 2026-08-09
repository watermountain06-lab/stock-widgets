# Canonical Widget Spec

Single source of truth for the 6-tab structure every `widgets/{TICKER}_analysis_widget.html`
must follow. Reference implementation is `widgets/NVDA_analysis_widget.html` (updated
2026-08-08, superseding PM — see "PM → NVDA reference change" below), which is also the
structural contract `scripts/validate_widget.py` enforces. When this doc and
`progress_log.md`'s older "Codex Handoff Checklist" disagree, **this doc wins** — see
"Superseded guidance" at the bottom for what changed and why.

Use this doc, not NVDA's raw HTML, as the thing to read before building or fixing a widget.
Still copy NVDA's actual markup verbatim for anything not spelled out here (exact CSS, inline
styles, class names) — this doc describes *what* goes where, not full markup. The other 44
widgets have not been migrated to this NVDA-standard structure yet (2026-08-08) - both the old
PM-order and new NVDA-order validate, see `validate_widget.py`'s `val_contract_old`/`_new`.
Migrate a widget to the new structure when you're already touching it for another reason, not
as a standalone batch job.

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

1. Card: **분기 매출/순이익/영업이익률(OPM) 차트** (Chart.js, 8 quarters) — fixed to exactly this
   3-series set (매출 bar + 순이익 bar + OPM% line), not per-ticker variants. This was
   standardized 2026-08-08 after finding the fleet had drifted into inconsistent sets
   (GOOGL/META/MSFT plot 영업이익 instead of 순이익; JNJ plots EPS lines instead of a margin
   line; TSLA has no dollar-value series at all, just GM%/OPM%). The rationale for exactly
   these three: 영업이익 doesn't need its own bar because it's recoverable from 매출×OPM% once
   OPM is on the chart, so a dedicated 순이익 bar is more informative than a third $-bar. OPM
   was kept as the *only* margin line (not 매출총이익률 or 순이익률) because it isolates core
   operating profitability from both COGS-structure noise (매출총이익률) and one-time/tax noise
   (순이익률) — see `stock-refresh/SKILL.md`'s "손익계산서 표준 차트" section for the fuller
   design-discussion trail (bar count, line count, and why a dual-chart split was rejected).
   Load animation (added 2026-08-08): `renderFundChart()` creates the chart with every dataset
   at its own axis baseline (bars at 0, the OPM line at `y2`'s min) and `animation:false`, then
   on the next frame swaps in the real data and calls `chart.update()` with the actual
   animation config. This is a two-step create-then-update, **not** a top-level
   `animations: { y: { ... from ... } }` override — that literal pattern is the one
   `validate_widget.py` forbids as a "fly-in" anti-pattern. Plain Chart.js defaults were tried
   first and rejected: bars already grow correctly from 0, but the line snaps to its final
   shape almost instantly while the bars are still near-zero, so the completed line appears to
   float above unfinished bars — the "flying in" look the create-then-update fix eliminates by
   making every series start flat at its own baseline and rise together.
2. **6-box `grid-3` stat block** directly below the chart (NVDA standard, 2026-08-08 —
   supersedes the legacy 9-box PM grid, not yet migrated on the other 44 widgets). Kept exactly
   the boxes that are not already shown somewhere else on the page and dropped everything that
   duplicates the chart or the top ticker-summary row:
   - **Dropped** 매출/영업이익/순이익 (all three duplicate the #fund chart directly) and TTM
     매출 (duplicates the top ticker-summary row — 매출/EPS are shown there on a TTM basis).
   - **Kept**: 순이익률 (the one bottom-line margin figure not shown anywhere else — distinct
     from the chart's OPM, which stops at operating income and excludes tax/interest/other
     income), FCF (cash actually generated, not shown elsewhere), **Capex** (new box, added
     2026-08-08 — NVDA's own capital spending was completely absent from the widget; every
     other "capex" mention on the page is *hyperscaler* capex, i.e. NVDA's customers' spending,
     a different number entirely; FCF and Capex are shown as a pair since FCF = OCF − Capex),
     현금 및 단기투자 (balance-sheet cash position — 재무 건전성's 유동비율 uses this number
     but only ever shows the ratio, never the absolute figure), EPS (quarterly, distinct from
     the TTM EPS already in the top summary row), and 다음 실적 (calendar, no overlap with
     anything). Each box's `.stat-sub` line leads with a short axis tag (e.g. "현금창출력 ·",
     "미래 재투자 ·") so a reader can tell at a glance why each box exists and that none of the
     six repeat each other.
   - Data source: `scripts/fetch_financials.py` gained `operatingCashFlow` and `capex`
     concepts (`PaymentsToAcquirePropertyPlantAndEquipment` XBRL tag) for this change — verify
     any pulled Capex figure against FCF via OCF − Capex ≈ FCF as a sanity check before trusting
     it (this is how NVDA's own $1.8B Capex figure was confirmed against its existing $48.6B
     FCF box).
   - `scripts/audit_widgets.py`'s `check_kpi_count` accepts both 6 (NVDA) and 9 (legacy PM)
     stat-box counts; `validate_widget.py` does not check box count.
3. Card: **재무 건전성 — 안정성·활동성** (added 2026-08-08, replacing `#valuation`'s old
   `stage-grid` card in the same design pass) — directly below the KPI stat-box grid, before
   핵심 성장 동력. See "재무 건전성 card" subsection below for its internal structure and the underlying
   ratio formulas.
4. Card: **핵심 성장 동력** (3개) — `driver-item`/`driver-num`/`driver-title`/`driver-desc` numbered-circle style (NVDA's actual markup — this is the majority convention, 30/45 widgets). Optional CEO quote line above it: "분기 수치 · CEO 이름 "실제 발언(한국어 번역)"" — must be a real, WebSearch-verified quote, translated into Korean like the rest of the document.
5. Card: **핵심 투자 논리** — narrative paragraph, same text as the header `box-key`.
6. Card: **다음 실적 체크포인트** — "①②③④" checklist tied to real guidance numbers, not plain stat-boxes, each item separated by `<br>` inside one `<div>` (not run together with "→" or left as one unbroken paragraph — found unbroken on MSFT's first migration pass, 2026-08-09). Must be the *last* card in `#fund` (`validate_widget.py` enforces `fund` ending with 핵심투자논리 → 다음실적체크포인트).

### 재무 건전성 card (안정성·활동성)

Two sub-sections inside one card, per the 안정성/활동성 steps of the 재무제표 분석 프로세스
(하마터면 회계를 모르고 일할 뻔했다 — 손익계산서[수익성·성장성] → 재무상태표[안정성] →
크로스분석[활동성]; 수익성·성장성 is already covered by the #fund chart + KPI stat-box grid above, so this
card covers steps 3–4 only).

**Card shell is collapsible (added 2026-08-09, migrated to MSFT 2026-08-09)**: both sub-sections'
summary verdict stays visible by default; only the row-level detail collapses. **Each section's
toggle sits directly under that same section's summary — interleaved, not grouped** (2026-08-09
correction: an earlier version of this doc listed both summaries first and both toggles after,
which is what NVDA's file looked like mid-edit at one point but is *not* its final/correct state —
copying that stale doc wording produced exactly this bug on MSFT's first migration, caught only
by user review after publishing). Structure, top to bottom:

1. `.section-label` "안정성 — ..." + `.diag-summary` (안정성 verdict, always visible)
2. `.detail-toggle` "안정성 상세 — ..." → its own `.collapsible-body.collapsed` containing the 안정성 `.diag-list`
3. `.section-label` "활동성 — ..." + `.diag-summary` (or `.diag-summary.watch` if the trend verdict warrants it — see below; activity verdicts are not always `.watch`, MSFT's is plain green)
4. `.detail-toggle` "활동성 상세 — ..." → its own `.collapsible-body.collapsed` containing the 활동성 `.diag-list` + `.ccc-card`

Before migrating another widget, verify against NVDA's *actual current* markup
(`grep -n "section-label\|detail-toggle" widgets/NVDA_analysis_widget.html`), not against this
doc's prose alone — the doc can drift out of sync with the reference file, as it just did here.

**Two separate `.detail-toggle`s, not one shared toggle for the whole card** — an earlier pass
used a single toggle for both sub-sections' detail at once, and the user flagged that expanding
it merged 안정성 and 활동성 rows into one visually undifferentiated block. Each toggle's
`onclick="toggleCollapsible(this)"` operates on `header.nextElementSibling` only, so the two are
fully independent (expanding one doesn't affect the other). `toggleCollapsible()` also flips
`aria-expanded` and swaps the `.toggle-hint-text` label between "상세 보기"/"상세 숨기기" (or
"펼치기"/"접기" for the outer card-level toggle, if the whole card itself is also wrapped —
see `stock-refresh/SKILL.md`'s design-pass notes for why the *card-level* collapse was rejected
in favor of always-showing both verdicts and only collapsing detail).

**안정성** (`.diag-summary` + `.diag-list`/`.diag-row`) — a health-checkup-report layout, not a
bar/gauge (user-tested 2026-08-08: bar gauges were not legible to a lay reader at a glance).
One green summary banner ("종합 진단: {매우 안정적|주의 필요|...}") plus one `.diag-row` per
metric with a ✅/⚠️/❌ `.diag-badge`, not a percentage bar:

| 지표 | 공식 | 판정 기준 |
|---|---|---|
| 유동비율 | 유동자산 ÷ 유동부채 × 100 | 150%↑ 안정, 50%↓ 위험 |
| 당좌비율 | (유동자산−재고자산) ÷ 유동부채 × 100 | 100%↑ 양호 |
| 부채비율 | 부채 ÷ 자기자본 × 100 | 낮을수록 양호, 유동부채비율·차입금의존도와 함께 판단 |
| 차입금의존도 | (단기+장기차입금) ÷ 자산 × 100 | 30%↓ 양호 |
| 이자보상배율 | 영업이익 ÷ 이자비용 | 1 미만이면 잠재적 부실기업 명시 필수 |
| 총자산증가율 | (당기말 자산−전기말 자산) ÷ 전기말 자산 × 100 | 판정 배지 없이 `info` 참고용으로만 표시 (안정성이 아니라 성장성 지표) |

**활동성** (2026-08-09: switched from `.activity-grid`/`.act-card` icon-card grid to the same
`.diag-summary`/`.diag-list`/`.diag-row` layout 안정성 uses, plus the `.ccc-card` below it —
visual parity was a direct user request after the two sections looked structurally inconsistent
side by side. `.activity-grid`/`.act-card` CSS is still defined in NVDA's file but is dead/
superseded — don't copy it into a newly-migrated widget, use the diag-list pattern instead):

| 지표 | 공식 |
|---|---|
| 매출채권 회전율 | 매출액×2 ÷ (전기말+당기말 매출채권) |
| 재고자산 회전율 | 매출원가×2 ÷ (전기말+당기말 재고자산) |
| 매입채무 회전율 | 매입액×2 ÷ (전기말+당기말 매입채무) — 매입액이 직접 공시되지 않으면 매출원가+재고증가분으로 근사 |
| 각 회전기간 | 365 ÷ 해당 회전율 |
| 영업순환주기 | 매출채권 회전기간 + 재고자산 회전기간 |
| 현금창출주기 (CCC) | 영업순환주기 − 매입채무 지급기간 |

**CCC's own headline number is colored neutrally (`var(--gold)`), never red/green** — 활동성
has no universal pass/fail line the way 안정성 does; a shorter CCC ties up less cash, but what
counts as "short" is entirely industry-dependent (a semiconductor maker's CCC is structurally
longer than a software company's), so a red/green verdict on the day-count itself would be a
false claim the data doesn't support. Give the CCC card a one-line plain-language explanation
(e.g. "재고를 사서 판매 대금을 회수하기까지 N일이 걸리는데, 그중 M일은 매입채무로 버티고
나머지 X일은 회사가 직접 현금으로 메워야 하는 기간이다") instead of a good/bad label on the
number itself. (Exception: a genuinely negative CCC, e.g. AMZN — see `stock-refresh/SKILL.md`'s
2026-08-09 entry — is unambiguous and should be colored green, not neutral.)

**활동성 판정 기준 (added 2026-08-09) — trend-based, not a fixed threshold.** Unlike 안정성's
accounting-textbook cutoffs (150%, 30%, 1x — industry-agnostic), activity ratios have no universal
"good" value; a semiconductor maker's 3-4x inventory turnover is normal where a retailer's 10x+
is normal. Judge each 활동성 row by **direction and magnitude of change vs. the same TTM window
one year earlier**, computed from SEC EDGAR balance-sheet instants + quarterly revenue/COGS
(average-balance method — see `stock-refresh/SKILL.md`'s data-pipeline entry for the exact
computation and how it was validated against NVDA's existing, already-correct figures):

- `.diag-summary.watch` / `.diag-badge.watch` (amber, `var(--gold)`) — new badge tier alongside
  the existing `.safe` (green) and `.info` (gray), for "notably decelerated, worth watching, not
  alarming." Reserve for genuinely large swings (NVDA: inventory turnover -31.6%, CCC +33.7%),
  not routine quarter-to-quarter noise.
- **Interpret 매입채무 회전율 (AP turnover) direction opposite to AR/재고**: a falling AP
  turnover means the company is taking *longer* to pay suppliers, which is mild supplier-financed
  cash-flow relief for the company, not a warning sign — badge it `.info`, never `.watch`, even
  when the % change is as large as the AR/inventory swings. AR turnover and 재고자산 회전율
  falling both mean "collecting/selling slower," which is the actual thing worth flagging.
- Write the summary `.sub` line to name the *dominant driver* of the CCC change (e.g. "재고자산
  회전 둔화가 주된 원인, 매입채무 지급기간 확대가 일부 상쇄"), not just the headline delta —
  useful because CCC = 영업순환주기 − AP기간, so a CCC change can come from either side and the
  two sides often move in ways that partially offset.

Data source: `scripts/fetch_financials.py` was extended 2026-08-08 with the balance-sheet
concepts these ratios need (`currentAssets`, `currentLiabilities`, `inventory`,
`accountsReceivable`, `accountsPayable`, `totalLiabilities`, `shortTermDebt`, `longTermDebt`,
`costOfRevenue`, `interestExpense`) — none of these were pulled before. `interestExpense` in
particular can go stale on companies with negligible debt (NVDA's `InterestExpense` XBRL tag
stopped being populated after Q1 FY2024); the script now also tries
`InterestExpenseNonoperating` as a fallback. The trend-based 활동성 judgment above additionally
needs the **same instants and quarterly figures one year earlier** (prior-year TTM window) —
`fetch_financials.py` does not currently automate this second fetch; it was done by hand against
`data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` directly for NVDA (see SKILL.md).

## `#valuation` — 밸류에이션

Fixed 5-card order (`validate_widget.py`-enforced, do not reorder) — reduced from 6 to 5
2026-08-08 when the old `stage-grid` card was dropped (user's call: it only restated the same
5 multiples the 멀티플 5단계 평가 card above it and the 종합 밸류에이션 paragraph below it
*already* had to state independently per the rule in card 4 below — three restatements of the
same distribution was pure redundancy, not new information). Legacy widgets still on the old
6-card order (with `stage-grid` as card 3) remain valid until migrated — see
`validate_widget.py`'s `val_contract_old`.

1. **멀티플 5단계 평가** — 5 `val-item`s, each with `stage-badge stage-N` (1–5), a `val-fill` gauge (green→gold→red 3-stop gradient), and numeric `val-labels` (never generic "낮음/적정/높음"). **`val-fill` width is a fixed 5-position lookup by stage — `19%/38%/57%/76%/95%` for stage 1–5 — not a computed position on the low/mid/high scale** (confirmed fleet-wide 2026-08-09 after an earlier continuous-interpolation formula turned out to be a coincidental near-match, not the real mechanism; see `stock-refresh/SKILL.md`). Decide the stage qualitatively from where the value sits relative to low/mid/high, then look up the width — never compute it from the raw numbers. **The `mid`/"적정" reference value itself needs a stated source, not just a plausible-looking round number** — see `stock-refresh/SKILL.md`'s "멀티플 5단계 평가" methodology section (2026-08-09, revised after a 3-round Codex review): use a two-tier 핵심 앵커(core, same accounting basis + comparable business model only, included in the actual computed median/average) vs 참고 앵커(reference-only, cited but excluded from the calculation) system, and compute the real statistic rather than eyeballing a number that merely looks like a plausible median. An unsourced or miscalculated mid value is not just a documentation gap — this exact task got both the sourcing *and*, on a first attempt, the arithmetic wrong before a Codex review caught it. A metric's peer group can legitimately differ from the other 4 metrics' peer group within the same ticker (e.g. MSFT's PCR needing AI-capex-cycle context that its PER doesn't) — but that's a *second, clearly-labeled paragraph*, not a swapped core anchor; see the same doc's "Per-metric peer group" entry for the reasoning and the post-hoc-rationalization test to apply before ever doing this.

   **The per-item subtext is gone — sourcing/comparison content now lives in a clickable peer-chart panel, not inline** (2026-08-09): each `val-item` carries `data-metric="per|pbr|psr|pcr|evebitda"` + `onclick="selectMultiple(key)"` on the outer div, and clicking it swaps the adjacent card's chart + explanation to that metric (title, Chart.js bars, and the sourcing sentence + interpretation paragraph that used to be tiny 11px subtext). See `stock-refresh/SKILL.md`'s "Clickable 멀티플 5단계 ↔ peer-chart panel" entry for the full JS mechanism (`MULTIPLE_DATA` object, `renderMultipleChart`/`selectMultiple`) and two `validate_widget.py` regressions it's easy to trip on (the literal `class="val-item"` count check, and the literal `<div class="card-title">` match breaking if you put an `id` directly on that div instead of an inner `<span>`).
2. **peer 비교** — chart + one paragraph comparing the ticker to its named peer group.
3. **Per-Share 지표** (`per-share-grid`, 4 cards: EPS/BPS-or-매출/주/FCF-or-영업CF/주/DPS) — title states the share count and as-of quarter.
4. **종합 밸류에이션** — title format `종합 밸류에이션 <verdict-colored span>({verdict})</span> — {짧은 결론}`, followed by a `grid-2` of two boxes (`background:var(--bg3)`), **labels driven by the overall verdict, not hardcoded to "저평가"** (added 2026-08-09, generalizing NVDA's own card — NVDA happens to be 저평가 so its card already looked right, but the labels must flip for a 고평가 ticker instead of every widget copy-pasting NVDA's literal "저평가 근거" text):
   - **Left box, `{verdict} 근거`** — header color = the same 5-stage palette as the box-key verdict tag (`stage-refresh/SKILL.md`'s Format Conventions: 초저평가 `#2ecc71` / 저평가 `#27ae60` / 적정 `var(--gold)` / 고평가 `#e67e22` / 초고평가 `var(--red)`). Body lists the `val-item`s whose `stage-badge` agrees with the overall verdict direction (e.g. for a 저평가 verdict, the stage-1/2 items).
   - **Right box, `주의 요소`** (label itself doesn't change per verdict — it's always the countervailing side) — header color is a fixed neutral `var(--gold)` amber, **not** the ticker's own `--accent2` (NVDA's card used `--accent2` for this box, which is a per-file brand color — same cross-file inconsistency problem already flagged for the box-key tag; fix on sight when touching another widget's card, don't copy NVDA's `--accent2` literally). Body lists the `val-item`s whose `stage-badge` disagrees with the verdict (the minority-direction items) as the caveats.
   - `적정` verdict label: use `적정 판단 근거` for the left box (bare "적정 근거" reads oddly) — every other tier follows the plain `{verdict} 근거` pattern.
   - Content must state the same numbers and stage distribution as the 5 val-items in card 1 — this is where NVDA drifted out of sync before the stage-grid was dropped (2026-08-07 finding: the old stage-grid's summary cited different multiples and a wrong stage for PBR/PSR than the val-items actually showed). Regenerate this paragraph pair, don't hand-edit it, whenever the val-items or the overall verdict change.
5. **시나리오별 공정가치 분석** — 3 vertical `scenario-card`s (Bear/Base/Bull), never `grid-3`. Each states the driving assumption and a fair-value $ range vs. current price %.

The box-key/`#fund` 핵심 투자 논리 title's 5-tier verdict tag (`초저평가|저평가|적정|고평가|초고평가`)
is still derived by majority vote across these same 5 `val-item` `stage-badge`s directly — it
never depended on the `stage-grid` box existing, so removing that card doesn't change how the
tag gets picked. See `stock-refresh/SKILL.md`'s "Format conventions" section.

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

## PM → NVDA reference change (2026-08-08)

NVDA replaces PM as the widget scripts/docs treat as canonical, for a small, explicitly scoped
set of structural changes made incrementally across 2026-08-08 (the first two together in one
design pass with the user, mockups worked out via a claude.ai/design project; the last two in a
follow-up pass reducing #fund's overall density):

1. `#valuation`'s `stage-grid` card removed (6-card → 5-card valuation order).
2. `#fund` gained the **재무 건전성 — 안정성·활동성** card (in the slot the removed stage-grid's
   information effectively moved out of), and its chart was standardized to the fixed
   매출/순이익/OPM 3-series set.
3. `#fund`'s chart load animation changed from Chart.js defaults (line snaps in ahead of the
   still-growing bars) to a create-flat-then-update pattern so every series rises from its own
   baseline together — see `#fund` item 1 above for the mechanism.
4. `#fund`'s 9-box `grid-3` KPI grid trimmed to 6 boxes, dropping everything that duplicated the
   chart or the top ticker-summary row and adding a new Capex box — see `#fund` item 2 above for
   the full kept/dropped rationale.

Every *other* PM convention in this doc (candlestick SVG scaffolding, MA-row/zone-item markup,
tag-pills, box-key structure, 목표가 밴드 formula, etc.) is unaffected and still valid — this
is a small set of targeted changes, not a full reference-ticker rewrite. `scripts/validate_widget.py`
accepts both the old PM-order and the new NVDA-order (and `scripts/audit_widgets.py` accepts
both the old 9-box and new 6-box KPI count) so the other 44 widgets don't fail validation
outright; migrate each one to the NVDA order when it's next touched for another reason (per this
project's established stock-refresh pattern), not as a dedicated batch job.

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
