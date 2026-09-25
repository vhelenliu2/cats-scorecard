"""Shopping Revenue goals from the Q{n} DPA tracker pacing sheet.

Mirrors Hex helpers in the C performance goals gsheet cell:
- CQ goal: Q{n} Goal label on the pacing tab
- Paced QTD: latest column-B week <= as_of under the $22m pacing header
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from dates import parse_date, parse_number, quarter_of

SHOPPING_PACING_SHEET_ID = "1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8"
SHOPPING_PACING_GID = 1861501712
WEEK_COL_B = 1  # column B — week-start date


def _parse_pacing_dollar(val: Any) -> float | None:
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return float(val)
    s = str(val).strip().replace(",", "").replace("$", "")
    if not s or s.lower() in ("-", "--", "n/a", "tbd"):
        return None
    num = parse_number(s)
    if num is not None:
        return num
    m = re.search(r"([\d.]+)\s*([MmBb])?", s)
    if not m:
        return None
    n = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    if suffix == "M":
        return n * 1_000_000
    if suffix == "B":
        return n * 1_000_000_000
    return n


def _parse_pacing_week_cell(val: Any) -> date | None:
    if val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        serial = float(val)
        if 40_000 <= serial <= 60_000:
            return (date(1899, 12, 30) + timedelta(days=int(serial)))
        if serial > 1e12:
            dt = datetime.utcfromtimestamp(serial / 1000.0).date()
            return dt
    s = str(val).strip()
    m = re.search(r"(?:week\s+of\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", s, re.I)
    if m:
        dt = parse_date(m.group(1))
        if dt:
            return dt
    return parse_date(val)


def _find_shopping_pacing_col(rows: list[list[Any]]) -> int | None:
    ncols = max((len(r) for r in rows[:25]), default=0)
    for j in range(ncols):
        col_bits = []
        for row in rows[:12]:
            if j < len(row):
                col_bits.append(str(row[j] or ""))
        text = " ".join(col_bits).strip().lower()
        if not text or "pacing" not in text:
            continue
        if re.search(r"22\s*m|\$22|22m", text, re.I):
            return j
    for row in rows[:25]:
        for j, cell in enumerate(row):
            text = str(cell or "").strip().lower()
            if text and "pacing" in text and re.search(r"22\s*m|\$22|22m", text, re.I):
                return j
    return None


def shopping_cq_goal_from_rows(rows: list[list[Any]], q_num: int) -> float | None:
    if not rows:
        return None
    q_label = rf"Q{q_num}\s*Goal"

    def _pick_goal_from_row(row: list[Any], start_col: int = 0) -> float | None:
        candidates = []
        for k in range(start_col, len(row)):
            v = _parse_pacing_dollar(row[k])
            if v is not None and v >= 1_000_000:
                candidates.append(v)
        return max(candidates) if candidates else None

    for ri, row in enumerate(rows[:80]):
        for j, cell in enumerate(row):
            text = str(cell or "").strip()
            if not re.search(q_label, text, re.I):
                continue
            if ":" in text:
                same_cell = _parse_pacing_dollar(text.split(":", 1)[1])
                if same_cell is not None:
                    return same_cell
            v = _pick_goal_from_row(row, j + 1)
            if v is not None:
                return v
            for dr in range(1, 4):
                if ri + dr >= len(rows):
                    break
                v = _pick_goal_from_row(rows[ri + dr])
                if v is not None:
                    return v
    ncols = max((len(r) for r in rows[:25]), default=0)
    for j in range(ncols):
        header = " ".join(
            str(rows[i][j] if j < len(rows[i]) else "") for i in range(min(10, len(rows)))
        ).strip()
        if not re.search(q_label, header, re.I):
            continue
        for row in rows:
            if len(row) <= j:
                continue
            v = _parse_pacing_dollar(row[j])
            if v is not None and v >= 1_000_000:
                return v
    return None


def shopping_paced_qtd_from_rows(
    rows: list[list[Any]], q_num: int, as_of: date
) -> tuple[float | None, date | None, int | None]:
    """Return (paced_qtd, week_start, pacing_col_index)."""
    if not rows:
        return None, None, None
    paced_col = _find_shopping_pacing_col(rows)
    if paced_col is None:
        return None, None, None
    best_val: float | None = None
    best_week: date | None = None
    for row in rows:
        if len(row) <= paced_col:
            continue
        week_dt = _parse_pacing_week_cell(row[WEEK_COL_B] if len(row) > WEEK_COL_B else None)
        if week_dt is None:
            continue
        paced = _parse_pacing_dollar(row[paced_col])
        if paced is None:
            continue
        if week_dt <= as_of and (best_week is None or week_dt >= best_week):
            best_week = week_dt
            best_val = paced
    return best_val, best_week, paced_col


def extract_shopping_goals(
    rows: list[list[Any]], *, as_of: date, q_num: int | None = None
) -> dict[str, Any]:
    q_num = q_num or quarter_of(as_of)
    cq = shopping_cq_goal_from_rows(rows, q_num)
    paced, week_start, paced_col = shopping_paced_qtd_from_rows(rows, q_num, as_of)
    return {
        "quarter": q_num,
        "as_of_date": as_of.isoformat(),
        "current_quarter": cq,
        "qtd": paced,
        "week_start": week_start.isoformat() if week_start else None,
        "pacing_col_index": paced_col,
    }
