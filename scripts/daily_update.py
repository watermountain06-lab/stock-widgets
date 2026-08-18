#!/usr/bin/env python3
"""Daily orchestration for the whole fleet: for every ticker in
data/manifest.json, fetch 5y price + 5y financials + analyst target price,
compute a PER/PBR/target-price valuation signal, patch the widget's PER/PBR
badges and 목표가 밴드 markers in place, validate, and write a digest.

This script never commits or pushes anything - it only edits files in the
working tree. The calling GitHub Actions workflow (.github/workflows/
daily_update.yml) is responsible for committing to a new branch and opening
a PR; nothing here or in that workflow pushes directly to main. See the
project plan (2026-08-17) for why that split exists.

Usage: python3 scripts/daily_update.py [--tickers AAPL,JNJ,...] [--workdir DIR]
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
DATA = REPO_ROOT / "data"

sys.path.insert(0, str(SCRIPTS))
import fetch_target_price as ftp          # noqa: E402
import compute_valuation_score as cvs     # noqa: E402
import audit_valuation_consistency as avc  # noqa: E402


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], cwd=REPO_ROOT, **kw)


def process_ticker(entry, workdir, opener, crumb):
    ticker = entry["ticker"]
    widget_path = REPO_ROOT / entry["page"]
    price_path = workdir / f"{ticker}_price_5y.json"
    fin_path = workdir / f"{ticker}_financials_5y.json"
    signal_path = workdir / f"{ticker}_signal.json"

    row = {"ticker": ticker, "status": "ok", "notes": []}

    r = run(["python3", SCRIPTS / "fetch_price.py", ticker, "--range", "5y", "--out", price_path],
            capture_output=True, text=True)
    if r.returncode != 0:
        row["status"] = "fetch_price_failed"; row["notes"].append(r.stderr.strip()[-300:]); return row

    r = run(["python3", SCRIPTS / "fetch_financials.py", ticker, "--years", "5",
             "--sp500", DATA / "sp500.json", "--out", fin_path], capture_output=True, text=True)
    if r.returncode != 0:
        row["status"] = "fetch_financials_failed"; row["notes"].append(r.stderr.strip()[-300:]); return row

    target_data = None
    if crumb:
        try:
            target_data = ftp.fetch_target_data_with_crumb(opener, crumb, ticker)
        except Exception as e:
            row["notes"].append(f"target price unavailable: {e}")
    else:
        row["notes"].append("target price skipped: no crumb this run")

    price_data = json.loads(price_path.read_text())
    fin_data = json.loads(fin_path.read_text())
    signal = cvs.compute_signal(ticker, price_data, fin_data, target_data)
    signal_path.write_text(json.dumps(signal, indent=2, ensure_ascii=False))
    row["signal"] = signal

    if not widget_path.exists():
        row["status"] = "no_widget_file"; return row

    r = run(["python3", SCRIPTS / "apply_valuation_signals.py", ticker, widget_path,
             "--signal", signal_path], capture_output=True, text=True)
    if r.returncode != 0:
        row["status"] = "apply_failed"; row["notes"].append(r.stderr.strip()[-300:]); return row
    try:
        row["applyNotes"] = json.loads(r.stdout)["notes"]
    except (json.JSONDecodeError, KeyError):
        row["applyNotes"] = [r.stdout.strip()]
    # apply_valuation_signals.py can compute a value but still fail to write
    # it (e.g. CAT/COST/LRCX use an older val-fill markup with no gradient
    # background, so the regex match count check aborts that one metric) -
    # the digest must reflect what's actually IN the file, not just what was
    # computed, or it silently overclaims (confirmed: CAT's digest once
    # showed a computed 45.54x while the widget file still said 36.8x).
    row["patchedMetrics"] = {
        metric: any(note.startswith(f"{metric}: patched") for note in row["applyNotes"])
        for metric in ("per", "pbr")
    }

    v = run(["python3", SCRIPTS / "validate_widget.py", widget_path, "--ticker", ticker],
            capture_output=True, text=True)
    if v.returncode != 0:
        row["status"] = "validation_failed"
        row["notes"].append(v.stdout.strip())
        # revert only this ticker's widget - don't let one bad patch block the rest of the fleet
        run(["git", "checkout", "--", entry["page"]])
        return row

    # The badge just moved but this pipeline deliberately never touches the
    # widget's narrative prose (out of scope - see project plan), so any
    # prose mention of PER/PBR elsewhere in the file can now be stale. Surface
    # that as a count in the digest rather than trying to auto-fix it here.
    widget_html = widget_path.read_text(encoding="utf-8")
    prose_findings = []
    for check in avc.CHECKS:
        prose_findings.extend(check(widget_html))
    row["proseSyncIssues"] = len(prose_findings)
    row["proseSyncDetails"] = [msg for _, msg in sorted(prose_findings, key=lambda x: -x[0])]
    return row


def build_digest_markdown(digest, run_date):
    lines = [f"# 정기 밸류에이션 업데이트 — {run_date}", ""]
    applied = [r for r in digest if r["status"] == "ok"]
    failed = [r for r in digest if r["status"] != "ok"]
    stage_flips = []
    for r in applied:
        sig = r.get("signal", {})
        cs = sig.get("combinedStage")
        if cs and cs in (1, 5):
            stage_flips.append((r["ticker"], cs, sig.get("combinedLabel")))

    needs_prose_sync = [r for r in applied if r.get("proseSyncIssues")]

    lines.append(f"- 총 {len(digest)}개 종목 중 {len(applied)}개 자동 반영, {len(failed)}개 제외 (아래 참고)")
    if stage_flips:
        lines.append(f"- 극단 스테이지(1 또는 5) 종목: {', '.join(f'{t}({l})' for t, _, l in stage_flips)}")
    if needs_prose_sync:
        sync_summary = ", ".join(f"{r['ticker']}({r['proseSyncIssues']}건)" for r in needs_prose_sync)
        lines.append(f"- 배지-프로즈 불일치 발견: {sync_summary} — stock-refresh로 서술문 갱신 권장")
    lines.append("")
    lines.append("## 자동 반영된 종목")
    lines.append("")
    lines.append("| 티커 | PER | PBR | 목표가 괴리율 | 종합 | 프로즈 동기화 |")
    lines.append("|---|---|---|---|---|---|")
    for r in applied:
        sig = r.get("signal", {})
        patched = r.get("patchedMetrics", {})
        tp = sig.get("targetPrice", {})
        n_issues = r.get("proseSyncIssues", 0)
        prose_cell = "✓" if not n_issues else f"⚠️ {n_issues}건"

        def cell(metric):
            m = sig.get(metric)
            if not m:
                return "-"
            if not patched.get(metric):
                return f"{m['current']}x (stage {m['stage']}, 파일 미반영*)"
            return f"{m['current']}x (stage {m['stage']})"

        lines.append(
            f"| {r['ticker']} | {cell('per')} | {cell('pbr')} "
            f"| {tp.get('upsidePct', '-')}% | {sig.get('combinedStage', '-')} {sig.get('combinedLabel', '')} "
            f"| {prose_cell} |"
        )
    if any(not r.get("patchedMetrics", {}).get(m, True) and r.get("signal", {}).get(m)
           for r in applied for m in ("per", "pbr")):
        lines.append("")
        lines.append("\\* 계산은 됐지만 파일에는 반영되지 않은 값 (예: 구형 val-fill 마크업이라 배지 패치가 스킵된 경우) - "
                      "실제 위젯은 이전 숫자 그대로입니다.")
    if needs_prose_sync:
        lines.append("")
        lines.append("### 배지-프로즈 불일치 상세")
        lines.append("")
        for r in needs_prose_sync:
            lines.append(f"- **{r['ticker']}**:")
            for detail in r.get("proseSyncDetails", []):
                lines.append(f"  - {detail}")
    if failed:
        lines.append("")
        lines.append("## 제외된 종목 (수동 확인 필요)")
        lines.append("")
        for r in failed:
            lines.append(f"- **{r['ticker']}** ({r['status']}): {'; '.join(r['notes']) or '(no detail)'}")

    lines.append("")
    lines.append("## 참고")
    lines.append("- 이 파이프라인은 PER/PBR 배지와 목표가 밴드 마커만 자동 갱신합니다. "
                  "Forward P/E, EV/EBITDA, PSR, 시나리오별 공정가치, 서술형 텍스트는 여전히 수작업입니다.")
    lines.append("- PER/PBR이 바뀐 종목은 '종합 밸류에이션', '5개 분석 종합' 등 서술형 문단이 "
                  "새 숫자와 어긋날 수 있으니, 변동폭이 큰 종목은 stock-refresh로 한 번 더 훑어보세요.")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default=None, help="comma-separated subset, default: all of manifest.json")
    ap.add_argument("--workdir", default=str(REPO_ROOT / "_daily_update_workdir"))
    args = ap.parse_args()

    manifest = json.loads((DATA / "manifest.json").read_text())
    if args.tickers:
        wanted = {t.strip().upper() for t in args.tickers.split(",")}
        manifest = [e for e in manifest if e["ticker"] in wanted]

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    jar, opener = ftp.build_opener()
    try:
        crumb = ftp.fetch_crumb(opener)
    except Exception as e:
        print(f"warning: could not obtain Yahoo crumb ({e}); "
              f"all tickers will skip the target-price component this run", file=sys.stderr)
        crumb = None

    digest = []
    for i, entry in enumerate(manifest):
        print(f"[{i+1}/{len(manifest)}] {entry['ticker']}...", file=sys.stderr)
        digest.append(process_ticker(entry, workdir, opener, crumb))
        time.sleep(0.3)

    run_date = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    digest_md = build_digest_markdown(digest, run_date)
    digest_path = REPO_ROOT / "docs" / f"daily_digest_{run_date}.md"
    digest_path.parent.mkdir(exist_ok=True)
    digest_path.write_text(digest_md)
    # stable filename for CI to point the PR body at (the dated file's name
    # isn't known until after this script runs)
    (REPO_ROOT / "docs" / "daily_digest_latest.md").write_text(digest_md)

    signals_path = DATA / "valuation_signals.json"
    signals_path.write_text(json.dumps(
        {r["ticker"]: r["signal"] for r in digest if "signal" in r}, indent=2, ensure_ascii=False))

    print(digest_md)
    print(f"Digest written to {digest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
