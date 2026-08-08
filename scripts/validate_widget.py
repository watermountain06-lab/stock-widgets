#!/usr/bin/env python3
"""Validate structure, data arrays, CSS classes, and two-way navigation."""
import argparse, json, re, sys
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('widget'); p.add_argument('--ticker',required=True); a=p.parse_args()
path=Path(a.widget); s=path.read_text(); errors=[]

def section(tab):
    opener=rf'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid="{tab}")[^>]*>'
    next_section=r'<div(?=[^>]*\bclass="section(?: active)?")(?=[^>]*\bid=")[^>]*>'
    m=re.search(rf'{opener}(.*?)(?={next_section}|<div class="disclaimer")',s,re.S)
    return m.group(1) if m else ''

def card_titles(tab):
    return [re.sub(r'<[^>]+>','',x).strip() for x in re.findall(r'<div class="card-title">(.*?)</div>',section(tab),re.S)]

for tab in ('tech','fund','valuation','us','news','invest'):
    if f'id="{tab}"' not in s: errors.append(f'missing tab: {tab}')
for text in ('다음 실적 체크포인트','Per-Share','S&P 500 대비','목표가 밴드','5개 분석 종합','투자의견 요약'):
    if text not in s: errors.append(f'missing block: {text}')
if s.count('class="val-item"') != 5: errors.append('valuation list must contain exactly 5 val-items')
# stage-grid was required exactly-once under the old PM contract; superseded 2026-08-08 when
# NVDA replaced it with #fund's 재무 건전성 card (see fund_titles/val_titles below). At most
# one is still enforced (no duplicates), but zero is now valid for NVDA-standard widgets.
if s.count('class="stage-grid"') > 1: errors.append('valuation must contain at most one stage-grid')
if s.count('class="tl-item"') < 5: errors.append('timeline must contain at least 5 events')
if re.search(r'tl-dot (?:blue|orange|teal|yellow)',s): errors.append('ad-hoc timeline color class')

# NVDA is the canonical component/order contract for every newly added widget
# (superseded PM 2026-08-08: 재무 건전성 - 안정성·활동성 moved into #fund, directly
# replacing #valuation's old stage-grid card; the #fund chart also standardized to a
# fixed 매출/순이익 bar pair + 영업이익률(OPM) line, dropping the per-ticker
# 영업이익-vs-순이익-vs-EPS mix the fleet had drifted into). Widgets not yet migrated
# still validate against the legacy 6-card PM order - both are accepted below.
fund_titles=card_titles('fund')
if len(fund_titles) < 4 or not fund_titles[-2].startswith('핵심 투자 논리') or not fund_titles[-1].startswith('다음 실적 체크포인트'):
    errors.append('fund tab must end with core thesis then earnings checkpoints, matching NVDA/PM')
if len(fund_titles) >= 2 and any(t.startswith('재무 건전성') for t in fund_titles) and not fund_titles[1].startswith('재무 건전성'):
    errors.append('재무 건전성 card must directly follow the fund chart/KPI block (NVDA standard)')
val_titles=card_titles('valuation')
val_contract_new=('멀티플 5단계 평가','peer','Per-Share','종합 밸류에이션','시나리오별 공정가치 분석')
val_contract_old=('멀티플 5단계 평가','peer','밸류에이션 5단계','Per-Share','종합 밸류에이션','시나리오별 공정가치 분석')
if len(val_titles) == 5:
    if not (val_titles[0].startswith(val_contract_new[0]) and
            val_titles[2].startswith(val_contract_new[2]) and
            val_titles[3].startswith(val_contract_new[3]) and
            val_titles[4].startswith(val_contract_new[4])):
        errors.append('valuation card order differs from NVDA (5-card, no stage-grid)')
