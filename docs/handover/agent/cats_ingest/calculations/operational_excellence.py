"""Operational Excellence: sum of team scores at latest completed month-end.

MoM/QoQ/YoY are same-team % change vs prior month / prior quarter-end / Dec 2025
(runbook Scale actuals table). "Same-team" is enforced by summing each pair of
periods over the intersection of teams that report a numeric score in BOTH
periods — otherwise a team appearing/leaving would distort the ratio.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .base import CalcContext, CalcOutput, require_ok, pct_change

YOY_BASE_PERIOD = "2025-12"     # runbook: YoY vs December 2025


def oe_from_monthly_totals(totals: Dict[str, float], current_period: str,
                           prior_month: str, prior_quarter_end: str) -> CalcOutput:
    """Pure core. `totals` maps 'YYYY-MM' -> summed team score."""
    value = totals.get(current_period)
    if value is None:
        return CalcOutput(reason="no team-score total for %s" % current_period)
    return CalcOutput(
        value=value,
        MoM=pct_change(value, totals.get(prior_month)),
        QoQ=pct_change(value, totals.get(prior_quarter_end)),
        YoY=pct_change(value, totals.get(YOY_BASE_PERIOD)),
        as_of=current_period,
    )


def parse_score(v: Any) -> Optional[float]:
    """'44.3%' -> 44.3 ; '0.0%' -> 0.0 (real zero) ; '' / '#N/A' / grade text -> None.

    Scores are kept as percentage points (scale-invariant for the ratios below).
    Non-numeric grade text ("No Tier-1 Service", "Level 1 Complete") is *not* a
    score and returns None so it is skipped, never coerced to 0.
    """
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.upper() in ("#N/A", "N/A", "NA"):
        return None
    if s.endswith("%"):
        s = s[:-1].strip()
    try:
        return float(s)
    except ValueError:
        return None


def _matched_sums(rows: List[Dict[str, Any]], a_label: str,
                  b_label: str) -> Tuple[Optional[float], Optional[float], int]:
    """Sum (a, b) over teams whose score is numeric in BOTH periods (same-team)."""
    a_tot = b_tot = 0.0
    n = 0
    for r in rows:
        if r.get("_summary_row"):
            continue
        a = parse_score(r.get(a_label))
        b = parse_score(r.get(b_label))
        if a is None or b is None:
            continue
        a_tot += a
        b_tot += b
        n += 1
    if n == 0:
        return None, None, 0
    return a_tot, b_tot, n


def oe_from_team_rows(rows: List[Dict[str, Any]], columns: Dict[str, Any]) -> CalcOutput:
    """Pure core over transcribed team rows + the period-column descriptor.

    `columns` shape (from the source export):
        current_period / prior_reading / yoy_base -> {label, period}
    """
    cur = columns.get("current_period", {}) or {}
    prior = columns.get("prior_reading", {}) or {}
    yoy = columns.get("yoy_base", {}) or {}
    cur_label = cur.get("label")
    prior_label = prior.get("label")
    yoy_label = yoy.get("label")
    if not cur_label:
        return CalcOutput(reason="current-period column label missing in export")

    # Headline value: sum of ALL teams with a numeric current-month score
    # (skip summary rows + non-numeric grade text). Real 0.0 is preserved.
    value = None
    n_teams = 0
    for r in rows:
        if r.get("_summary_row"):
            continue
        s = parse_score(r.get(cur_label))
        if s is None:
            continue
        value = (value or 0.0) + s
        n_teams += 1
    if value is None:
        return CalcOutput(reason="no numeric team scores for current period %r" % cur_label)

    # value = the OE SCORE level (sum of team scores). The row also carries the QoQ
    # GROWTH below, so it contains BOTH the score and the growth the goal targets.
    out = CalcOutput(value=value, as_of=cur.get("period"))
    out.notes.append("Value = OE score = sum of %d team scores for %s (summary rows + "
                     "non-numeric grades skipped)." % (n_teams, cur_label))

    # QoQ growth: read the sheet's own reported "% Increase" summary cell — this is
    # the growth figure the dashboard tracks and the +N% rate goal compares against.
    reported = _reported_growth(rows, cur_label)
    if reported is not None:
        out.QoQ = reported / 100.0                # percent -> fraction
        out.notes.append("QoQ growth = %.2f%% read from the sheet's reported "
                         "'%% Increase' summary cell (the figure the +N%% rate goal "
                         "compares to)." % reported)
    else:
        out.notes.append("QoQ growth blank: no reported '%% Increase' summary cell found.")

    # YoY: same-team score change vs Dec 2025 (informational vs the FY +40% frame).
    if yoy_label:
        a, b, n = _matched_sums(rows, cur_label, yoy_label)
        out.YoY = pct_change(a, b)
        out.notes.append("YoY = same-team score change vs %r over %d matched teams." %
                         (yoy_label, n))

    # MoM left blank: the same-team sum change vs the combined prior reading is not a
    # clean month-over-month and would mislead next to the reported QoQ growth.
    out.MoM = None
    return out


def _reported_growth(rows, cur_label) -> Optional[float]:
    """Return the sheet's reported '% Increase' from the summary row (percent points)."""
    for r in rows:
        if r.get("_summary_row"):
            g = parse_score(r.get(cur_label))
            if g is not None:
                return g
    return None


def compute(ctx: CalcContext) -> CalcOutput:
    gate = require_ok(ctx, ctx.metric_spec.get("actual_sources", []))
    if gate is not None:
        return gate

    sid = (ctx.metric_spec.get("actual_sources") or [None])[0]
    env = ctx.envelopes.get(sid)
    if env is None:
        return CalcOutput(reason="OE source %r not read" % sid)
    columns = (env.meta or {}).get("columns", {})
    if not columns:
        return CalcOutput(reason="OE export missing 'columns' period descriptor; "
                                 "confirm month/score columns with Nikhil.")
    return oe_from_team_rows(env.raw_rows or [], columns)
