"""DAUq goals from DAUq Master Sheet / Latest Forecast.

Port of hex_edits/TO_PASTE/dauq_official_targets_df.py.
Staging stores absolute users. Sheet cells are usually millions.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from dates import parse_number, planning_period, quarter_labels
from schema import make_row, mark_publishable

SECTION_TO_KEY = {
    "US": "US",
    "RoW": "ROW",
    "ROW": "ROW",
    "Global": "Total",
}

SEGMENT_DISPLAY = {
    "US": "DAUq - US (QTD), #",
    "ROW": "DAUq - ROW (QTD), #",
}


def _to_users(value: float | None) -> float | None:
    if value is None:
        return None
    if 0 < float(value) < 1000:
        return float(value) * 1_000_000
    return float(value)


def parse_dauq_sheet_goals(all_values: list[list[Any]], as_of: date) -> dict[str, Any]:
    labels = quarter_labels(as_of)
    q_row = q_col = None
    for ri, row in enumerate(all_values[:40]):
        for ci, cell in enumerate(row):
            if str(cell).strip() in labels:
                q_row, q_col = ri, ci
                break
        if q_col is not None:
            break

    goals = {"Total": None, "US": None, "ROW": None}
    meta = {
        "quarter_cell": None if q_col is None else (q_row, q_col),
        "planning_period": planning_period(as_of),
    }
    if q_col is None:
        meta["error"] = "unmatched: current-quarter label not found in first 40 rows"
        return {"goals": goals, "meta": meta}

    section = None
    for row in all_values[q_row + 1 :]:
        if len(row) <= q_col:
            continue
        label = str(row[1] if len(row) > 1 else "").strip()
        if not label:
            label = str(row[0]).strip()
        compact = label.lower().replace(" ", "")
        if "paidua" in compact or compact == "paiduaspend":
            break
        val = parse_number(row[q_col] if q_col < len(row) else None)
        if label in SECTION_TO_KEY:
            section = SECTION_TO_KEY[label]
            continue
        if label == "App" and section == "Total" and val is None:
            break
        if section and label == "Total" and val is not None:
            goals[section] = val
            if all(goals.get(k) is not None for k in ("Total", "US", "ROW")):
                break

    if goals.get("ROW") is None and goals.get("Total") is not None and goals.get("US") is not None:
        goals["ROW"] = float(goals["Total"]) - float(goals["US"])
        meta["row_derived"] = True

    users = {k: _to_users(v) for k, v in goals.items()}
    meta["sheet_millions"] = dict(goals)
    return {"goals": users, "meta": meta}


def extract_dauq_goals(
    all_values: list[list[Any]],
    *,
    as_of: date,
    catalog_row: dict[str, Any],
) -> list[dict[str, Any]]:
    parsed = parse_dauq_sheet_goals(all_values, as_of)
    goals = parsed["goals"]
    meta = parsed["meta"]
    cq = meta["planning_period"]
    tab = catalog_row.get("source_tab") or "Latest Forecast"
    total = goals.get("Total")
    unmatched = bool(meta.get("error")) or total is None
    reason = meta.get("error") or ("" if total is not None else "unmatched")
    cell = meta.get("quarter_cell")
    hint = f"{tab}!{cq} Total" + (f" r{cell[0]}c{cell[1]}" if cell else "")

    parent_common = dict(
        metric_id=catalog_row["metric_id"],
        display_name=catalog_row["display_name"],
        hex_display_name=catalog_row.get("hex_display_name") or catalog_row["display_name"],
        field_kind="goal",
        planning_period=cq,
        as_of_date=as_of,
        unit="users",
        source_id=catalog_row["source_id"],
        source_url=catalog_row["source_url"],
        source_tab=tab,
        source_cell_hint=hint,
        row_matched=not unmatched,
        value=None if unmatched else int(round(total)),
        review_reason=reason,
        confidence="review" if unmatched else "high",
    )
    # Mean metric: QTD target = CQ target (Hex calculate_qtd=False).
    out = [
        mark_publishable(make_row(**parent_common, period_type="current_quarter")),
        mark_publishable(make_row(**parent_common, period_type="qtd")),
    ]

    geos = (goals.get("US"), goals.get("ROW"), goals.get("Total"))
    incomplete = any(v is None for v in geos)
    if not incomplete and goals["Total"]:
        drift = abs((goals["US"] or 0) + (goals["ROW"] or 0) - goals["Total"])
        if drift > 100_000:
            incomplete = True
            geo_reason = f"incomplete_geo: US+ROW off Total by {int(drift)} users"
        else:
            geo_reason = ""
    else:
        geo_reason = "incomplete_geo"

    for key, display in SEGMENT_DISPLAY.items():
        val = goals.get(key)
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
                    value=None if val is None else int(round(val)),
                    unit="users",
                    source_id=catalog_row["source_id"],
                    source_url=catalog_row["source_url"],
                    source_tab=tab,
                    source_cell_hint=f"{tab}!{cq} {key} Total",
                    row_matched=val is not None,
                    confidence="review",
                    review_reason="unregistered_segment"
                    + (f"; {geo_reason}" if geo_reason else ""),
                    publish_ready=False,
                )
            )
        )
    return out
