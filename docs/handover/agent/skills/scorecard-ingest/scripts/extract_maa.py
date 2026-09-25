"""MAA goals from MAB Goaling 2026 / Daily Goals Allocation.

Mirrors hex_edits/modules/tabs/company_level_goals.py lookup:
EOQ exact → last date in quarter → on-or-before EOQ.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from dates import fy_end, fy_period, parse_date, parse_number, planning_period, quarter_bounds
from schema import make_row, mark_publishable

OVERALL = "Overall"
SEGMENT_COLS = {
    "Global LCS": "MAA - Global LCS (R28D), #",
    "Global MM": "MAA - Global MM (R28D), #",
    "Global SMB": "MAA - Global SMB (R28D), #",
}


def _find_header(all_values: list[list[Any]]) -> tuple[int | None, list[str]]:
    for idx, raw in enumerate(all_values[:15]):
        cells = [str(c).strip() for c in raw]
        if "Date" in cells and OVERALL in cells:
            return idx, cells
    return None, []


def _records(all_values: list[list[Any]]) -> tuple[list[dict[str, Any]], str | None]:
    header_idx, headers = _find_header(all_values)
    if header_idx is None:
        return [], "missing_column: no Date+Overall header"
    rows: list[dict[str, Any]] = []
    for raw in all_values[header_idx + 1 :]:
        padded = list(raw) + [""] * (len(headers) - len(raw))
        rec = {headers[i]: padded[i] for i in range(len(headers))}
        dt = parse_date(rec.get("Date"))
        if dt is None:
            continue
        rec["_date"] = dt
        rec["_overall"] = parse_number(rec.get(OVERALL))
        for col in SEGMENT_COLS:
            rec[f"_{col}"] = parse_number(rec.get(col)) if col in headers else None
        rows.append(rec)
    return rows, None


def _on_or_before(rows: list[dict[str, Any]], target: date) -> dict[str, Any] | None:
    eligible = [r for r in rows if r["_date"] <= target]
    if not eligible:
        return None
    return max(eligible, key=lambda r: r["_date"])


def _eoq_row(rows: list[dict[str, Any]], q_start: date, q_end: date) -> dict[str, Any] | None:
    exact = [r for r in rows if r["_date"] == q_end]
    if exact:
        return exact[0]
    in_q = [r for r in rows if q_start <= r["_date"] <= q_end]
    if in_q:
        return max(in_q, key=lambda r: r["_date"])
    return _on_or_before(rows, q_end)


def extract_maa_goals(
    all_values: list[list[Any]],
    *,
    as_of: date,
    catalog_row: dict[str, Any],
    q_start: date | None = None,
    q_end: date | None = None,
) -> list[dict[str, Any]]:
    rows, header_err = _records(all_values)
    _, bound_start, bound_end = quarter_bounds(as_of)
    q_start = q_start or bound_start
    q_end = q_end or bound_end
    cq = planning_period(as_of)
    fy = fy_period(as_of)
    base = dict(
        metric_id=catalog_row["metric_id"],
        display_name=catalog_row["display_name"],
        hex_display_name=catalog_row.get("hex_display_name") or catalog_row["display_name"],
        field_kind="goal",
        as_of_date=as_of,
        unit=catalog_row.get("unit") or "count",
        source_id=catalog_row["source_id"],
        source_url=catalog_row["source_url"],
        source_tab=catalog_row.get("source_tab") or "Daily Goals Allocation",
    )

    def parent_row(period_type: str, planning: str, rec: dict[str, Any] | None, hint: str) -> dict[str, Any]:
        if header_err:
            return mark_publishable(
                make_row(
                    **base,
                    planning_period=planning,
                    period_type=period_type,
                    row_matched=False,
                    confidence="review",
                    review_reason=header_err,
                    source_cell_hint=hint,
                )
            )
        if rec is None or rec.get("_overall") is None:
            return mark_publishable(
                make_row(
                    **base,
                    planning_period=planning,
                    period_type=period_type,
                    row_matched=False,
                    confidence="review",
                    review_reason="late" if rec is None else "unmatched",
                    freshness_flag="late" if rec is None else "unconfirmed",
                    source_cell_hint=hint,
                )
            )
        return mark_publishable(
            make_row(
                **base,
                planning_period=planning,
                period_type=period_type,
                value=int(rec["_overall"]),
                row_matched=True,
                confidence="high",
                source_cell_hint=f"{base['source_tab']}!{rec['_date'].isoformat()} {OVERALL}",
            )
        )

    eoq = _eoq_row(rows, q_start, q_end)
    qtd = None
    exact_qtd = [r for r in rows if r["_date"] == as_of]
    qtd = exact_qtd[0] if exact_qtd else _on_or_before(rows, as_of)
    fy_row = None
    fy_target = fy_end(as_of)
    exact_fy = [r for r in rows if r["_date"] == fy_target]
    fy_row = exact_fy[0] if exact_fy else _on_or_before(rows, fy_target)

    out = [
        parent_row("current_quarter", cq, eoq, "EOQ Overall"),
        parent_row("qtd", cq, qtd, "QTD Overall"),
        parent_row("fy", fy, fy_row, "FY Overall"),
    ]

    for col, display in SEGMENT_COLS.items():
        rec = eoq
        val = rec.get(f"_{col}") if rec else None
        out.append(
            mark_publishable(
                make_row(
                    metric_id="",
                    display_name=display,
                    hex_display_name=display,
                    parent_metric_id=catalog_row["metric_id"],
                    field_kind="goal",
                    planning_period=cq,
                    period_type="current_quarter",
                    as_of_date=as_of,
                    value=None if val is None else int(val),
                    unit="count",
                    source_id=catalog_row["source_id"],
                    source_url=catalog_row["source_url"],
                    source_tab=base["source_tab"],
                    source_cell_hint=(
                        f"{base['source_tab']}!{rec['_date'].isoformat()} {col}" if rec else col
                    ),
                    row_matched=val is not None,
                    confidence="review",
                    review_reason="unregistered_segment",
                    publish_ready=False,
                )
            )
        )
    return out
