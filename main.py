from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import logging

# Local module for QuickBooks report pulling
import pull_reports

# Set up logger for error handling
logger = logging.getLogger("uvicorn.error")

# Initialize FastAPI app
app = FastAPI()
# ────────────────────────────────────────────────────────────────
# Pydantic models
# ────────────────────────────────────────────────────────────────
class PLItem(BaseModel):
    date: Optional[datetime]
    total: float

class BSItem(BaseModel):
    account: str
    total: float

class RTPoint(BaseModel):
    timestamp: datetime
    value: float

class Scorecard(BaseModel):
    dates: List[str]
    metrics: List[Dict[str, float]]

# ────────────────────────────────────────────────────────────────
# Helper to fetch & parse reports
# ────────────────────────────────────────────────────────────────
def get_df(report_name: str):
    try:
        raw = pull_reports.fetch_report(report_name)
        return pull_reports.parse_report(raw)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        msg = e.response.text or e.response.reason
        if status == 401:
            raise HTTPException(401, "Unauthorized: QBO token invalid or expired")
        raise HTTPException(status, f"QuickBooks API error: {msg}")
    except Exception as e:
        logger.exception(f"Error fetching/parsing report {report_name}")
        raise HTTPException(500, f"Server error parsing '{report_name}': {e}")

# ────────────────────────────────────────────────────────────────
# Profit & Loss endpoint
# ────────────────────────────────────────────────────────────────
@app.get("/api/qbo/pl", response_model=List[PLItem])
async def api_pl():
    df = get_df("ProfitAndLoss")
    cols = list(df.columns)
    if not cols:
        return []

    date_col, total_col = cols[0], cols[-1]
    items: List[PLItem] = []

    for _, row in df.iterrows():
        # parse date (if any)
        raw_date = row.get(date_col)
        try:
            date_val = datetime.fromisoformat(raw_date) if raw_date else None
        except Exception:
            date_val = None

        # parse total safely
        raw_total = row.get(total_col, "")
        try:
            total = float(raw_total) if raw_total not in (None, "") else 0.0
        except (ValueError, TypeError):
            total = 0.0

        items.append(PLItem(date=date_val, total=total))

    return items

# ────────────────────────────────────────────────────────────────
# Balance Sheet endpoint
# ────────────────────────────────────────────────────────────────
@app.get("/api/qbo/bs")
def get_balance_sheet():
    try:
        raw_json = pull_reports.fetch_report("BalanceSheet")
        print("🔍 Raw Balance Sheet JSON →", raw_json)  # ← ADD THIS
        rows = pull_reports.flatten_balance_sheet(raw_json)
        return JSONResponse(content=rows)
    except Exception as e:
        logger.exception("Error fetching Balance Sheet")
        raise HTTPException(status_code=500, detail=f"Failed to fetch balance sheet: {e}")
# ────────────────────────────────────────────────────────────────
# Real-Time Revenue via Query API
# ────────────────────────────────────────────────────────────────
@app.get("/api/qbo/realtime/revenue", response_model=List[RTPoint])
async def api_realtime_revenue():
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).date().isoformat()
    query = f"""
      SELECT TxnDate, SUM(Line.Amount) AS Total
      FROM Invoice
      WHERE TxnDate >= '{thirty_days_ago}'
      GROUP BY TxnDate
      ORDER BY TxnDate
    """
    try:
        rows = pull_reports.run_qbo_query(query)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error running QBO query for realtime revenue")
        raise HTTPException(500, f"Server error querying daily revenue: {e}")

    points: List[RTPoint] = []
    for row in rows:
        # parse date
        try:
            ts = datetime.fromisoformat(row.get("TxnDate"))
        except Exception:
            continue
        # parse amount
        raw_val = row.get("Total", "")
        try:
            val = float(raw_val) if raw_val not in (None, "") else 0.0
        except (ValueError, TypeError):
            val = 0.0

        points.append(RTPoint(timestamp=ts, value=val))

    return points

# ────────────────────────────────────────────────────────────────
# Mentor Scorecard stub
# ────────────────────────────────────────────────────────────────
@app.get("/api/qbo/scorecard/weekly", response_model=Scorecard)
async def api_scorecard_weekly():
    return Scorecard(
        dates=["2025-05-03", "2025-05-10", "2025-05-17"],
        metrics=[
            {"WeeklySales": 21000, "WeeklyNetIncome": 2600},
            {"WeeklySales": 23000, "WeeklyNetIncome": 3100},
            {"WeeklySales": 25000, "WeeklyNetIncome": 3600},
        ],
    )
