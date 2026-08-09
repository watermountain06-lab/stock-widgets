---
name: stock-refresh
description: Refresh or repair an existing stock-widgets ticker card - from a scoped fix (one tab, one bug) to a full earnings-quarter synchronization. Use when the user says "stock-refresh", "이 위젯 업데이트해줘", asks to bring a card current after new earnings, requests a specific tab/section fixed on an existing ticker, or wants a fact-check/format-consistency pass on a widget already in widgets/.
---

# Stock Refresh

Work in `/Users/watermountain/Workspace/stock-widgets`. Never touch `widgets/kr_test/` (separate KR pipeline) unless explicitly asked.

## Single source of truth

Read `docs/canonical_widget_spec.md` first - it is the reconciled, current spec for all 6 tabs (order, card titles, formatting rules), built from PM's actual structure and already resolves two places where `progress_log.md`'s older notes had drifted. Don't treat PM's raw HTML or `progress_log.md` as competing specs; when they conflict with the canonical doc, the doc wins. Use PM's HTML to copy exact markup/CSS scaffolding the doc references but doesn't fully reproduce (e.g. the candlestick SVG renderer) - except for `#fund`'s chart and its new 재무 건전성 card, and `#valuation`'s card count, where **NVDA is the reference instead** (2026-08-08, see the doc's "PM → NVDA reference change" section). Most widgets, including PM itself, haven't been migrated to the NVDA order yet - that's expected, migrate opportunistically per the "Pick a mode" section below, not as a batch job.

## Pick a mode

- **Scoped repair**: user names a specific tab, card, or defect. Touch only that surface plus anything it makes inconsistent (e.g. fixing a target price also means fixing the upside % derived from it). Don't re-fetch price/financial data just because the skill was invoked.
- **Full synchronization**: user asks to bring a card current after a new earnings release, or gives no narrower scope. Every price-dependent and earnings-dependent layer must move together - a partial refresh that updates the fund tab but leaves valuation/target-band on the old quarter is the single most common failure mode seen so far (caught on both PM and CAT in the same session). Never ship one without the other.

## Data fetching order

1. **Standard financials**: `python3 scripts/fetch_financials.py TICKER --sp500 data/sp500.json` - pulls revenue, operating income, net income, diluted EPS, equity, cash, dividend/share directly from SEC EDGAR XBRL (no API key). This is the primary source; prefer it over WebSearch for anything it covers. Verified against real Q2 2026 CAT data and matched exactly.
2. **Price/technicals**: `python3 scripts/fetch_price.py` for daily OHLCV - use `range=2y`, compute MAs on the full lookback, then keep exactly the latest 252 completed trading days (exclude an incomplete current-day bar).
3. **Everything the scripts don't cover** - segment/geographic breakdowns (e.g. a Construction Industries North America split), backlog, forward guidance, CEO quotes, analyst consensus, news - use WebSearch/WebFetch against primary or high-quality sources:
   - Analyst consensus: `stockanalysis.com/stocks/{ticker}/forecast/` (average target, analyst count, buy/hold/sell breakdown). Never fabricate a count or average - if only 1-2 firm targets are confirmable, show them individually with firm + rating instead.
   - CEO quotes: verify through a real transcript/release, translate to Korean, never leave English untranslated.
   - News links: real third-party coverage or the primary filing/release, never a generic IR landing page repeated across events, never a bare category/tag page.
4. Cross-check whatever a script or search returns against the file's own last daily-bar close and against other verified numbers before writing (e.g. net income / diluted shares should reproduce the reported EPS).

## The recurring bug: stale price/quarter propagation

A single "current price" or "latest quarter" gets echoed in far more places than expected. Before calling a refresh done, grep the **whole file**, not just the tab you edited, for every place the old value could still be hiding:

- `today-banner` (top banner)
- header `price-main` / `price-change` / 52-week line
- `#tech` "핵심 가격대" zone-list, the MA-summary sentence, all four `구간별 패턴 분석` cards, the tag-pills row
- `#fund` box-key AND the `#fund` tab's own 핵심 투자 논리 card (both exist separately and both need the update)
- `#valuation` section-title (if it embeds a price), every `val-item`, Per-Share grid, 종합 밸류에이션 text, stage-grid distribution/footnote
- `#us` growth/segment cards and their chart data
- `#invest` Bull/Bear items that cite a multiple or %, the 목표가 밴드 card (see below), 5개 분석 종합, 투자의견 요약

`scripts/validate_widget.py` now catches one instance of this automatically (valuation-tab current price vs 목표가 밴드 marker, when the valuation section-title embeds "현재가 $X") - but that check is not a substitute for the manual grep above, since it only compares two of the many locations.

Two more leak points found by testing this skill on TSM, easy to miss because they're outside the fixed 6-element width list and outside the two obvious valuation cards:

- **Any other banner/note-style element the widget has beyond `.today-banner`/`.header`/`.box-key`/`.nav`/`.section`/`.disclaimer`** - e.g. TSM has its own `.note-box` (ADR share-conversion note) that PM doesn't have, and it was missed on the first width-fix pass. Grep the `<style>` block for every rule with `margin:` using a raw pixel value instead of `auto` before considering the width fix done.
- **Section-title date ranges** (e.g. "시계열 뉴스 (2025.07 ~ 2026.06)") - update the end date whenever a new news event pushes the real latest date forward.

## Stage-badge vs. narrative-text mismatches - check every occurrence, not just one

A stage-grid's per-metric badges (`stage-badge stage-N`) can be internally correct while one or more *separate* prose sentences elsewhere still describe an older distribution - and a widget can have **more than one such sentence to check**. TSM had this in two different places at once: the `#valuation` "종합 밸류에이션" card's paragraph *and* the "밸류에이션 5단계" stage-grid card's own footnote sentence both restated the 5-metric distribution independently, and only one of the two was caught on the first pass (the other - which claimed PCR was "4단계" when both its own badge and the stage-grid's own tag placement said stage-1 - was only caught by the browser walkthrough, not by grep). Whenever you touch valuation data, find every sentence that names a metric + a stage number or 저평가/고평가 word, not just the first one you spot, and verify each against the actual `stage-badge` values.

