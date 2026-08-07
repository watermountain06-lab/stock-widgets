---
name: stock-refresh
description: Refresh or repair an existing stock-widgets ticker card - from a scoped fix (one tab, one bug) to a full earnings-quarter synchronization. Use when the user says "stock-refresh", "이 위젯 업데이트해줘", asks to bring a card current after new earnings, requests a specific tab/section fixed on an existing ticker, or wants a fact-check/format-consistency pass on a widget already in widgets/.
---

# Stock Refresh

Work in `/Users/watermountain/Workspace/stock-widgets`. Never touch `widgets/kr_test/` (separate KR pipeline) unless explicitly asked.

## Single source of truth

Read `docs/canonical_widget_spec.md` first - it is the reconciled, current spec for all 6 tabs (order, card titles, formatting rules), built from PM's actual structure and already resolves two places where `progress_log.md`'s older notes had drifted. Don't treat PM's raw HTML or `progress_log.md` as competing specs; when they conflict with the canonical doc, the doc wins. Use PM's HTML only to copy exact markup/CSS scaffolding the doc references but doesn't fully reproduce (e.g. the candlestick SVG renderer).

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

- **MA-row layout**: `.ma-row` is `display:flex;justify-content:space-between` over what should be exactly 2 children (`.ma-name` and a wrapper). If a widget instead has 3 direct children (`.ma-name`, `.ma-val`, `.ma-status`), `space-between` spreads all three apart and the price ends up nowhere near the status badge - it needs to visually sit immediately left of "현재가 상회/하회". Fix: wrap `.ma-val` + `.ma-status` together in `<div style="display:flex;align-items:center;gap:10px;">`, matching PM. Check this on every widget - it's a one-time markup mistake at authoring time, not something that degrades from data refreshes, so it can be present from the start and never get caught by content-focused review.
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

- **`(고평가|적정가|저평가)` tag**: wherever "핵심 투자 논리" appears (both the header box-key, if present, and the `#fund` card title), append a colored span - `var(--red)` for 고평가, `var(--gold)` for 적정가, `var(--green)` for 저평가 - matching the current 밸류에이션 5단계 stage distribution. If `var(--gold)` isn't defined in the widget's `:root` yet, add `--gold: #f0c040;` (it's usually already referenced elsewhere - stage-mini tag chips, US-tab zone-vals - without being defined, a silent bug worth fixing on sight).
- **Bull/Bear triangle color**: `▲` gets `var(--bull)`, `▼` gets `var(--bear)` (Korean market convention - red=up/gain, blue=down, the opposite of the US convention used elsewhere in the same file for the target-band Bear/Bull colors; this is intentional, don't "fix" it to match). Apply inline `style="color:var(--bull);"` / `var(--bear);"` directly on each triangle span - don't rely on a shared CSS class, since older widgets have some `bb-item`s with the `bb-icon` class and some without, so a class-based rule silently misses half of them.
- **투자의견 요약**: stacked layout (`display:flex;flex-direction:column;gap:10px`, not a wrapped flex row), exactly four lines in order - 📅 다음 실적 / 투자의견 / 목표주가 / 결론. No separate valuation-verdict line here - that belongs on the 핵심 투자 논리 title tag instead (redundant with the 5개 분석 종합 card's ⚖️ row otherwise).
- **시계열 뉴스**: newest event first (top of the DOM = most recent date). Check this on every widget touched - at least one existing widget (CAT) had it backwards before this session.
- **Page width**: `.today-banner`, `.header`, `.box-key`, `.nav`, `.section`, `.disclaimer` all need `max-width:1100px; margin:0 auto` (disclaimer keeps its own top/bottom margin: `margin:28px auto 16px`). `.back-bar` stays full-bleed. Many older widgets are still missing this - check and fix opportunistically when touching a widget for another reason.
- **box-key** (header-level 핵심 투자 논리 summary): not universal yet (~9/45 widgets have it). If adding one to a widget that lacks it, copy PM's structure - a short stat-based subtitle line ("Q2 매출 $X (+Y%) · PER Zx") plus the same paragraph body as the `#fund` tab's 핵심 투자 논리 card, `max-width:1100px;margin:0 auto 16px` on the `.box-key` CSS rule, background tinted with the widget's own `--accent2` at low alpha.

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

## Validation gate

Run in this order, fix every failure before moving on:

1. `<div>` open/close balance (`s.count('<div')` vs `s.count('</div>')`).
2. Extract the inline `<script>` block and run `node --check` on it.
3. `python3 scripts/validate_widget.py widgets/{TICKER}_analysis_widget.html --ticker {TICKER}`.
4. Grep the whole file for every old number/date/price identified during the stale-propagation check above - confirm zero remaining hits (excluding the historical daily-bar array, which legitimately contains old prices).
5. Start a local server (`python3 -m http.server PORT`) and visually check every tab you touched in the browser at a wide window size (confirms both content and the max-width layout fix) - screenshot, don't just trust the HTML. Close the tab and kill the server when done.

## Git

Commit locally with a message that explains *why*, not just what changed (what earnings quarter, what bug, what was cross-checked against what source). **Never push without the user explicitly asking in that turn** - a prior push approval does not carry over to new changes. Never run `publish_widget.py` unsupervised (it auto-commits and auto-pushes). Exclude `widgets/kr_test/` and any other untracked path unrelated to the current task from the commit.
