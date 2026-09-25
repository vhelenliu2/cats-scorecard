"""Goal + pacing contract tests."""

from __future__ import annotations

from datetime import date

from cats_ingest.periods import PeriodContext
from cats_ingest.goals import resolve_goal, goal_binary_status, pacing
from cats_ingest.schema import VAL_GREEN, VAL_RED, VAL_GREY, CONFIRM


def test_unapproved_goal_is_never_paced():
    g = {"pacing_rule": "linear_quarter", "current_quarter_goal": 300,
         "approval_status": "pending"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))
    assert not res.ok and "not approved" in res.reason


def test_confirm_sentinel_blocks_pacing():
    g = {"pacing_rule": "linear_quarter", "current_quarter_goal": CONFIRM,
         "approval_status": "approved"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))
    assert not res.ok and "not confirmed" in res.reason


def test_linear_quarter_pacing():
    # As of Aug 31 in Q3 => 2 completed months (Jul, Aug) / 3.
    g = {"pacing_rule": "linear_quarter", "current_quarter_goal": 300,
         "goal_2026": 1200, "approval_status": "approved"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))
    assert res.ok
    assert abs(res.QTD_goal - 300 * (2 / 3)) < 1e-9
    assert res.goal_2026 == 1200.0


def test_oe_qoq_rate_paces_the_rate():
    # OE goal is a QoQ growth rate; QTD bar = rate * completed_months_in_quarter/3.
    g = {"pacing_rule": "oe_qoq_rate", "current_quarter_goal": 0.05,
         "goal_2026": 0.40, "approval_status": "approved"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))  # 2/3 of Q3
    assert res.ok
    assert abs(res.QTD_goal - 0.05 * (2 / 3)) < 1e-12
    assert res.goal_2026 == 0.40


def test_ltm_point_waypoint_is_not_phased():
    g = {"pacing_rule": "waypoint_interpolation", "ltm_point": True,
         "quarterly_waypoints": {"Q3 2026": 3400000}, "goal_2026": 3700000,
         "approval_status": "approved"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))
    assert res.ok
    assert res.QTD_goal == 3400000            # point target, not * fraction
    # Without ltm_point it WOULD be phased.
    g2 = dict(g); g2.pop("ltm_point")
    res2 = resolve_goal(g2, PeriodContext(date(2026, 8, 31)))
    assert abs(res2.QTD_goal - 3400000 * (2 / 3)) < 1e-6


def test_grade_map_missing_is_review():
    g = {"pacing_rule": "grade_linear", "grade_to_rank_map": None,
         "approval_status": "approved"}
    res = resolve_goal(g, PeriodContext(date(2026, 8, 31)))
    assert not res.ok and "grade_to_rank_map" in res.reason


def test_goal_binary_status():
    assert goal_binary_status(100, 90) == VAL_GREEN
    assert goal_binary_status(80, 90) == VAL_RED
    assert goal_binary_status(None, 90) == VAL_GREY
    assert goal_binary_status(80, None) == VAL_GREY


def test_pacing_ratio():
    assert abs(pacing(90, 100) - 0.9) < 1e-9
    assert pacing(90, 0) is None
    assert pacing(None, 100) is None