Determining the (고평가|적정가|저평가) verdict itself is not always a clean read - PM/CAT had all 5 metrics clustered on one side, making the call trivial, but TSM's badges were `[2,1,3,1,3]` (mixed low/fair, nothing high) and required actually counting rather than eyeballing the card's existing subtitle.

## More structural checks, found on a second TSM pass

- **MA-row layout**: `.ma-row` is `display:flex;justify-content:space-between` over what should be exactly 2 children (`.ma-name` and a wrapper). If a widget instead has 3 direct children (`.ma-name`, `.ma-val`, `.ma-status`), `space-between` spreads all three apart and the price ends up nowhere near the status badge - it needs to visually sit immediately left of "현재가 상회/하회". Fix: wrap `.ma-val` + `.ma-status` together in `<div style="display:flex;align-items:center;gap:10px;">`, matching PM. Check this on every widget - it can be present from the start and never get caught by content-focused review.
  **This DOES degrade from data refreshes, and can actively corrupt already-fixed widgets** - confirmed 2026-08-08 when a refresh pass updated MA values on AAPL/AMZN/GOOGL/META/MSFT (all previously wrapped correctly) by regenerating each `.ma-row`'s inner HTML from a template that didn't include the wrapper. That stripped the two wrapper `<div>` opens per row while leaving their matching `</div></div>` closes in place - not just a visual regression back to unwrapped, but actual unbalanced-HTML corruption (traced via `git diff` between the commit before and after: AAPL was exactly 362/362 open/close before, 354/362 after). **When updating a `.ma-val` number, edit only the digits inside the existing `<span class="ma-val">…</span>`, in place - never regenerate the row's surrounding markup from a fresh template or string-join.** After any refresh touching MA values, run `python3 scripts/audit_widgets.py TICKER` and confirm div-balance (`grep -o '<div' file | wc -l` vs `grep -o '</div>' file | wc -l`) before considering the pass done; `scripts/fix_ma_row_gap.py` can repair both the never-wrapped and the corrupted-by-regression case if one slips through.
- **구간별 패턴 분석 sentiment color**: verify each of the 4 period cards' background/border/title color comes from `var(--green)` / `var(--event-neutral)` / `var(--red)` only. A visually-similar but semantically wrong substitute (e.g. `var(--ma60)`, a gold MA-line color) is easy to miss since it renders a plausible-looking yellow/gold card - but it's the wrong variable and not part of the documented 3-color sentiment system.
- **Count requirements from `canonical_widget_spec.md`**: the `#fund` quarterly chart needs 8 quarters (rolling window) and the primary KPI grid needs exactly 9 `.stat-box` cards - these aren't currently enforced by `validate_widget.py`, so a widget can silently ship with 5 quarters or 7 KPI boxes. Count them explicitly when touching `#fund`.
- **Rebuilding a shortened quarterly series can surface a deeper data bug, not just missing history**: extending TSM's chart from 5 to 8 quarters required fetching 3 older quarters, and cross-checking those against the *existing* 5 revealed the whole 순이익 (net income) series was internally inconsistent with revenue/margin (each value implied a NT$→USD rate wildly different from the rest, off by close to one full quarter's growth) - likely a stale or miscomputed series from whenever it was first built. Recomputing all 8 net-income points from NT$ figures at one consistent FX rate (not just appending 3 new ones next to 5 old ones) was the actual fix.

## Stage-badge/narrative staleness can spread across 6+ locations in one widget - grep the number, don't card-scan

