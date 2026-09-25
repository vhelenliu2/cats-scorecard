"""Experimentation Velocity: QTD distinct Ads experiments with unique_objects > 1000.

Prefer approved SQL. If SQL is unavailable, use the documented manual _EXP_COUNTS
fallback ONLY when it is supplied with value, owner, timestamp, reason, and
evidence link — otherwise emit REVIEW (never a silent guess). BUILD_PLAN.md §4/§7.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from ..periods import PeriodContext, quarter_start
from ..schema import SRC_OK
from .base import CalcContext, CalcOutput

MIN_UNIQUE_OBJECTS = 1000
_REQUIRED_OVERRIDE_FIELDS = ("value", "owner", "timestamp", "reason", "evidence")


def count_distinct_experiments(records: List[Dict[str, Any]], pctx: PeriodContext) -> int:
    """Pure core. record: {experiment_id, start_date, unique_objects}."""
    qstart = quarter_start(pctx.as_of)
    seen = set()
    for rec in records:
        try:
            if float(rec.get("unique_objects", 0)) <= MIN_UNIQUE_OBJECTS:
                continue
            d = date.fromisoformat(str(rec.get("start_date"))[:10])
        except (TypeError, ValueError):
            continue
        if qstart <= d <= pctx.as_of:
            seen.add(rec.get("experiment_id"))
    return len(seen)


def _valid_override(ov: Dict[str, Any]) -> bool:
    return isinstance(ov, dict) and all(ov.get(f) for f in _REQUIRED_OVERRIDE_FIELDS)


def compute(ctx: CalcContext) -> CalcOutput:
    spec = ctx.metric_spec
    sql_ids = spec.get("actual_sources", [])
    sql_env = ctx.envelopes.get(sql_ids[0]) if sql_ids else None

    # 1) Preferred path: SQL source is OK -> count from rows.
    if sql_env is not None and sql_env.source_status == SRC_OK and not sql_env.meta.get(
            "needs_header_confirmation"):
        n = count_distinct_experiments(sql_env.raw_rows, ctx.pctx)
        return CalcOutput(value=float(n), as_of=ctx.pctx.month_label,
                          notes=["counted from approved SQL"])

    # 2) Fallback: documented _EXP_COUNTS manual override, only if fully evidenced.
    ov = spec.get("manual_override") or ctx.goal.get("manual_override")
    if _valid_override(ov):
        return CalcOutput(
            value=float(ov["value"]),
            as_of=ctx.pctx.month_label,
            reason="manual _EXP_COUNTS fallback used (SQL unavailable); needs review",
            manual_override=dict(ov),
            notes=["fallback owner=%s ts=%s" % (ov.get("owner"), ov.get("timestamp"))],
        )

    return CalcOutput(reason="Experimentation SQL unavailable and no approved "
                             "_EXP_COUNTS fallback (value/owner/timestamp/reason/"
                             "evidence) supplied.")