elif len(val_titles) == 6:
    if not (val_titles[0].startswith(val_contract_old[0]) and
            val_titles[2].startswith(val_contract_old[2]) and
            val_titles[3].startswith(val_contract_old[3]) and
            val_titles[4].startswith(val_contract_old[4]) and
            val_titles[5].startswith(val_contract_old[5])):
        errors.append('valuation card order differs from PM (legacy 6-card)')
else:
    errors.append('valuation must contain 5 (NVDA standard) or 6 (legacy PM, not yet migrated) card titles')
us_titles=card_titles('us')
if len(us_titles) != 2: errors.append('US tab must contain exactly two dense cards after rel-container')
us_open=re.search(r'<div(?=[^>]*\bid="us")[^>]*>',s)
us_visual_mode=(re.search(r'data-us-visual="([^"]+)"',us_open.group(0)) if us_open else None)
if us_visual_mode:
    mode=us_visual_mode.group(1)
    us_body=section('us')
    if mode not in ('chart','not-applicable'):
        errors.append('data-us-visual must be chart or not-applicable')
    elif mode == 'chart':
        if not (re.search(r'<canvas\b',us_body) or re.search(r'<svg\b',us_body) or 'class="us-visual' in us_body):
            errors.append('US chart mode requires canvas, svg, or structured .us-visual')
    elif 'US_VISUAL_EXCEPTION:' not in us_body:
        errors.append('US not-applicable mode requires a specific US_VISUAL_EXCEPTION comment')
elif us_open:
    errors.append('us section missing data-us-visual="chart|not-applicable" attribute (declaration was optional before - TSM shipped without one)')

# Every chart-bearing card inside #us needs its own interpretation text, not a bare canvas/svg.
# Cards don't nest, so split on the literal card-opener and cut each chunk at the next
# top-level boundary rather than trying to div-match with regex.
if us_open:
    for chunk in re.split(r'<div class="card">', section('us'))[1:]:
        card_body = re.split(r'<div class="danger-box"', chunk)[0]
        body_minus_title = re.sub(r'<div class="card-title">.*?</div>', '', card_body, count=1, flags=re.S)
        if (re.search(r'<canvas\b', card_body) or re.search(r'<svg\b', card_body)) and len(re.sub(r'<[^>]+>', '', body_minus_title).strip()) < 20:
            errors.append('a #us chart card has no adjacent interpretation text')
invest_titles=card_titles('invest')
if len(invest_titles) != 3 or not (invest_titles[0].startswith('목표가 밴드') and invest_titles[1].startswith('5개 분석 종합') and invest_titles[2].startswith('투자의견 요약')):
    errors.append('invest card order differs from PM')
if section('invest').count('class="bb-box"') != 2: errors.append('invest must contain PM Bull/Bear pair')
if section('invest').count('class="bb-item"') != 10: errors.append('Bull/Bear must contain exactly 5 items each')

# 목표가 밴드's current-price marker must track the same price as the rest of the
# widget - this drifted stale (hand-typed, never recomputed) in PM/NVDA/GOOGL/AAPL/JNJ.
val_price_m=re.search(r'현재가 \$([\d,.]+)',section('valuation'))
band_price_m=re.search(r'현재 \$([\d,.]+)',section('invest'))
if val_price_m and band_price_m:
    vp=float(val_price_m.group(1).replace(',',''))
    bp=float(band_price_m.group(1).replace(',',''))
    if vp and abs(vp-bp)/vp > 0.005:
        errors.append(f'목표가 밴드 current price ${bp} does not match valuation-tab current price ${vp} - run scripts/target_band_gauge.py')

scenario=re.search(r'<div class="card-title">시나리오별 공정가치 분석</div>(.*?)(?=</div>\s*</div>\s*<div class="section"|</div>\s*</div>\s*<div class="disclaimer"|$)',section('valuation'),re.S)
if not scenario or scenario.group(1).count('class="scenario-card"') != 3:
    errors.append('valuation must contain exactly 3 vertical scenario cards')