On NVDA, the same handful of stale multiples (PER, EV/EBITDA, PBR, PSR, PCR - each pinned to whatever they were the last time someone actually recalculated) had been copy-pasted into **six separate places**: the peer-comparison chart's own data array, the peer-comparison prose beneath it, both paragraphs inside the "종합 밸류에이션" card ("저평가 근거" *and* a separate "주의 요소" box), a scenario-card premise, the 목표가 밴드 narrative sentence, the 5개 분석 종합 zone-item, and a Bear-factor bullet - eight total counting the stage-grid footnote already covered above. Fixing the val-item badges and one obvious narrative sentence is not enough. Once you've identified the correct current numbers, **grep the file for the old (wrong) numbers themselves** (e.g. `grep -n "25.6x\|20.7x\|53.4x"`) rather than relying on tab-by-tab visual scanning - the wrong numbers are the fastest way to find every place they leaked to, including ones a card-by-card read will miss (the "종합 밸류에이션" card had two separate stale paragraphs stacked in it; a scan that stops after finding one feels done but isn't).

A related but distinct bug: a summary line can flip the *direction* of a fact, not just go stale on a number. NVDA's "5개 분석 종합" card claimed "MA60>MA20>MA5>MA120>현재가 · 전 이평선 하회 · 기술적 약세" (price below all 4 MAs, bearish) while the 이동평균선 현황 card two tabs over correctly showed price above all 4 MAs (bullish) - the technical setup had flipped since that summary line was last written, and nothing about the number-based checks above would have caught a wrong *direction* claim with no numbers in it to grep for. Read what each cross-tab summary line actually asserts, not just whether it has a plausible-looking number.

## 목표가 밴드 (target price band) gauge

**Check which markup convention the widget already uses before computing anything** - count the flex divs in the color bar:

- **7 segments** (pad-left/bear/gap/base/gap/bull/pad-right) - PM's convention, most widgets. Run `target_band_gauge.py` with no extra flag.
- **5 segments** (bear/gap/base/gap/bull, no end padding) - CAT's convention. Run with `--no-pad`.

Applying the wrong mode silently misplaces the current-price marker relative to the widget's own color bar (this happened once already, on CAT, and was only caught on a later pass). Verify by confirming the script's segment-width output matches the widget's existing (or original) segment widths before trusting the marker positions.

```
python3 scripts/target_band_gauge.py --bear LO HI --base LO HI --bull LO HI \
    --current PRICE --target TARGET [--no-pad]
```

**Not every widget's 목표가 밴드 is a Bear/Base/Bull scenario band at all.** TSM's version is a single analyst Low/Average/High range instead (card text literally states "목표가 밴드 $354~$700 · 평균 $520.37"), which doesn't fit `target_band_gauge.py`'s three-range interface. When you hit this shape, compute by hand: `marker_pct = (price - domain_min) / (domain_max - domain_min) * 100` using the domain the card's own text states (here `[354, 700]`) - verify it reproduces the *unchanged* value (target/average marker here) before trusting the recomputed current-price marker.

For the standard three-range case, apply the printed segment widths, both marker `left:%` values, and the current-vs-target upside % together. Keep the Bear/Base/Bull dollar ranges unchanged unless there's a documented fundamental reason to move them (a market-price move alone is not one - but a real earnings beat with raised guidance, like CAT's Q2, can be, and even then be conservative: check whether analyst high/low already bracket the existing range before touching it). Recompute the analyst-distribution bar widths (`buy/(total)*100` etc.) from the verified count, never eyeball them.

## Format conventions this session established beyond `canonical_widget_spec.md`

