#!/usr/bin/env python3
"""Fetch the 6 macro indicators shown above the gallery search bar.

Sources (both free, no API key/signup required):
- Yahoo Finance chart API: S&P500 (^GSPC), VIX (^VIX), USD/KRW (KRW=X)
- FRED public CSV export (no key needed, unlike the FRED REST API):
  https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES_ID>
  Series: FEDFUNDS (effective fed funds rate), UNRATE (unemployment rate),
  CPIAUCSL (CPI index level, used to compute YoY % ourselves).

FOMC meeting dates aren't available via any free API - the Fed publishes
the full-year schedule as a press release, not a machine-readable feed - so
the 2026 dates are hardcoded from https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
and must be updated by hand once the 2027 schedule is announced (typically
each August for the following year).

Usage: python3 fetch_macro.py [output_path]
"""
import csv
import io
import json
import sys
import urllib.request
from datetime import date, datetime, timezone

FOMC_2026_MEETINGS = [
    ("2026-01-27", "2026-01-28"),
    ("2026-03-17", "2026-03-18"),
    ("2026-04-28", "2026-04-29"),
    ("2026-06-16", "2026-06-17"),
    ("2026-07-28", "2026-07-29"),
    ("2026-09-15", "2026-09-16"),
    ("2026-10-27", "2026-10-28"),
    ("2026-12-08", "2026-12-09"),
]

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1d"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def fetch_yahoo_latest(ticker):
    req = urllib.request.Request(
        YAHOO_CHART_URL.format(ticker=ticker), headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = data["chart"]["result"][0]
    closes = result["indicators"]["quote"][0]["close"]
    timestamps = result["timestamp"]
    # Walk backwards past any trailing nulls (holidays/intraday gaps).
    for i in range(len(closes) - 1, -1, -1):
        if closes[i] is not None:
            latest = closes[i]
            prev = next((closes[j] for j in range(i - 1, -1, -1) if closes[j] is not None), None)
            as_of = datetime.fromtimestamp(timestamps[i], tz=timezone.utc).strftime("%Y-%m-%d")
            change_pct = round((latest - prev) / prev * 100, 2) if prev else None
            return {"value": round(latest, 2), "changePct": change_pct, "asOf": as_of}
    raise ValueError(f"no usable data for {ticker}")


def fetch_fred_series(series_id):
    req = urllib.request.Request(
        FRED_CSV_URL.format(series_id=series_id), headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(raw)))
    header, data_rows = rows[0], rows[1:]
    # rows are (date, value); FRED uses "." for missing observations, and
    # trailing/blank lines can produce rows with fewer than 2 columns.
    parsed = [(r[0], float(r[1])) for r in data_rows if len(r) == 2 and r[1] not in ("", ".")]
    return parsed  # chronological order, oldest first


def cpi_yoy(cpi_series):
    latest_date, latest_val = cpi_series[-1]
    latest_dt = datetime.strptime(latest_date, "%Y-%m-%d")
    target_year_month = (latest_dt.year - 1, latest_dt.month)
    year_ago = next(
        (v for d, v in cpi_series if datetime.strptime(d, "%Y-%m-%d").year == target_year_month[0]
         and datetime.strptime(d, "%Y-%m-%d").month == target_year_month[1]),
        None,
    )
    if year_ago is None:
        raise ValueError("could not find CPI value from 12 months ago")
    yoy_pct = round((latest_val - year_ago) / year_ago * 100, 1)
    return {"value": yoy_pct, "asOf": latest_date}


def next_fomc_meeting(today=None):
    today = today or date.today()
    for start, end in FOMC_2026_MEETINGS:
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        if end_date >= today:
            return {"start": start, "end": end}
    return None  # 2027 schedule not yet hardcoded


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "macro.json"

    sp500 = fetch_yahoo_latest("%5EGSPC")
    vix = fetch_yahoo_latest("%5EVIX")
    usdkrw = fetch_yahoo_latest("KRW=X")

    fedfunds = fetch_fred_series("FEDFUNDS")
    unrate = fetch_fred_series("UNRATE")
    cpi = fetch_fred_series("CPIAUCSL")

    fedfunds_latest = {"value": fedfunds[-1][1], "asOf": fedfunds[-1][0]}
    unrate_latest = {"value": unrate[-1][1], "asOf": unrate[-1][0]}
    cpi_yoy_latest = cpi_yoy(cpi)
    fomc_next = next_fomc_meeting()

    macro = {
        "generatedAt": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sp500": sp500,
        "vix": vix,
        "usdkrw": usdkrw,
        "fedFunds": fedfunds_latest,
        "nextFomcMeeting": fomc_next,
        "unemploymentRate": unrate_latest,
        "cpiYoy": cpi_yoy_latest,
    }

    with open(out_path, "w") as f:
        json.dump(macro, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps(macro, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
