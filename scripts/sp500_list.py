#!/usr/bin/env python3
"""Fetch current S&P 500 constituent list (ticker, name, GICS sector, CIK).

Source: https://github.com/datasets/s-and-p-500-companies (free, no key,
community-maintained, tracks index changes). Writes data/sp500.json for the
site's index.html to consume.

Usage: python3 sp500_list.py [output_path]
"""
import csv
import io
import json
import sys
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"


def fetch_sp500():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(raw)))
    out = []
    for row in rows:
        out.append({
            "ticker": row["Symbol"].strip(),
            "name": row["Security"].strip(),
            "sector": row["GICS Sector"].strip(),
            "subIndustry": row["GICS Sub-Industry"].strip(),
            "cik": row["CIK"].strip().zfill(10),
        })
    return out


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "sp500.json"
    data = fetch_sp500()
    with open(out_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(data)} companies to {out_path}")
