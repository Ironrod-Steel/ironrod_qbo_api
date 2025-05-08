#!/usr/bin/env python3
"""
pull_reports.py

Fetches specified QuickBooks Online reports via the QBO API,
auto-refreshes expired tokens, saves raw JSON to `raw_reports/`,
parses them into pandas DataFrames, and provides a helper to run QBO SQL-style queries.
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Union, Optional
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError
from dotenv import load_dotenv
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# Configuration & Logging
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Environment
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()

CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
REALM_ID      = os.getenv("REALM_ID")
TIMEOUT       = int(os.getenv("HTTP_TIMEOUT", "30"))
MINOR_VERSION = os.getenv("MINOR_VERSION", "65")

# fail fast if anything critical is missing
required = {
    "CLIENT_ID": CLIENT_ID,
    "CLIENT_SECRET": CLIENT_SECRET,
    "ACCESS_TOKEN": ACCESS_TOKEN,
    "REFRESH_TOKEN": REFRESH_TOKEN,
    "REALM_ID": REALM_ID,
}
missing = [k for k, v in required.items() if not v]
if missing:
    logger.error("Missing required env vars: %s", ", ".join(missing))
    raise SystemExit(1)

# allow switching between sandbox and production via .env
QBO_BASE = os.getenv(
    "QBO_BASE_URL",
    "https://sandbox-quickbooks.api.intuit.com/v3/company"
)
BASE_URL = f"{QBO_BASE}/{REALM_ID}"

def _make_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json"
    }

# initialize headers
HEADERS = _make_headers(ACCESS_TOKEN)

# ──────────────────────────────────────────────────────────────────────────────
# Auth Helper
# ──────────────────────────────────────────────────────────────────────────────
def refresh_access_token() -> Union[str, None]:
    global ACCESS_TOKEN, REFRESH_TOKEN, HEADERS
    """
    Uses the REFRESH_TOKEN to obtain a fresh ACCESS_TOKEN (and REFRESH_TOKEN),
    updates module-level vars and writes them back to .env for persistence.
    """
    token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    params = {
        "grant_type":    "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    resp = requests.post(
        token_url,
        headers={"Accept": "application/json"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        data=params,
        timeout=TIMEOUT
    )
    resp.raise_for_status()
    creds = resp.json()
    new_access = creds["access_token"]
    new_refresh = creds.get("refresh_token", REFRESH_TOKEN)

    ACCESS_TOKEN  = new_access
    REFRESH_TOKEN = new_refresh
    HEADERS       = _make_headers(ACCESS_TOKEN)

    # persist to .env
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        lines = env_path.read_text().splitlines()
        with env_path.open("w") as f:
            for line in lines:
                if line.startswith("ACCESS_TOKEN="):
                    f.write(f"ACCESS_TOKEN={new_access}\n")
                elif line.startswith("REFRESH_TOKEN="):
                    f.write(f"REFRESH_TOKEN={new_refresh}\n")
                else:
                    f.write(line + "\n")
        logger.info("Wrote new tokens to .env")

    logger.info("Refreshed QBO access token")
    return new_access

# ──────────────────────────────────────────────────────────────────────────────
# Fetching
# ──────────────────────────────────────────────────────────────────────────────
def fetch_report(name: str) -> dict:
    """
    Fetches the named report from QBO and returns the JSON,
    saving a copy to raw_reports/ and auto-refreshing tokens on 401.
    """
    url = f"{BASE_URL}/reports/{name}"
    params = {"minorversion": MINOR_VERSION}

    logger.info("Fetching report %s from %s", name, url)
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        if resp.status_code == 401:
            refresh_access_token()
            resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except HTTPError as e:
        logger.error("HTTP error fetching report %s: %s", name, e)
        raise
    except RequestException as e:
        logger.error("Network error fetching report %s: %s", name, e)
        raise

    data = resp.json()
    if not isinstance(data, dict):
        logger.error("Unexpected JSON structure for %s: %r", name, data)
        raise ValueError(f"Invalid JSON for report {name}")

    # save raw JSON
    raw_dir = Path("raw_reports")
    raw_dir.mkdir(exist_ok=True)
    path = raw_dir / f"raw_{name.lower()}.json"
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved raw JSON to %s", path)

    return data

# ──────────────────────────────────────────────────────────────────────────────
# Parsing
# ──────────────────────────────────────────────────────────────────────────────
def parse_report(data: dict) -> pd.DataFrame:
    """
    Parses a QBO report JSON into a pandas DataFrame:
    - Extracts headers from Columns metadata.
    - Recursively collects all ColData rows.
    - Pads rows to match header length.
    """
    # headers
    cols_meta = data.get("Columns", {}).get("Column", [])
    headers = [
        col.get("ColTitle") or col.get("ColumnLabel") or col.get("ColLabel") or ""
        for col in cols_meta
    ]

    # collect rows
    rows: List[List] = []
    def collect(node):
        if isinstance(node, dict):
            if "ColData" in node and isinstance(node["ColData"], list):
                rows.append([c.get("value") for c in node["ColData"]])
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for item in node:
                collect(item)

    collect(data.get("Rows", {}).get("Row", []))

    # pad rows
    for i, r in enumerate(rows):
        if len(r) < len(headers):
            rows[i] = r + [None] * (len(headers) - len(r))

    return pd.DataFrame(rows, columns=headers)

def flatten_balance_sheet(data: dict) -> List[Dict[str, float]]:
    out = []

    def walk_rows(rows: List[Dict]):
        for row in rows:
            if "ColData" in row and row.get("type") == "Data":
                coldata = row["ColData"]
                if len(coldata) >= 2:
                    label = coldata[0].get("value", "").strip()
                    value = coldata[1].get("value", "")
                    try:
                        out.append({"account": label, "total": float(value)})
                    except ValueError:
                        continue
            elif "Rows" in row:
                walk_rows(row["Rows"].get("Row", []))

    top_rows = data.get("Rows", {}).get("Row", [])
    walk_rows(top_rows)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Query Helper
# ──────────────────────────────────────────────────────────────────────────────
def run_qbo_query(query: str) -> List[Dict[str, str]]:
    """
    Executes a QBO SQL-style query and returns list of row dicts.
    """
    url = f"{BASE_URL}/query"
    params = {"query": query, "minorversion": MINOR_VERSION}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("QueryResponse", {}).get("Invoice", [])

# ──────────────────────────────────────────────────────────────────────────────
# CLI & Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Pull & parse QBO reports")
    parser.add_argument(
        "reports", nargs="*", default=["ProfitAndLoss", "BalanceSheet"],
        help="Names of QuickBooks report(s) to fetch"
    )
    args = parser.parse_args()

    for name in args.reports:
        data = fetch_report(name)
        df = parse_report(data)
        logger.info("Top 5 rows of %s:\n%s", name, df.head().to_string(index=False))
    logger.info("All reports fetched!")

if __name__ == "__main__":
    main()