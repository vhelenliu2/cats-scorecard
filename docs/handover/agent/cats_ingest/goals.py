"""Goal + pacing contract (BUILD_PLAN.md §5, runbook Scale pacing rules).

A pace is NEVER computed when a goal is missing, unapproved, unit-incompatible,
or still the CONFIRM sentinel. In those cases we return a GoalResult with
ok=False and a reason, and the metric row is marked REVIEW.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import is_confirmed, goal_is_approved
from .periods import PeriodContext
from .schema import VAL_GREEN, VAL_YELLOW, VAL_RED, VAL_GREY


@dataclass
class GoalResult:
    current_quarter_goal: Optional[float] = None
    QTD_goal: Optional[float] = None
    goal_2026: Optional[float] = None
    ok: bool = False
    reason: str = ""


def _num(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def resolve_goal(goal: Dict[str, Any], pctx: PeriodContext) -> GoalResult:
    """Compute current-quarter goal + time-phased QTD goal from an approved record."""
    if not goal:
        return GoalResult(reason="no goal record configured")
    # Actual-only metrics (e.g. S+M FTE headcount) have no goal by design: they are
    # published grey. Treat as ok with no goal numbers so they are not held REVIEW.
    if goal.get("actual_only") or goal.get("pacing_rule") == "actual_only":
        return GoalResult(ok=True)
    if not goal_is_approved(goal):
        return GoalResult(reason="goal not approved (approval_status=%r)"
                          % goal.get("approval_status"))

    rule = goal.get("pacing_rule")
    g2026 = _num(goal.get("goal_2026")) if is_confirmed(goal.get("goal_2026")) else None

    if rule == "linear_quarter":
        cq = goal.get("current_quarter_goal")
        if not is_confirmed(cq):
            return GoalResult(goal_2026=g2026, reason="current_quarter_goal not confirmed")
        cqv = _num(cq)
        return GoalResult(cqv, cqv * pctx.fraction_of_quarter_elapsed, g2026, True)

    if rule == "oe_qoq_rate":
        # Operational Excellence: the goal is a QoQ GROWTH RATE (e.g. Q3 +5%).
        # QTD bar = CQ rate * (completed months in quarter / 3). Status/pace compare
        # the actual's QoQ GROWTH to this bar (not the score level) — the metric row
        # sets compare_field: QoQ so the pipeline compares the right field.
        cq = goal.get("current_quarter_goal")   # the current-quarter growth rate
        if not is_confirmed(cq):
            return GoalResult(goal_2026=g2026, reason="OE current-quarter rate not confirmed")
        cqv = _num(cq)
        return GoalResult(cqv, cqv * pctx.fraction_of_quarter_elapsed, g2026, True)

    if rule == "linear_fy_months":
        # FY-based (e.g. Cloud Savings): QTD bar = FY * completed_months/12
        fy = goal.get("goal_2026")
        if not is_confirmed(fy):
            return GoalResult(reason="goal_2026 (FY target) not confirmed")
        fyv = _num(fy)
        cq = _num(goal.get("current_quarter_goal")) if is_confirmed(goal.get("current_quarter_goal")) else None
        return GoalResult(cq, fyv * pctx.fraction_of_year_elapsed, fyv, True)

    if rule == "yoy_elapsed":
        rate = goal.get("fy_yoy_rate")
        ly = goal.get("ly_same_elapsed_count")
        if not (is_confirmed(rate) and is_confirmed(ly)):
            return GoalResult(goal_2026=g2026,
                              reason="fy_yoy_rate or ly_same_elapsed_count not confirmed")
        qtd = _num(ly) * (1 + _num(rate))
        cq = None
        lyq = goal.get("ly_full_quarter_count")
        if is_confirmed(lyq):
            cq = _num(lyq) * (1 + _num(rate))
        return GoalResult(cq, qtd, g2026, True)

    if rule == "grade_linear":
        mapping = goal.get("grade_to_rank_map")
        if not is_confirmed(mapping):
            # BUILD_PLAN.md §4: missing mapping -> REVIEW, never a guessed pace.
            return GoalResult(goal_2026=g2026,
                              reason="grade_to_rank_map not configured; SOTA pace unavailable")
        # Approved mapping present -> paced rank per runbook formula.
        expected_rank = 1.7 + 1.3 * pctx.fraction_of_year_elapsed
        return GoalResult(None, expected_rank, g2026, True,
                          reason="paced rank (map to letter grade downstream)")

    if rule == "external_weekly_paced":
        # Shopping Revenue: QTD goal is read directly from the pacing sheet col AO
        # (current-week row). It is NOT time-phased here and NEVER guessed.
        cq = _num(goal.get("current_quarter_goal")) if is_confirmed(goal.get("current_quarter_goal")) else None
        ao = goal.get("qtd_goal_col_ao")
        if not is_confirmed(ao):
            return GoalResult(cq, None, g2026, False,
                              reason="col AO current-week paced QTD goal not confirmed")
        return GoalResult(cq, _num(ao), g2026, True)

    if rule == "waypoint_interpolation":
        wps = goal.get("quarterly_waypoints")
        if not is_confirmed(wps) or not isinstance(wps, dict):
            return GoalResult(goal_2026=g2026, reason="quarterly_waypoints not confirmed")
        cq_label = pctx.quarter_label
        cqv = _num(wps.get(cq_label))
        if cqv is None:
            return GoalResult(goal_2026=g2026,
                              reason="no waypoint for %s" % cq_label)
        # LTM point targets (e.g. Revenue/FTE productivity) are compared directly to
        # the quarter's waypoint, not time-phased within the quarter.
        qtd = cqv if goal.get("ltm_point") else cqv * pctx.fraction_of_quarter_elapsed
        return GoalResult(cqv, qtd, g2026, True)

    return GoalResult(goal_2026=g2026, reason="unknown pacing_rule=%r" % rule)


def goal_binary_status(value: Optional[float], qtd_goal: Optional[float],
                       direction: str = "up") -> str:
    """runbook goal_binary: Green >=100% of paced bar, Red <100%, Grey if N/A."""
    if value is None or qtd_goal is None or qtd_goal == 0:
        return VAL_GREY
    ratio = value / qtd_goal
    if direction == "down":
        ratio = qtd_goal / value if value else 0
    return VAL_GREEN if ratio >= 1.0 else VAL_RED


def shopping_pace_status(value: Optional[float], qtd_goal: Optional[float]) -> str:
    """runbook shopping_pace: Green >=85% of paced bar, Yellow 70-85%, Red <70%."""
    if value is None or qtd_goal is None or qtd_goal == 0:
        return VAL_GREY
    ratio = value / qtd_goal
    if ratio >= 0.85:
        return VAL_GREEN
    if ratio >= 0.70:
        return VAL_YELLOW
    return VAL_RED


def status_for(status_rule: str, value: Optional[float], qtd_goal: Optional[float],
               direction: str = "up") -> str:
    """Dispatch to the metric's configured status rule (default goal_binary)."""
    if status_rule == "shopping_pace":
        return shopping_pace_status(value, qtd_goal)
    if status_rule == "grey":
        return VAL_GREY
    return goal_binary_status(value, qtd_goal, direction)


def pacing(value: Optional[float], qtd_goal: Optional[float]) -> Optional[float]:
    if value is None or qtd_goal is None or qtd_goal == 0:
        return None
    return value / qtd_goal
