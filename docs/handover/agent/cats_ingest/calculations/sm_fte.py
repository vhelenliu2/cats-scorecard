"""S+M FTE: latest-month Sales+Marketing headcount from the HC forecast sheet.

Per the build plan (AGENTS.md §3/§4) this metric is HEADCOUNT-ONLY: there is no
revenue join / ratio (revenue lives in the warehouse and is out of scope). It is
actual-only, status grey until a headcount goal is approved. Comparisons are made
on the monthly headcount series:
  MoM = vs prior month, QoQ = vs prior quarter-end month, YoY = vs same month last year.
"""

from __future__ import annotations

from typing import Dict, Optional

from .base import CalcContext, CalcOutput, require_ok, pct_change


def _prior_month(period: str) -> str:
    y, m = int(period[:4]), int(period[5:7])
    m -= 1
    if m == 0:
        y, m = y - 1, 12
    return "%04d-%02d" % (y, m)


def _prior_quarter_end_month(period: str) -> str:
    """Last month of the quarter before `period`'s quarter (e.g. 2026-07 -> 2026-06)."""
    y, m = int(period[:4]), int(period[5:7])
    q = (m - 1) // 3 + 1
    end_month = 3 * (q - 1)          # 0,3,6,9
    if end_month == 0:
        return "%04d-12" % (y - 1)
    return "%04d-%02d" % (y, end_month)


def _same_month_prior_year(period: str) -> str:
    return "%04d-%s" % (int(period[:4]) - 1, period[5:7])


def fte_from_series(totals: Dict[str, float], as_of_period: str) -> CalcOutput:
    """Pure core. `totals` maps 'YYYY-MM' -> S+M total headcount."""
    if not totals:
        return CalcOutput(reason="no headcount series")
    available = sorted(m for m in totals if m <= as_of_period and totals[m] is not None)
    if not available:
        return CalcOutput(reason="no headcount month at or before %s" % as_of_period)
    period = available[-1]
    value = float(totals[period])

    def val(p: str) -> Optional[float]:
        v = totals.get(p)
        return float(v) if v is not None else None

    out = CalcOutput(
        value=value,
        MoM=pct_change(value, val(_prior_month(period))),
        QoQ=pct_change(value, val(_prior_quarter_end_month(period))),
        YoY=pct_change(value, val(_same_month_prior_year(period))),
        as_of=period,
    )
    out.notes.append("Latest S+M headcount month = %s (%g). Headcount-only per build "
                     "plan; no revenue join. Status grey (no approved headcount goal)."
                     % (period, value))
    return out


def compute(ctx: CalcContext) -> CalcOutput:
    gate = require_ok(ctx, ctx.metric_spec.get("actual_sources", []))
    if gate is not None:
        return gate
    sid = (ctx.metric_spec.get("actual_sources") or [None])[0]
    env = ctx.envelopes.get(sid)
    totals = (env.meta or {}).get("monthly_totals", {}) if env else {}
    if not totals:
        return CalcOutput(reason="HC export missing 'monthly_totals'; confirm the "
                                 "S+M Total series with Nick Asaad.")
    return fte_from_series(totals, ctx.pctx.month_label)
