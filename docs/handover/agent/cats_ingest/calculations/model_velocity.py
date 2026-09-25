"""Model Velocity: QTD count of qualifying launches across Ranking+Retrieval+Shopping.

Qualifying = launch with >0 impact, excluding bug fixes, backtests, deprecations,
zero-valued and undated records (runbook / BUILD_PLAN.md §4).
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from ..periods import PeriodContext, quarter_start
from .base import CalcContext, CalcOutput, require_ok

_EXCLUDE_MARKERS = ("bug fix", "bugfix", "backtest", "deprecat")


def _is_qualifying(rec: Dict[str, Any]) -> bool:
    kind = " ".join(str(rec.get(k, "")) for k in ("type", "category", "notes", "name")).lower()
    if any(m in kind for m in _EXCLUDE_MARKERS):
        return False
    # Only launched work counts. If a status is present it must start with "launch"
    # (Launched); In-progress / Not Started / etc. are excluded.
    status = rec.get("status")
    if status is not None and not str(status).strip().lower().startswith("launch"):
        return False
    impact = rec.get("impact")
    try:
        if impact is None or float(impact) <= 0:
            return False
    except (TypeError, ValueError):
        return False
    if not rec.get("date"):        # undated dropped
        return False
    return True


def count_qualifying_launches(records: List[Dict[str, Any]], pctx: PeriodContext) -> int:
    """Pure core. Each record: {date: 'YYYY-MM-DD', impact: float, type/notes:str}."""
    qstart = quarter_start(pctx.as_of)
    n = 0
    for rec in records:
        if not _is_qualifying(rec):
            continue
        try:
            d = date.fromisoformat(str(rec["date"])[:10])
        except ValueError:
            continue
        if qstart <= d <= pctx.as_of:
            n += 1
    return n


def compute(ctx: CalcContext) -> CalcOutput:
    source_ids = ctx.metric_spec.get("actual_sources", [])
    gate = require_ok(ctx, source_ids)
    if gate is not None:
        return gate
    # Aggregate launch records across all three trackers (Ranking + Retrieval + Shopping).
    records: List[Dict[str, Any]] = []
    per_source = []
    for sid in source_ids:
        env = ctx.envelopes.get(sid)
        rows = list(env.raw_rows) if env and env.raw_rows else []
        records.extend(rows)
        per_source.append("%s=%d rows" % (sid, len(rows)))
    n = count_qualifying_launches(records, ctx.pctx)
    out = CalcOutput(value=float(n), as_of=ctx.pctx.month_label)
    out.notes.append("QTD qualifying launches = %d across %d trackers (%s). Qualifying = "
                     "Launched, dated within the quarter and <= as_of, impact>0; excludes "
                     "bug fixes, backtests, deprecations, zero/negative-impact, undated."
                     % (n, len(source_ids), "; ".join(per_source)))
    out.notes.append("MoM/QoQ/YoY blank: launch trackers carry no prior-period launch "
                     "counts in this export to phase against (not guessed).")
    return out
