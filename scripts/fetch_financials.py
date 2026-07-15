#!/usr/bin/env python3
"""Pull structured financials for a US ticker from SEC EDGAR (free, no API key).

SEC EDGAR requires a descriptive User-Agent identifying the requester
(https://www.sec.gov/os/webmaster-faq#developers) - set SEC_USER_AGENT env var
or edit DEFAULT_USER_AGENT below before running at scale.

Usage: python3 fetch_financials.py TICKER [--cik CIK] [--sp500 sp500.json]
Output: JSON with last 3 annual (10-K) periods + latest quarterly (10-Q) for
revenue, operating income, net income, EPS, assets, equity, cash, dividends.
"""
import argparse
import json
import os
import sys
import time
import urllib.request

DEFAULT_USER_AGENT = "second-brain-stock-widgets gptjhss@gmail.com"

# Fallback tag lists: US GAAP tagging isn't fully standardized across filers,
# so try each concept name in order until one has data.
CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "operatingIncome": ["OperatingIncomeLoss"],
    "netIncome": ["NetIncomeLoss", "ProfitLoss"],
    "netIncomeAttributableToParent": ["NetIncomeLossAvailableToCommonStockholdersBasic", "NetIncomeLoss"],
    "epsBasic": ["EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"],
    "epsDiluted": ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"],
    "assets": ["Assets"],
    "equityAttributableToParent": ["StockholdersEquity",
                                    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue",
             "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "dividendPerShare": ["CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid"],
}

# Balance-sheet concepts are point-in-time ("instant": only an "end" date,
# no "start") rather than period durations like income-statement concepts.
INSTANT_CONCEPTS = {"assets", "equityAttributableToParent", "cash"}


def fetch_json(url, user_agent):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_cik(ticker, sp500_path):
    with open(sp500_path) as f:
        rows = json.load(f)
    for row in rows:
        if row["ticker"].upper() == ticker.upper():
            return row["cik"]
    return None


def _days(entry):
    from datetime import date
    s = date.fromisoformat(entry["start"])
    e = date.fromisoformat(entry["end"])
    return (e - s).days


def pick_annual_series(entries, n_years=3):
    """Dedupe by reporting period (start, end), not by SEC's 'fy' field.

    A single fiscal period (e.g. FY2023) is re-disclosed as a comparative
    column in every subsequent 10-K for ~2 more years, each time stamped
    with that later filing's 'fy'. Grouping by 'fy' therefore silently
    drops the actual current-year figure. Grouping by the real (start,end)
    period and keeping the latest-filed copy (in case of restatement) is
    the correct dedup key.
    """
    by_period = {}
    for e in entries:
        if e.get("form") != "10-K" or e.get("fp") != "FY":
            continue
        if "start" not in e or _days(e) < 300:  # exclude non-full-year/point-in-time facts
            continue
        key = (e["start"], e["end"])
        prev = by_period.get(key)
        if prev is None or e["filed"] > prev["filed"]:
            by_period[key] = e
    periods = sorted(by_period.keys(), key=lambda k: k[1], reverse=True)[:n_years]
    return [by_period[p] for p in sorted(periods, key=lambda k: k[1])]


def pick_annual_instants(entries, n_years=3):
    """Balance-sheet equivalent of pick_annual_series: dedupe by 'end' date
    only (no 'start'), restricted to fiscal-year-end snapshots reported in
    a 10-K, keeping the latest-filed copy of each date."""
    by_end = {}
    for e in entries:
        if e.get("form") != "10-K":
            continue
        end = e.get("end")
        if not end:
            continue
        prev = by_end.get(end)
        if prev is None or e["filed"] > prev["filed"]:
            by_end[end] = e
    ends = sorted(by_end.keys(), reverse=True)[:n_years]
    return [by_end[d] for d in sorted(ends)]


def pick_latest_quarter(entries):
    """Latest 10-Q entry by period end date.

    A single 10-Q often tags the same duration concept twice for the same
    'end' date: once as the single quarter (~90 days) and once as the
    year-to-date cumulative (~180/270 days) - e.g. Q2 net income vs H1 net
    income both ending the same day. Among ties on 'end', prefer the
    shortest duration so this returns the single-quarter figure, not YTD.
    """
    quarters = [e for e in entries if e.get("form") == "10-Q"]
    if not quarters:
        return None
    latest_end = max(e.get("end", "") for e in quarters)
    candidates = [e for e in quarters if e.get("end") == latest_end]
    if len(candidates) == 1 or "start" not in candidates[0]:
        return candidates[0]
    return min(candidates, key=_days)


def extract_concept(facts, tag_candidates, is_instant=False):
    """Try every fallback tag and keep the one with the most recent data.

    Filers change XBRL tags over time (e.g. Apple's income-statement revenue
    moved from 'Revenues' to 'RevenueFromContractWithCustomerExcludingAssessedTax'
    around ASC 606 adoption). The old tag still returns years-stale data, so
    picking the first candidate with *any* data silently returns outdated
    numbers instead of an error - must compare recency across candidates.
    """
    best = None
    for tag in tag_candidates:
        node = facts.get(tag)
        if not node:
            continue
        for unit_entries in node["units"].values():
            annual = (pick_annual_instants(unit_entries) if is_instant
                      else pick_annual_series(unit_entries))
            quarterly = pick_latest_quarter(unit_entries)
            if not annual and not quarterly:
                continue
            end_dates = [a["end"] for a in annual]
            if quarterly:
                end_dates.append(quarterly["end"])
            latest_end = max(end_dates)
            if best is None or latest_end > best[0]:
                best = (latest_end, {"tag": tag, "annual": annual, "latestQuarter": quarterly})
    if best is None:
        return {"tag": None, "annual": [], "latestQuarter": None}
    return best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("--cik", help="10-digit CIK, skips sp500.json lookup")
    ap.add_argument("--sp500", default="sp500.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    user_agent = os.environ.get("SEC_USER_AGENT", DEFAULT_USER_AGENT)

    cik = args.cik
    if not cik:
        if not os.path.exists(args.sp500):
            print(f"error: {args.sp500} not found and no --cik given; "
                  f"run sp500_list.py first or pass --cik", file=sys.stderr)
            sys.exit(1)
        cik = load_cik(args.ticker, args.sp500)
        if not cik:
            print(f"error: {args.ticker} not found in {args.sp500}; pass --cik CIK "
                  f"(look it up at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)",
                  file=sys.stderr)
            sys.exit(1)

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    data = fetch_json(url, user_agent)
    usgaap = data["facts"].get("us-gaap", {})

    result = {
        "ticker": args.ticker.upper(),
        "cik": cik,
        "entityName": data.get("entityName"),
    }
    for key, tags in CONCEPTS.items():
        result[key] = extract_concept(usgaap, tags, is_instant=key in INSTANT_CONCEPTS)

    out_path = args.out or f"{args.ticker.upper()}_financials.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {out_path}")

    # SEC fair-access guidance: keep to a reasonable request rate when looping
    # over many tickers (e.g. sleep 0.2-0.5s between calls).
    time.sleep(0.2)


if __name__ == "__main__":
    main()
