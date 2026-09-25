"""Shopping Revenue (pacing): QTD Shopping revenue with a week-over-week check.

value = QTD Shopping revenue for the latest weekly row at/<= as_of (from the
warehouse-fed DPA/pacing tracker). The time-phased QTD goal comes from the
Shopping pacing sheet col AO (external, weekly) — handled in goals.py; a pace is
NEVER computed here without that approved external goal (build plan §4/§5).

Weekly guardrail (build plan §6 gate 12): if the latest week's QTD revenue equals
the prior week's, the current-week row likely did not update -> flag REVIEW
("NEEDS VERIFICATION"), never publish a stale pace.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from ..schema import SRC_OK
from .base import CalcContext, CalcOutput


def _as_date(v: Any) -> Optional[date]:
    try:
        return date.fromisoformat(str(v)[:10])
    except (TypeError, ValueError):
        return None


def qtd_from_weekly(rows: List[Dict[str, Any]], as_of: date) -> CalcOutput:
    """Pure core. rows: [{week: 'YYYY-MM-DD', qtd_rev_usd: float}, ...]."""
    dated = []
    for r in rows:
        d = _as_date(r.get("week"))
        v = r.get("qtd_rev_usd")
        if d is not None and v is not None and d <= as_of:
            dated.append((d, float(v)))
    if not dated:
        return CalcOutput(reason="no weekly QTD revenue row at or before as_of")
    dated.sort()
    cur_d, cur_v = dated[-1]
    out = CalcOutput(value=cur_v, as_of=cur_d.isoformat())
    if len(dated) >= 2:
        prev_d, prev_v = dated[-2]
        if cur_v == prev_v:
            out.reason = ("weekly QTD revenue unchanged vs prior week (%s == %s); col AO "
                          "current-week row may be stale -> NEEDS VERIFICATION"
                          % (prev_d.isoformat(), cur_d.isoformat()))
        else:
            out.notes.append("week-over-week check OK: %g (%s) vs %g (%s)."
                             % (cur_v, cur_d.isoformat(), prev_v, prev_d.isoformat()))
    return out


def compute(ctx: CalcContext) -> CalcOutput:
    ids = ctx.metric_spec.get("actual_sources", [])
    env = ctx.envelopes.get(ids[0]) if ids else None
    if env is None or env.source_status != SRC_OK:
        return CalcOutput(reason="Shopping tracker not read: %s"
                          % (env.error if env else "no source"))
    out = qtd_from_weekly(env.raw_rows or [], ctx.pctx.as_of)
    if out.value is not None:
        out.notes.append("QTD Shopping revenue = %g (warehouse-fed, mirrored on DPA tracker)."
                         % out.value)
    return out
