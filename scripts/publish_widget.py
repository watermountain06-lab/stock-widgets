#!/usr/bin/env python3
"""Publish a completed widget HTML into the stock-widgets repo: copy the
file into widgets/, upsert its entry in data/manifest.json, regenerate
index.html, and commit/push with the same safety rules the PlusMath
kospi10000 workflow uses (pull before starting, fetch-check right before
committing, never force-push - retry via merge on a rejected push).

Usage:
  python3 publish_widget.py REPO_DIR WIDGET_HTML_PATH \\
      --rank 11 --ticker BRK.B --name "Berkshire Hathaway" \\
      --sector Financials --accent "#c8a84b"

This only touches the working tree and git history of REPO_DIR - it never
force-pushes, and stops with a clear error if a merge conflict needs a
human to resolve it.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd, check=True):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return result


def git_pull(repo_dir):
    run(["git", "pull", "--no-rebase"], cwd=repo_dir)


def git_has_incoming_commits(repo_dir):
    run(["git", "fetch"], cwd=repo_dir)
    result = run(["git", "log", "--oneline", "HEAD..origin/main"], cwd=repo_dir, check=False)
    return bool(result.stdout.strip())


def upsert_manifest(manifest_path, entry):
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        manifest = []
    manifest = [m for m in manifest if m["ticker"] != entry["ticker"]]
    manifest.append(entry)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def build_index(repo_dir):
    sys.path.insert(0, SCRIPT_DIR)
    import build_index as build_index_mod
    build_index_mod.build(repo_dir)


def commit_and_push(repo_dir, ticker, files):
    run(["git", "add", *files], cwd=repo_dir)
    status = run(["git", "status", "--porcelain"], cwd=repo_dir)
    if not status.stdout.strip():
        print("nothing to commit (widget already up to date)")
        return

    if git_has_incoming_commits(repo_dir):
        print("remote has new commits - pulling before commit to avoid a conflicted push")
        git_pull(repo_dir)

    msg = f"Add {ticker} 분석 위젯\n\n데이터 출처: SEC EDGAR(재무제표) + Yahoo Finance(주가)"
    run(["git", "commit", "-m", msg], cwd=repo_dir)

    push = run(["git", "push"], cwd=repo_dir, check=False)
    if push.returncode != 0:
        print("push rejected - pulling (merge, not rebase) and retrying once")
        git_pull(repo_dir)
        run(["git", "push"], cwd=repo_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_dir")
    ap.add_argument("widget_html_path")
    ap.add_argument("--rank", type=int, required=True)
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--sector", required=True)
    ap.add_argument("--accent", required=True, help="hex accent color, e.g. #c8a84b")
    args = ap.parse_args()

    repo_dir = os.path.abspath(args.repo_dir)
    widgets_dir = os.path.join(repo_dir, "widgets")
    os.makedirs(widgets_dir, exist_ok=True)

    git_pull(repo_dir)

    safe_ticker = args.ticker.replace(".", "_")
    dest_filename = f"{safe_ticker}_analysis_widget.html"
    dest_path = os.path.join(widgets_dir, dest_filename)
    shutil.copyfile(args.widget_html_path, dest_path)

    entry = {
        "rank": args.rank,
        "ticker": args.ticker,
        "name": args.name,
        "sector": args.sector,
        "accentColor": args.accent,
        "page": f"widgets/{dest_filename}",
        "lastUpdated": date.today().isoformat(),
    }
    manifest_path = os.path.join(repo_dir, "data", "manifest.json")
    upsert_manifest(manifest_path, entry)
    build_index(repo_dir)

    commit_and_push(
        repo_dir, args.ticker,
        files=[f"widgets/{dest_filename}", "data/manifest.json", "index.html"],
    )


if __name__ == "__main__":
    main()