- **`(초저평가|저평가|적정|고평가|초고평가)` tag** (2026-08-08: expanded from the original 3-tier 고평가/적정/저평가 set at user request, to match the 5-stage granularity already used by `#valuation`'s `stage-badge`s): wherever "핵심 투자 논리" appears (both the header box-key, if present, and the `#fund` card title), append a colored span using the *same* 5-color hex values PM's own `.stage-1`–`.stage-5` CSS classes already define (not each ticker's brand-specific `--accent2`, which varies per file and would make the tag's color meaning inconsistent across widgets):
  - 초저평가 → `#2ecc71` (stage-1)
  - 저평가 → `#27ae60` (stage-2)
  - 적정 → `var(--gold)` (stage-3; add `--gold: #f0c040;` to the widget's `:root` if missing - it's usually already referenced elsewhere, e.g. stage-mini tag chips, US-tab zone-vals, without being defined, a silent bug worth fixing on sight)
  - 고평가 → `#e67e22` (stage-4)
  - 초고평가 → `var(--red)` (stage-5)

  Pick the tag from the same majority-vote read on the `#valuation` stage-badge distribution used for the 3-tier version (see the paragraph above on TSM's `[2,1,3,1,3]` case) - a widget with metrics clustered at stage-1/2 reads 초저평가/저평가, not just 저평가, when the distribution actually skews to the extreme end, not just the mild one. `check_valuation_verdict_tag` in `audit_widgets.py` accepts all five values.
- **Bull/Bear triangle color**: `▲` gets `var(--bull)`, `▼` gets `var(--bear)` (Korean market convention - red=up/gain, blue=down, the opposite of the US convention used elsewhere in the same file for the target-band Bear/Bull colors; this is intentional, don't "fix" it to match). Apply inline `style="color:var(--bull);"` / `var(--bear);"` directly on each triangle span - don't rely on a shared CSS class, since older widgets have some `bb-item`s with the `bb-icon` class and some without, so a class-based rule silently misses half of them.
- **투자의견 요약**: stacked layout (`display:flex;flex-direction:column;gap:10px`, not a wrapped flex row), exactly four lines in order - 📅 다음 실적 / 투자의견 / 목표주가 / 결론. No separate valuation-verdict line here - that belongs on the 핵심 투자 논리 title tag instead (redundant with the 5개 분석 종합 card's ⚖️ row otherwise).
- **시계열 뉴스**: newest event first (top of the DOM = most recent date). Check this on every widget touched - at least one existing widget (CAT) had it backwards before this session.
- **Page width**: `.today-banner`, `.header`, `.box-key`, `.nav`, `.section`, `.disclaimer` all need `max-width:1100px; margin:0 auto` (disclaimer keeps its own top/bottom margin: `margin:28px auto 16px`). `.back-bar` stays full-bleed. Many older widgets are still missing this - check and fix opportunistically when touching a widget for another reason.
- **box-key** (header-level 핵심 투자 논리 summary): not universal yet (~9/45 widgets have it). If adding one to a widget that lacks it, copy PM's structure - a short stat-based subtitle line ("Q2 매출 $X (+Y%) · PER Zx") plus the same paragraph body as the `#fund` tab's 핵심 투자 논리 card, `max-width:1100px;margin:0 auto 16px` on the `.box-key` CSS rule, background tinted with the widget's own `--accent2` at low alpha.

## 손익계산서 표준 차트 (#fund) — 매출/순이익/OPM, 2026-08-08

The `#fund` chart is now fixed to exactly 3 series: 매출($B) bar, 순이익($B) bar,
영업이익률(OPM,%) line - single y-axis for the two bars, single secondary y-axis for the one
line. This replaced real per-ticker drift (GOOGL/META/MSFT plotted 영업이익 instead of 순이익;
JNJ plotted GAAP/Adjusted EPS lines instead of a margin line; TSLA had no dollar bars at all,
just GM%/OPM%; AMZN's chart is segment-focused - 매출+AWS+OPM - which is a legitimate ticker-
specific exception, not drift, since AWS-vs-total is the actual investment story there).

This exact set was reached through several rejected alternatives worth knowing before you touch
another widget's chart, so the same dead ends aren't re-walked:

1. **5-series single chart** (매출/순이익 bars + OPM/매출총이익률/순이익률 lines, dual axis) -
   rejected as visually too dense; three overlapping % lines crossing each other made the chart
   hard to read even though Chart.js rendered it without technical issues.
2. **Dot-only markers instead of dashed lines** for the two extra margin lines - cleaner than (1)
   but still added clutter without adding information, once (3) below made the deeper point.
3. **Two separate charts in one card** (money chart + margin chart, stacked with a divider) -
   genuinely worked visually (no axis-scale conflict, each sub-chart legible on its own) but was
   dropped anyway once the real question got asked: **영업이익률 is not derivable from
   매출총이익률 and 순이익률 together** (판관비 sits between the first two, 영업외손익+세금 sits
   between the last two - two different, non-substitutable gaps) so all three margins really are
   distinct information. But practically, OPM alone is the one analysts lean on most because it's
   the cleanest read of core-business profitability, uncontaminated by COGS-mix noise (매출총이익률)
   or one-time/tax noise (순이익률) - so the fix wasn't a layout trick, it was dropping the other
   two margins from the chart entirely, not just changing how they're drawn.
4. **Bars: settled on 2, not 3.** 영업이익 doesn't need its own bar once OPM is the chart's only
   line - a reader can back it out as 매출×OPM% - so a dedicated 순이익 bar carries more marginal
   information than a third $-bar would. This is also why 영업이익 isn't shown as a stat-box
   duplicate elsewhere without the OPM context nearby.

When migrating an older widget's chart to this standard, don't just relabel an existing 영업이익
series as 순이익 - the underlying data is different (영업이익 excludes non-operating items,
순이익 includes them), pull the real net-income series from `fetch_financials.py`'s `netIncome`
concept (already covers this - no script extension needed for this part, unlike the 재무
건전성 card below).

## 재무 건전성 카드 (안정성·활동성) — 2026-08-08

Replaces `#valuation`'s old `stage-grid` card; lives in `#fund`, directly after the KPI stat-box
grid (9-box on unmigrated widgets, 6-box on NVDA - see "#fund KPI box count" section below) and
before 핵심 성장 동력. See `docs/canonical_widget_spec.md`'s "재무 건전성 card"
subsection for the exact formulas and CSS class list (`.diag-*` for 안정성, `.act-*`/`.ccc-*`/
`.tl-*` for 활동성) - copy NVDA's markup verbatim rather than re-deriving the layout.

**Why 안정성 uses checkup badges (✅/⚠️), not a bar gauge**: the first prototype used
`val-track`/`val-fill`-style progress bars (matching the `#valuation` multiples card's visual
language). The user rejected it after seeing it live - a bar with a threshold marker requires
the reader to interpret a position-on-a-scale, which isn't legible to a lay reader at a glance,
unlike a green ✅ badge that states the verdict directly. This is a real, useful pattern:
**when a metric has a hard pass/fail threshold from the source material** (유동비율 150%/50%,
당좌비율 100%, 차입금의존도 30%, 이자보상배율 1x - all from 하마터면 회계를 모르고 일할 뻔했다),
prefer a stated verdict over a bar/gauge visualization of the same fact.

**Why 활동성's CCC number is colored neutrally (`var(--gold)`), never red/green**: the opposite
lesson from the same design pass. 활동성 metrics have no universal pass/fail line the way 안정성
does - a shorter CCC ties up less cash, but "how short is good" is entirely industry-dependent
(a semiconductor maker's CCC is structurally longer than a software company's due to physical
inventory and validation cycles). Coloring CCC red implied a false "this is bad" verdict the
data can't actually support without a peer-industry comparison this card doesn't have. Give it a
one-line plain-language explanation of the day-count instead of a color-coded judgment - and
resist the urge to add a caveat sentence explaining the industry-comparison nuance in the card
itself (tried this, user cut it) - the neutral color already communicates "no verdict here",
spelling it out again in prose was redundant.

**Data pipeline**: `scripts/fetch_financials.py`'s `CONCEPTS` dict was extended for this card -
`currentAssets`, `currentLiabilities`, `inventory`, `accountsReceivable`, `accountsPayable`,
`totalLiabilities`, `shortTermDebt`, `longTermDebt`, `costOfRevenue`, `interestExpense` are all
new (none of the balance-sheet-level detail existed before; the script previously only pulled
`assets`/`equityAttributableToParent`/`cash` at the balance-sheet level). Two real snags found
building NVDA's card, both fixed in the script rather than worked around per-ticker:

- `interestExpense`'s first-choice XBRL tag (`InterestExpense`) silently stopped returning
  current data for NVDA after Q1 FY2024 - plausibly because their real debt became immaterial
  enough that they stopped tagging it separately. `extract_concept`'s existing recency-comparison
  logic (picks whichever candidate tag has the most recent data, not just the first with *any*
  data) already handles this correctly once `InterestExpenseNonoperating` was added as a
  fallback candidate - don't assume the first tag in a `CONCEPTS` list is still the live one for
  every ticker, especially for low-debt companies.
- 매입채무 회전율 needs a 매입액 (purchases) figure that's essentially never tagged directly in
  XBRL. Approximate it as 매출원가 + (당기말 재고자산 − 전기말 재고자산) rather than fetching a
  concept that doesn't reliably exist.

## 재무 건전성 카드 — collapsible shell + trend-based 활동성 판정, 2026-08-09

Three follow-up changes to the card above, all NVDA-only so far (not yet propagated to the rest
of the fleet — do this pass when a widget is otherwise being touched, same "opportunistic
migration" rule as everything else NVDA-standard).

**1. Card became collapsible, iteratively, across several corrections in one session:**

- First pass wrapped the *entire* card body (both 안정성 and 활동성) behind one click on the
  card title, default-expanded. User asked for legible title-bar text (first fix touched only
  the inner content CSS, missed the actual clickable title bar — caught via a screenshot the
  user sent of the collapsed state) and a pill-badge affordance so it visually reads as
  interactive, not just a plain title.
- Then asked "should the default be collapsed?" as an open design question — ran a text-mode
  `codex exec -` review (see `_system/workflow/codex_review_loop.md` in the second-brain vault)
  on placement + collapse-default. Codex's answer, adopted: **don't fully collapse the summary
  verdict** — a card that reads "매우 안정적" only after a click hides the one sentence a reader
  actually needs first. Split into "always-visible summary + collapsible detail" instead of
  "always-visible title + collapsible everything."
- User then asked for the same always-visible treatment on the 활동성 summary (it had been left
  inside the collapsed body when 안정성's was pulled out) — moved both summaries above the fold.
- Finally, with both summaries visible and one shared "상세 보기" toggle below them, expanding it
  merged both sections' detail rows into one block with no visual seam — user flagged this as
  confusing. Split into two independent `.detail-toggle`s (안정성/활동성), each with its own
  `.collapsible-body`. See `canonical_widget_spec.md`'s 재무 건전성 subsection for the final
  structure — don't rebuild from an earlier commit's markup, several intermediate states in this
  file's git history are superseded.
- Takeaway for the next widget: build the final two-summary/two-toggle shape directly, don't
  replay the whole iteration — but if the user asks for opinions on placement/collapse-default
  again on a *different* widget, the same "summary stays, detail collapses" logic likely still
  applies since it came from a real readability argument, not a one-off preference.

**2. `.diag-badge`/`.diag-summary` gained a third tone, `.watch` (amber, `var(--gold)`)**,
alongside the existing `.safe` (green) / `.info` (gray) — for "notable but not alarming," sitting
between the two. Don't reuse `.info` for genuinely large swings just because there's no red/danger
tier defined; `.watch` exists precisely so a real deceleration doesn't get flattened into the same
visual weight as a routine footnote.

**3. 활동성 rows now carry a trend-based judgment (current TTM vs. the same TTM window one year
earlier), not just a bare number** — this is what `.watch` is for. Computed by hand for NVDA,
worth automating into `fetch_financials.py` before the next widget needs it:

- Pull `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` directly (same endpoint
  `fetch_financials.py` already uses, just read further back in the same JSON rather than calling
  the script twice). Need: quarter-end **instant** balances (`AccountsReceivableNetCurrent`,
  `InventoryNet`, `AccountsPayableCurrent`) at both TTM boundaries (start and end), and quarterly
  **duration** figures (`Revenues` or `RevenueFromContractWithCustomerExcludingAssessedTax`,
  `CostOfRevenue` or `CostOfGoodsAndServicesSold`) for all 4 quarters in each TTM window. A fiscal
  Q4 duration value is usually not tagged standalone — derive it as (annual 10-K figure) − (9-month
  YTD figure from the Q3 10-Q).
- Average-balance method: `turnover = TTM_flow / ((balance_at_TTM_start + balance_at_TTM_end) / 2)`.
  For AP specifically, use **purchases** (COGS + ΔInventory over the same window), not raw COGS —
  confirmed by reverse-engineering NVDA's own already-published 7.83회/46.6일 AP figures: COGS
  alone reproduced neither number, COGS+ΔInventory reproduced both exactly.
  **Always validate the current-period recomputation against the widget's own existing (trusted)
  figures before computing the prior period** — if the method doesn't reproduce known-correct
  numbers, the prior-period output can't be trusted either. (NVDA check: recomputed 8.07회/45.2일/
  3.53회/103.4일/7.83회/46.6일/148.6일/102.0일 all matched the file's existing values exactly.)
- **Badge direction is asymmetric, not just "turnover down = bad"**: AR turnover falling and
  재고자산 회전율 falling both genuinely mean "slower" (worth a `.watch` if the magnitude is
  large). 매입채무 회전율 falling means the *opposite* in practice — the company is stretching
  supplier payment terms, which is mild cash-flow relief, not deterioration — so badge that
  `.info`, not `.watch`, regardless of how large the % change is. Getting this backwards would
  flag a mildly *good* development as a warning.
- Name the CCC change's dominant driver in the summary `.sub` line (which side of 영업순환주기 −
  AP기간 actually moved) rather than only stating the delta — NVDA's case was ~92% inventory-
  driven (+32.7일 of a +35.5일 cycle change), with AR contributing only +2.8일; a reader shouldn't
  have to infer that split themselves from the row-level numbers.

## `#fund` chart load animation - grow-from-bottom, not fly-in, 2026-08-08

User reported the `#fund` chart's load animation looked like it was "flying in" rather than
growing from the bottom, even though nothing in the widget (or the whole fleet, grepped) had any
custom `animations:` config - Chart.js was running on pure defaults.

Diagnosed live in-browser (destroyed and re-created the chart with an artificially long
`duration` to slow it down enough to screenshot mid-animation, several iterations): the bars
were already growing correctly from 0 under Chart.js defaults, but the OPM **line** was not -
its points reach their final `(x,y)` almost immediately while the bars are still near-zero
height, so for most of the animation the viewer sees a fully-formed line floating above
unfinished bars. That mismatch - one series completing instantly while the other visibly grows -
is what read as "flying in," not a swirl/artifact in the line itself (an earlier scroll-clipped
screenshot briefly looked like a spiral glitch in the line; re-screenshotting at the correct
scroll position showed that was just an optical artifact of viewing a curved line through a
narrow crop, not a real bug).

**Fix**: `renderFundChart()` now creates the chart with `animation:false` and every dataset
pinned to its own axis baseline (bars at 0, the OPM line at the `y2` scale's `min`), then on the
next animation frame (`requestAnimationFrame`) swaps in the real data and calls `chart.update()`
with the actual `animation:{duration,easing}` config. Chart.js's own data-transition animation
then interpolates every series from that shared flat baseline to its final value in lockstep, so
bars and line rise together with no snap. This is a two-step create-then-update, not a
`animations: { y: { ... from ... } }` override - `validate_widget.py` explicitly forbids that
literal pattern (a past, unrelated "fly-in" bug used it to drop elements in from the wrong
direction) - so this fix doesn't need a validator exception and passes as-is.

If another widget's chart gets this same complaint, check first whether it's a mixed bar+line
chart before assuming the fix applies - a pure-bar or pure-line chart doesn't have this
completion-mismatch in the first place.

## `#fund` KPI box count - 9 to 6, 2026-08-08

The legacy 9-box `grid-3` KPI grid was trimmed to 6 on NVDA after the user flagged that #fund had
become too dense once the 재무 건전성 card was added on top of it. Rather than picking round
numbers, went through the full 9 (plus one newly-discovered gap) box by box and kept only what
wasn't already shown somewhere else on the page:

- **Dropped as chart duplicates**: 매출, 영업이익, 순이익 - all three are now directly on the
  #fund chart (see "손익계산서 표준 차트" above), so a stat-box repeating one is pure redundancy.
- **Dropped as top-summary duplicates**: TTM 매출 - the ticker header row above the tabs already
  shows TTM 매출 and TTM EPS, so this box added nothing a reader couldn't already see without
  switching tabs.
- **Kept, each covering a distinct axis with zero overlap with anything else on the page**:
  순이익률 (the one *final* bottom-line margin figure left anywhere in the widget once 영업이익/
  순이익 boxes are gone - distinct from the chart's OPM, which stops at operating income),
  FCF (cash actually generated), **Capex** (see below - a new box), 현금 및 단기투자 (absolute
  balance-sheet cash figure - the 재무 건전성 card's 유동비율 uses this number internally but
  only ever displays the *ratio*, never the dollar amount), EPS (quarterly - distinct from the
  TTM EPS already in the top summary), and 다음 실적 (calendar, always unique).
- Each box's `.stat-sub` line now leads with a short axis tag before the existing detail (e.g.
  "현금창출력 · FCF 마진 59.5%", "미래 재투자 · 매출의 2.2%(팹리스)") at the user's request, so a
  reader can tell at a glance what each box represents and confirm none of the six repeat.

**Capex was a real gap, not just a density trim.** Mid-discussion the user asked whether the
widget showed how much NVDA itself invests in its future - it didn't. Every existing "capex"
mention on the page (핵심 투자 논리, 하이퍼스케일러 AI Capex 차트, US 특화 등) is about
*hyperscaler* capex - Meta/MSFT/Amazon/Alphabet's spending, which is NVDA's demand signal, not
NVDA's own number. `fetch_financials.py` gained two new concepts for this:
`PaymentsToAcquirePropertyPlantAndEquipment` (capex) and `NetCashProvidedByUsedInOperatingActivities`
(operatingCashFlow, added alongside it so FCF = OCF − Capex can be sanity-checked against the
existing FCF box rather than trusted blindly - this caught nothing wrong for NVDA, OCF $50.3B −
Capex $1.76B ≈ FCF $48.6B matched, but do this check every time a Capex figure is added to
another widget). NVDA's Capex is small relative to revenue (~2.2%) because it's fabless (TSMC
manufactures) - worth a one-line note in the box, not just the bare dollar figure, since a reader
comparing it to the $700B hyperscaler number nearby could otherwise misread NVDA's own capex
intensity.

`scripts/audit_widgets.py`'s `check_kpi_count` now accepts both 6 and 9 as valid box counts, the
same both-old-and-new pattern used for `validate_widget.py`'s valuation card-order check.
Grid stays `grid-3` (3×2 for 6 boxes) - no CSS change needed. A `.grid-4` class already exists
in-file (reused from the #tech 구간별 패턴 분석 card) if a future widget lands on exactly 4 boxes
instead and wants a single row - `.grid-3`/`.grid-4` both already collapse to 2 columns on
mobile via the existing media query.

## `#us` sector evidence framework

Select evidence by business model, not a generic template:

| Sector | Look for | Avoid defaulting to |
|---|---|---|
| 정보기술 (note: split further - semiconductor/equipment vs. software/cloud/govtech are very different stories within this one bucket) | US capacity/fab investment, RPO/backlog quality, R&D, customer prepayments | generic institutional-ownership summary |
| 통신서비스 | US ad revenue/DAU-MAU, US subscriber count/ARPU, content/network capex | Street consensus restated |
| 임의소비재 | US comp sales, traffic/ticket, store/distribution footprint, named growth channel (e.g. a "Pro" segment) | dividend/buyback figures |
| 필수소비재 | US category volume/share, channel economics, regulation/capacity | generic valuation restated |
| 금융 | US client assets/flows, segment mix, regulatory capital (CET1/SCB/TLAC-equivalent) | bare beta with no context |
| 헬스케어 | US product mix, FDA/PDUFA catalysts, patent exclusivity, reimbursement | generic pipeline description |
| 산업재 | US backlog, government/defense contract exposure, reshoring/infrastructure policy exposure | generic revenue-geography split |
| 에너지 | US production volume, refining/capacity utilization, domestic regulatory exposure | oil-price commentary alone |

The "avoid" column is a default, not an absolute ban - if a metric is genuinely central to that company's specific US thesis (e.g. dividend policy for a staples aristocrat), use it; just don't reach for it as filler.

**ADR / foreign issuer is not one category.** Check which of these actually applies before writing the card:
- **Real US legal subsidiary** (e.g. a bank's US-chartered arm) - use its own 10-K/10-Q, not group figures.
- **Active US capital investment** (e.g. a fab under construction) - the investment/subsidy/timeline *is* the US story; lead with it, don't bury it next to non-US facilities as one of several "global" bullet points (this was TSM's actual bug - real Arizona data existed but was framed as "global fab strategy" instead of "US investment").
- **US customer/export-exposure only, no real US operations** - reframe the card honestly around that exposure (e.g. export-control risk, customer concentration) rather than inventing a US-operations narrative that doesn't exist.

Every `#us` chart card needs adjacent interpretation text (not a bare canvas) - `validate_widget.py` now checks for this. When a real regional/segment number isn't disclosed, say so explicitly (an honest "이는 북미 단독 수치가 아니며..." caveat, like CAT's original text had) rather than silently substituting a global figure - and check one level deeper before concluding no better data exists (CAT's real NA segment split *was* in its own 10-Q; the caveat was masking a research gap, not a real disclosure gap).

## validate_widget.py can itself have false positives - verify before trusting a FAIL

The old "stale MSFT Capex/FCF chart data found" check matched on the generic substring `'Capex($B)'`, which meant it flagged NVDA's and AMZN's own legitimate hyperscaler-capex charts (real, ticker-specific content) as if they were copy-pasted MSFT template leakage. Fixed by switching to the same pattern the working "stale PM template identifiers" check already used - search for MSFT's actual unique identifiers (`MSFT_DAILY`, `msftCandleSvg`, `msftVolumeSvg`) instead of a topic keyword. When a validator FAIL doesn't match what you see in the file, check whether the *check itself* is well-targeted before assuming the widget is wrong - and if you fix the check, verify it against a widget that should still legitimately fail (there wasn't one available for this specific check, so this was verified by confirming NVDA/AMZN/META/MSFT all pass cleanly instead).

## 핵심 가격대 zone-val colors - checked in `#valuation` but not in `#tech`

`canonical_widget_spec.md` says resistance/current/support prices should be red/`var(--accent2)`/green, but that check was only being applied to the valuation-tab `.zone-val`s. TSM and NVDA's `#tech`-tab "핵심 가격대" (or "구간별 가격 분석") card - the 52주 최고/현재가/MAxxx 지지/52주 최저 rows - had zero color on any `.zone-val`, only the `.zone-tag` badge next to it carried the semantic color. CAT already had this right (built correctly from the start), so this isn't universal drift - check it explicitly on every widget rather than assuming it's covered by the valuation-tab check. Fix: `style="color:var(--red|--accent2|--green);"` on the `.zone-val` span itself, matching whichever `.zone-tag` (저항/현재/지지) sits next to it in the same row.

## Stale valuation-multiple propagation - fleet-wide, found 2026-08-08

NVDA's #valuation tab had a bug class worth checking on every widget: the "멀티플 5단계 평가" val-item badges get recalculated when a widget is refreshed, but prose mentions of the same multiple elsewhere in the tab (종합 밸류에이션, 피어 비교 card+chart, 시나리오별 공정가치, 목표가 밴드, and #invest's 5개 분석 종합) don't always get resynced - they're free text, not derived from the val-item at render time. `scripts/audit_valuation_consistency.py` checks this mechanically: extracts every val-item (name, number) pair, then scans the rest of the widget for the same metric keyword (PER/PBR/PSR/PCR/EV-EBITDA/P-S/Forward PER) followed by a number, and flags any prose mention that doesn't match. It also checks EV/EBITDA footnote self-consistency (`EV $X ÷ EBITDA $Y` should equal the displayed multiple) and 시가총액 vs 현재가×주식수.

Ran it fleet-wide once NVDA was fixed: **24 of the other 44 widgets have at least one instance of this**, 55 total findings. Two distinct patterns emerged, worth telling apart before fixing:

- **Uniform-gap tickers** (AAPL, AMAT, BRK.B, GOOGL, GE, KO, MSFT - every multiple on the same widget off by roughly the same %, e.g. AAPL ~6-7% across all 5, GOOGL ~9-10%, MSFT ~22%) - the uniformity across unrelated multiples is the signature of one root cause: the prose block was written against an older stock price and never resynced when the price/val-items were last updated. Likely fixable by resyncing the price reference in that one prose block rather than recomputing each multiple from scratch.
- **Large, non-uniform gaps** (AMZN 108%, TSLA 97% with 3 wildly different prose numbers, MU 73%, AVGO 64% with 4 inconsistent prose numbers, ORCL 35% with 2 different prose numbers, RHHBY 31%) - not a single stale-price signature, more likely a genuine data error (possibly GAAP/non-GAAP mixups, like the AVGO 영업이익 mixup found earlier in this project, or multi-quarter-stale figures) that needs the same SEC-EDGAR-verification treatment NVDA got, not just a resync.

Script has a real limitation: it does per-widget name-collision handling (e.g. ABBV's "PER (GAAP TTM)" and "PER (Adjusted TTM)" both strip to "PER" - matches each prose value against its *nearest* canon value, not a single one) but can't verify which number is actually *correct* against live data - it only catches internal inconsistency, same as `validate_widget.py`. A clean run doesn't mean the numbers are right, only that they agree with each other.

## 재무건전성 card on retailers/negative-CCC tickers (AMZN, and watch for WMT/COST) - 2026-08-09

A retailer's activity ratios can produce a genuinely **negative CCC** (AMZN: -46.2일) - it collects cash from customers faster than it pays suppliers, a well-known structural advantage, not a warning sign. Two adaptations from the NVDA template when this happens:

1. **Color the CCC value green, not NVDA's neutral gold.** The "always neutral, no universal threshold" rule was specifically for cases like semiconductor CCC where "how many days is good" is genuinely industry-relative and ambiguous. A *negative* CCC for a retailer has no such ambiguity - it's unambiguously a structural strength, so treat it like any other pass/fail-style metric and color it accordingly.
2. **Retool the timeline bar** - when AP-payment days (매입채무 지급기간) exceed 영업순환주기 (재고+매출채권 days), the marker can't sit inside the inventory+AR segment bar like NVDA's positive-CCC case. Scale the whole `.tl-bar-wrap` to a total that comfortably fits the *longer* of the two (pad ~10% past it so the marker label doesn't clip at the container edge), place the inventory+AR segments proportionally at the start, and put the AP marker further right with a green `.tl-ccc-span` bridging the gap between them - visually showing the "float" period the company gets to hold cash before paying.
3. Same reasoning likely applies to WMT/COST and any other low-margin, high-inventory-turnover retailer when they're migrated - check the CCC sign before copying NVDA's positive-CCC card verbatim.

Also found on AMZN's 안정성 metrics: 유동비율(103.3%)/당좌비율(87.5%) both read below the generic 150%/100% "safe" threshold, but this is *normal* for a retailer running tight working capital funded by supplier credit (the negative CCC above is the same fact from a different angle) - don't badge these as a warning. Used the `.diag-badge.info` (ℹ️) style with a "유통업 특성상 낮게 나옴" note rather than inventing a new "warning" badge class - the existing safe/info two-state system was enough once the note explains why info != alarming here.

## Dual-metric GAAP-vs-adjusted framing is not drift - verify before "fixing"

`audit_valuation_consistency.py` flags large val-item-vs-prose gaps as candidates, not confirmed bugs. Before treating a big flagged gap as a NVDA/AVGO-style stale-number error, read the surrounding prose first - AMZN's val-item PER (22.1x, GAAP TTM) vs its own prose "실질 PER ~46x" is a **deliberately explained** ex-one-time-gain figure (Anthropic mark-to-market gains inflating GAAP EPS), not a propagation bug; the two numbers are correctly computed and clearly labeled as different things. This is the same pattern as AVGO's GAAP-vs-Non-GAAP split and ABBV's GAAP-vs-Adjusted PER - **big, well-explained gaps are usually intentional; small, unexplained gaps (NVDA's 2.3%, AVGO's stale $16.40 EPS) are usually the real bugs.** Check the explanation before spending SEC-verification effort on a "fix" that isn't needed.

## Validation gate

Run in this order, fix every failure before moving on:

1. `<div>` open/close balance (`s.count('<div')` vs `s.count('</div>')`).
2. Extract the inline `<script>` block and run `node --check` on it.
3. `python3 scripts/validate_widget.py widgets/{TICKER}_analysis_widget.html --ticker {TICKER}`.
4. `python3 scripts/audit_widgets.py {TICKER}` - catches structural/formatting regressions (e.g. the ma-row wrapper) that `validate_widget.py` doesn't check. Run this even on a scoped repair, not just a full sync - it's what caught the MA-row corruption described above, on a widget that "only" needed its price updated.
5. Grep the whole file for every old number/date/price identified during the stale-propagation check above - confirm zero remaining hits (excluding the historical daily-bar array, which legitimately contains old prices).
6. Start a local server (`python3 -m http.server PORT`) and visually check every tab you touched in the browser at a wide window size (confirms both content and the max-width layout fix) - screenshot, don't just trust the HTML. Close the tab and kill the server when done.

## Git

Commit locally with a message that explains *why*, not just what changed (what earnings quarter, what bug, what was cross-checked against what source). **Never push without the user explicitly asking in that turn** - a prior push approval does not carry over to new changes. Never run `publish_widget.py` unsupervised (it auto-commits and auto-pushes). Exclude `widgets/kr_test/` and any other untracked path unrelated to the current task from the commit.
