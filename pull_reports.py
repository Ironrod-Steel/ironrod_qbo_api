#!/usr/bin/env python3
"""
pull_reports.py

Fetches specified QuickBooks Online reports via the QBO API,
saves raw JSON to `raw_reports/`, and parses them into pandas DataFrames.
"""

import os
import json
import logging
import argparse
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
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

load_dotenv()  # load from .env

CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
REALM_ID      = os.getenv("REALM_ID")
REDIRECT_URI  = os.getenv("REDIRECT_URI", "http://localhost:8000/callback")
TIMEOUT       = int(os.getenv("HTTP_TIMEOUT", "30"))
MINOR_VERSION = os.getenv("MINOR_VERSION", "65")

# fail fast if anything is missing
required = {
    "CLIENT_ID": CLIENT_ID,
    "CLIENT_SECRET": CLIENT_SECRET,
    "ACCESS_TOKEN": ACCESS_TOKEN,
    "REALM_ID": REALM_ID,
}
missing = [k for k,v in required.items() if not v]
if missing:
    logger.error("Missing required env vars: %s", ", ".join(missing))
    raise SystemExit(1)

BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}"

# ──────────────────────────────────────────────────────────────────────────────
# Functions
# ──────────────────────────────────────────────────────────────────────────────

def fetch_report(name: str) -> dict:
    """
    Fetches the named report from QBO and saves the raw JSON under raw_reports/.
    """
    url = f"{BASE_URL}/reports/{name}"
    params = {"minorversion": MINOR_VERSION}
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    logger.info("Fetching report %s from %s", name, url)
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except RequestException as e:
        logger.error("Error fetching report %s: %s", name, e)
        raise

    data = resp.json()

    # ensure directory exists
    raw_dir = Path("raw_reports")
    raw_dir.mkdir(exist_ok=True)
    filepath = raw_dir / f"raw_{name.lower()}.json"
    with filepath.open("w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved raw JSON for %s to %s", name, filepath)

    return data

def parse_report(data: dict) -> pd.DataFrame:
    """
    Converts a QuickBooks report JSON into a pandas DataFrame:
    - Uses Column.ColTitle for headers
    - Recursively extracts every ColData occurrence as a row
    - Pads shorter rows with None
    """
    # 1) Extract column titles
    cols = []
    for col in data.get("Columns", {}).get("Column", []):
        title = (
            col.get("ColTitle")
            or col.get("ColumnLabel")
            or col.get("ColLabel")
            or ""
        )
        cols.append(title)

    # 2) Traverse and collect every ColData list
    rows = []
    def traverse(node):
        if isinstance(node, dict):
            if "ColData" in node and isinstance(node["ColData"], list):
                values = [cell.get("value") for cell in node["ColData"]]
                rows.append(values)
            for v in node.values():
                traverse(v)
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    traverse(data.get("Rows", {}).get("Row", []))

    # 3) Pad rows so they all match # of columns
    for i, row in enumerate(rows):
        if len(row) < len(cols):
            rows[i] = row + [None] * (len(cols) - len(row))

    df = pd.DataFrame(rows, columns=cols)
    return df

# ──────────────────────────────────────────────────────────────────────────────
# CLI & Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse QuickBooks Online reports."
    )
    parser.add_argument(
        "reports",
        nargs="*",
        default=["ProfitAndLoss", "BalanceSheet"],
        help="Names of QBO reports to pull (default: ProfitAndLoss BalanceSheet)"
    )
    args = parser.parse_args()

    for report_name in args.reports:
        data = fetch_report(report_name)
        df = parse_report(data)
        logger.info(
            "First 5 rows of %s:\n%s",
            report_name,
            df.head().to_string(index=False)
        )
    logger.info("All done!")

if __name__ == "__main__":
    main()
