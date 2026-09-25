"""Validation gates (BUILD_PLAN.md §7).

Gates never *upgrade* a row to PASS: if the calc or goal layer already flagged a
problem, the row stays REVIEW/BLOCKED. Gates can only add findings and, where a
hard invariant is violated, downgrade further.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .calculations.base import CalcOutput
from .goals import GoalResult
from .periods import PeriodContext
from .schema import (
    MetricRow, ValidationFinding, SourceEnvelope,
    V_PASS, V_REVIEW, V_BLOCKED,
    SRC_OK, SRC_STALE, SRC_MISSING, SRC_BLOCKED, SRC_ERROR,
)


def _sla_days(spec: Dict[str, Any]) -> Optional[int]:
    v = spec.get("freshness_sla_days")
    return int(v) if v is not None else None


def run_gates(row: MetricRow, calc: CalcOutput, goal_res: GoalResult,
              metric_spec: Dict[str, Any], cfg, envelopes: Dict[str, SourceEnvelope],
              pctx: PeriodContext, prev_row: Optional[Dict[str, Any]],
              tolerances: Dict[str, Any]) -> List[ValidationFinding]:
    m = row.metric
    f: List[ValidationFinding] = []

    def add(check: str, status: str, detail: str = ""):
        f.append(ValidationFinding(m, check, status, detail))

    # Gate 1: required columns/types.
    if row.value is not None and not isinstance(row.value, (int, float)):
        add("types", V_BLOCKED, "value is non-numeric")
    else:
        add("types", V_PASS)

    # Gate 2: dates parse / in window.
    if row.as_of:
        add("date_window", V_PASS, "as_of=%s" % row.as_of)
    else:
        add("date_window", V_REVIEW, "no as_of date resolved")

    # Gate 5: freshness within SLA (per source).
    fresh_status = V_PASS
    fresh_detail = []
    for sid in metric_spec.get("actual_sources", []):
        env = envelopes.get(sid)
        spec = cfg.source(sid)
        if env is None:
            fresh_status = V_REVIEW
            fresh_detail.append("%s: not read" % sid)
            continue
        if env.source_status == SRC_BLOCKED:
            fresh_status = V_BLOCKED
            fresh_detail.append("%s: blocked" % sid)
        elif env.source_status in (SRC_MISSING, SRC_ERROR):
            fresh_status = V_REVIEW if fresh_status != V_BLOCKED else fresh_status
            fresh_detail.append("%s: %s" % (sid, env.source_status))
        elif env.source_status == SRC_STALE:
            fresh_status = V_REVIEW if fresh_status != V_BLOCKED else fresh_status
            fresh_detail.append("%s: stale" % sid)
    add("freshness", fresh_status, "; ".join(fresh_detail) or "sources OK")

    # Gate 7: zero-vs-missing preserved (calc contract). If value is None with no
    # reason, that's a bug; if 0.0, that's a real zero.
    if row.value is None and not calc.reason and not calc.blocked:
        add("zero_vs_missing", V_REVIEW, "null value without a reason")
    else:
        add("zero_vs_missing", V_PASS)

    # Gate 6: row-count tolerance vs previous good run.
    if prev_row and prev_row.get("value") not in (None, "") and row.value is not None:
        try:
            prev = float(prev_row["value"])
            tol = float(tolerances.get("row_count_pct", 0.25))
            if prev != 0 and abs(row.value - prev) / abs(prev) > tol:
                add("delta_vs_prev", V_REVIEW,
                    "value moved > %.0f%% vs last good run (%.4g -> %.4g)"
                    % (tol * 100, prev, row.value))
            else:
                add("delta_vs_prev", V_PASS)
        except (TypeError, ValueError):
            add("delta_vs_prev", V_PASS)

    # Gate 9: manual override completeness.
    if calc.manual_override is not None:
        req = ("value", "owner", "timestamp", "reason", "evidence")
        missing = [k for k in req if not calc.manual_override.get(k)]
        add("manual_override", V_BLOCKED if missing else V_REVIEW,
            "missing %s" % missing if missing else "override present (needs sign-off)")

    # Gate 10: revenue & FTE same-month join.
    if m == "revenue_per_sm_fte":
        if calc.blocked:
            add("rev_fte_same_month", V_BLOCKED, calc.reason)
        elif row.value is not None:
            add("rev_fte_same_month", V_PASS, "matched %s" % row.as_of)

    # Gate 11 + goal/pace: never pace without an approved, computable goal.
    if row.pacing_to_QTD_goal is None and not goal_res.ok:
        add("goal_pacing", V_REVIEW, goal_res.reason or "no computable paced goal")
    elif row.pacing_to_QTD_goal is not None:
        add("goal_pacing", V_PASS, "pace=%.3f" % row.pacing_to_QTD_goal)

    return f


def finalize_status(calc: CalcOutput, goal_res: GoalResult,
                    findings: List[ValidationFinding]) -> (str):
    """Fold calc + gate outcomes into a single publish decision."""
    if calc.blocked or any(x.status == V_BLOCKED for x in findings):
        return V_BLOCKED
    if calc.reason or (not goal_res.ok) or any(x.status == V_REVIEW for x in findings):
        return V_REVIEW
    return V_PASS


def review_reason(calc: CalcOutput, goal_res: GoalResult,
                  findings: List[ValidationFinding]) -> str:
    bits: List[str] = []
    if calc.reason:
        bits.append(calc.reason)
    if not goal_res.ok and goal_res.reason:
        bits.append("goal: " + goal_res.reason)
    for x in findings:
        if x.status in (V_REVIEW, V_BLOCKED) and x.detail:
            bits.append("%s: %s" % (x.check, x.detail))
    # de-dup while preserving order
    seen, out = set(), []
    for b in bits:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return " | ".join(out)