if scenario and 'class="grid-3"' in scenario.group(1):
    errors.append('scenario analysis must not use grid-3')

if 'class="stage-grid"' in section('valuation'):
    mini_labels=re.findall(r'class="stage-mini-label">([^<]+)',section('valuation'))
    if mini_labels != ['매우 저평가','저평가','적정','고평가','매우 고평가']:
        errors.append('stage-mini labels must match PM wording and order')
if section('tech').count('class="ma-row"') != 4: errors.append('technical MA card must have exactly 4 rows')
if section('tech').count('class="zone-item"') != 5: errors.append('technical price-zone card must have exactly 5 PM rows')
if a.ticker != 'MSFT' and (re.search(r'\bMSFT_(?:DAILY|MA5|MA20|MA60|MA120)\b', s) or 'msftCandleSvg' in s or 'msftVolumeSvg' in s):
    errors.append('stale MSFT template identifiers found')
if re.search(r'animations\s*:\s*\{\s*y\s*:\s*\{[^}]*from',s,re.S):
    errors.append('fundamental chart uses forbidden fly-in y.from animation')

# Every canvas must be connected to a renderer; this catches blank peer/US charts.
for canvas_id in re.findall(r'<canvas id="([^"]+)"',s):
    if f"getElementById('{canvas_id}')" not in s and f'getElementById("{canvas_id}")' not in s:
        errors.append(f'canvas has no renderer binding: {canvas_id}')

# Catch canonical-template identifiers that were not renamed. PM was the original
# copy-paste source; NVDA is the current one (2026-08-08+) - check both.
if a.ticker != 'PM' and (re.search(r'\bPM_(?:DAILY|MA5|MA20|MA60|MA120)\b',s) or 'pmCandleSvg' in s or 'pmVolumeSvg' in s):
    errors.append('stale PM template identifiers found')
if a.ticker != 'NVDA' and re.search(r'\bNVDA_(?:DAILY|MA5|MA20|MA60|MA120)\b',s):
    errors.append('stale NVDA template identifiers found')
for m in re.finditer(r'<div class="val-labels">(.*?)</div>',s,re.S):
    x=m.group(1)
    if not all(c in x for c in ('val-low','val-mid','val-high')) or not re.search(r'\d',x): errors.append('non-numeric or unstyled val-labels')
for name in ('DAILY','MA5','MA20','MA60','MA120'):
    m=re.search(rf'const {re.escape(a.ticker)}_{name} = (\[.*?\]);',s,re.S)
    if not m: errors.append(f'missing array: {name}'); continue
    try:
        if len(json.loads(m.group(1))) != 252: errors.append(f'{name} length is not 252')
    except json.JSONDecodeError: errors.append(f'invalid JSON array: {name}')
style=(re.search(r'<style>(.*?)</style>',s,re.S) or ['',''])[1]
defined=set(re.findall(r'\.([A-Za-z_][\w-]*)',style))
used=set(x for raw in re.findall(r'class="([^"]+)"',s) for x in raw.split())
for x in sorted(used-defined): errors.append(f'undefined CSS class: {x}')
if s.count('<div') != s.count('</div>'): errors.append('unbalanced div tags')
manifest=json.loads((path.parents[1]/'data/manifest.json').read_text())
cur=next((x for x in manifest if x['ticker']==a.ticker),None)
if not cur: errors.append('ticker missing from manifest')
else:
    prev=next((x for x in manifest if x['rank']==cur['rank']-1),None)
    if prev:
        prev_s=(path.parents[1]/prev['page']).read_text()
        if path.name not in prev_s: errors.append(f'previous ticker {prev["ticker"]} lacks next link')
        if Path(prev['page']).name not in s: errors.append(f'new ticker lacks previous link to {prev["ticker"]}')
if errors:
    print('\n'.join('FAIL: '+e for e in errors)); sys.exit(1)
print(f'OK: {path} passes structural, data, CSS, and navigation checks')
