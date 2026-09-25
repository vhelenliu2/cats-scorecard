"""Diff this run against last_staging.json; hold changed values for DS review."""

from __future__ import annotations

from typing import Any

from schema import row_key


def _num(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def apply_change_holds(rows: list[dict[str, Any]], previous: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not previous:
        return rows
    prev_map = {row_key(r): r for r in previous}
    out = []
    for row in rows:
        prev = prev_map.get(row_key(row))
        if prev is None:
            out.append(row)
            continue
        if not row.get("publish_ready"):
            out.append(row)
            continue
        old = _num(prev.get("value"))
        new = _num(row.get("value"))
        if old is None or new is None or old == new:
            out.append(row)
            continue
        held = dict(row)
        held["publish_ready"] = False
        held["confidence"] = "review"
        held["review_reason"] = f"value_changed: {old} → {new}"
        held["freshness_flag"] = "unconfirmed"
        out.append(held)
    return out
