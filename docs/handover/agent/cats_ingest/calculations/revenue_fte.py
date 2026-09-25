"""Revenue / S+M FTE: revenue divided by matched-month headcount.

Never pair newer revenue with older headcount: use the latest month for which
BOTH revenue and FTE exist. If the latest revenue month has no FTE, the metric
is BLOCKED for that period (BUILD_PLAN.md §4/§7/§12 failed-run example).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..periods import PeriodContext
from ..schema import SRC_OK
from .base import CalcContext, CalcOutput, pct_change


def _prior_month(period: str) -> str:
    y, m = int(period[:4]), int(period[5:7])
    m -= 1
    if m == 0:
        y, m = y - 1, 12
    return "%04d-%02d" % (y, m)


def revenue_per_fte(rev_by_month: Dict[str, float], fte_by_month: Dict[str, float],
                    as_of_period: str) -> CalcOutput:
    """Pure core. Returns BLOCKED output if newest revenue month lacks FTE."""
    if not rev_by_month:
        return CalcOutput(reason="no revenue data")
    latest_rev = max(rev_by_month)
    matched = sorted(m for m in rev_by_month if m in fte_by_month and rev_by_month[m] is not None
                     and fte_by_month[m] not in (None, 0))
    if not matched:
        return CalcOutput(reason="no month has both revenue and FTE", blocked=True)
    period = matched[-1]
    if latest_rev > period:
        # newer revenue exists but its headcount hasn't landed -> do not pair.
        return CalcOutput(
            reason="FTE behind revenue: revenue has %s but latest matched month is %s; "
                   "not pairing newer revenue with older headcount" % (latest_rev, period),
            blocked=True,
        )

    def ratio(p: str) -> Optional[float]:
        if p in rev_by_month and p in fte_by_month and fte_by_month[p]:
            return rev_by_month[p] / fte_by_month[p]
        return None

    value = ratio(period)
    prev_m = _prior_month(period)
    return CalcOutput(
        value=value,
        MoM=pct_change(value, ratio(prev_m)),
        as_of=period,
        notes=["matched month %s (LTM headcount)" % period],
    )


def compute(ctx: CalcContext) -> CalcOutput:
    ids = ctx.metric_spec.get("actual_sources", [])
    envs = [ctx.envelopes.get(i) for i in ids]
    for i, e in zip(ids, envs):
        if e is None or e.source_status != SRC_OK or e.meta.get("needs_header_confirmation"):
            reason = e.error if e else "not read"
            status = e.source_status if e else "MISSING"
            return CalcOutput(reason="source %r status=%s: %s" % (i, status, reason))
    return CalcOutput(reason="Rev/FTE parse requires confirmed month/revenue/FTE columns "
                             "and a registered warehouse runner. Confirm, then enable parse.")
