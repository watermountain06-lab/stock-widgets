#!/usr/bin/env python3
"""Validate structure, data arrays, CSS classes, and two-way navigation."""
import argparse, json, re, sys
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('widget'); p.add_argument('--ticker',required=True); a=p.parse_args()
path=Path(a.widget); s=path.read_text(); errors=[]
for tab in ('tech','fund','valuation','us','news','invest'):
    if f'id="{tab}"' not in s: errors.append(f'missing tab: {tab}')
for text in ('다음 실적 체크포인트','Per-Share','S&P 500 대비','목표가 밴드','5개 분석 종합','투자의견 요약'):
    if text not in s: errors.append(f'missing block: {text}')
if s.count('class="val-item"') != 5: errors.append('valuation list must contain exactly 5 val-items')
if s.count('class="stage-grid"') != 1: errors.append('valuation must contain exactly one stage-grid')
if s.count('class="tl-item"') < 5: errors.append('timeline must contain at least 5 events')
if re.search(r'tl-dot (?:blue|orange|teal|yellow)',s): errors.append('ad-hoc timeline color class')
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
