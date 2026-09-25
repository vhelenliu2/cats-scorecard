"""Quarter / date helpers. Q1=90/91, Q2=91, Q3=92, Q4=92 calendar days."""

from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y/%m/%d",
        "%d-%b-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_number(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"n/a", "na", "-", "none", "#n/a"}:
        return None
    for sep in ("<<<", "#", "("):
        if sep in text:
            text = text.split(sep, 1)[0].strip()
    text = (
        text.replace(",", "")
        .replace("$", "")
        .replace("%", "")
        .replace("+", "")
        .strip()
    )
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def quarter_of(as_of: date) -> int:
    return (as_of.month - 1) // 3 + 1


def quarter_bounds(as_of: date) -> tuple[int, date, date]:
    qnum = quarter_of(as_of)
    start_month = (qnum - 1) * 3 + 1
    start = date(as_of.year, start_month, 1)
    if qnum == 4:
        end = date(as_of.year, 12, 31)
    else:
        nxt = date(as_of.year, start_month + 3, 1)
        end = nxt - timedelta(days=1)
    return qnum, start, end


def planning_period(as_of: date) -> str:
    qnum, _, _ = quarter_bounds(as_of)
    return f"Q{qnum} {as_of.year}"


def fy_period(as_of: date) -> str:
    return f"FY {as_of.year}"


def fy_end(as_of: date) -> date:
    return date(as_of.year, 12, 31)


def quarter_labels(as_of: date) -> set[str]:
    qnum, _, _ = quarter_bounds(as_of)
    yy = str(as_of.year)[-2:]
    return {
        f"Q{qnum} {as_of.year}",
        f"Q{qnum}'{yy}",
        f"Q{qnum}/{as_of.year}",
    }
