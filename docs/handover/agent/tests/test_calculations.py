"""Unit tests for the pure numeric cores of each calc module."""

from __future__ import annotations

from datetime import date

from cats_ingest.periods import PeriodContext
from cats_ingest.calculations import operational_excellence as oe
from cats_ingest.calculations import cloud_savings as cs
from cats_ingest.calculations import model_velocity as mv
from cats_ingest.calculations import experimentation_velocity as ev
from cats_ingest.calculations import ads_sota_ml as sota
from cats_ingest.calculations import revenue_fte as rf
from cats_ingest.calculations import sm_fte as fte
from cats_ingest.calculations import shopping_revenue as shop


def _approx(a, b, tol=1e-9):
    return a is not None and abs(a - b) <= tol


def test_oe_totals_and_comparisons():
    totals = {"2025-12": 100.0, "2026-06": 120.0, "2026-07": 130.0, "2026-08": 143.0}
    out = oe.oe_from_monthly_totals(totals, "2026-08", "2026-07", "2026-06")
    assert _approx(out.value, 143.0)
    assert _approx(out.MoM, 143.0 / 130.0 - 1)
    assert _approx(out.QoQ, 143.0 / 120.0 - 1)
    assert _approx(out.YoY, 143.0 / 100.0 - 1)


def test_oe_team_rows_value_is_score_and_qoq_is_reported_growth():
    columns = {"current_period": {"label": "September", "period": "2026-09"},
               "prior_reading": {"label": "July/August", "period": "prior"},
               "yoy_base": {"label": "Dec 2025", "period": "2025-12"}}
    rows = [
        {"system": "A", "September": "40.0%", "July/August": "30.0%", "Dec 2025": "20.0%"},
        {"system": "B", "September": "20.0%", "July/August": "10.0%", "Dec 2025": "10.0%"},
        {"system": "% Increase (summary)", "September": "3.63%", "_summary_row": True},
    ]
    out = oe.oe_from_team_rows(rows, columns)
    assert _approx(out.value, 60.0)                  # score = sum of team scores
    assert _approx(out.QoQ, 0.0363)                  # growth read from summary cell
    assert out.MoM is None                           # not the misleading matched-sum growth
    assert _approx(out.YoY, 60.0 / 30.0 - 1)         # same-team vs Dec 2025


def test_cloud_value_and_blank_comparisons_and_zero_vs_missing():
    out = cs.cloud_from_ytd(ytd=300.0)
    assert _approx(out.value, 300.0)
    # MoM/QoQ/YoY are intentionally blank for Cloud Savings (no date to phase).
    assert out.MoM is None and out.QoQ is None and out.YoY is None
    # real zero preserved
    z = cs.cloud_from_ytd(ytd=0.0)
    assert z.value == 0.0 and z.reason == ""
    # missing stays missing (not zero)
    m = cs.cloud_from_ytd(ytd=None)
    assert m.value is None and m.reason


def test_model_velocity_excludes_and_windows():
    pctx = PeriodContext(date(2026, 8, 15))  # Q3
    recs = [
        {"date": "2026-07-05", "impact": 3, "type": "launch"},      # qualifies
        {"date": "2026-08-01", "impact": 1, "type": "bug fix"},     # excluded
        {"date": "2026-08-02", "impact": 0, "type": "launch"},      # zero impact
        {"date": "", "impact": 5, "type": "launch"},                # undated
        {"date": "2026-06-30", "impact": 5, "type": "launch"},      # before quarter
        {"date": "2026-08-10", "impact": 2, "type": "backtest"},    # excluded
        {"date": "2026-08-12", "impact": 4, "type": "launch"},      # qualifies
    ]
    assert mv.count_qualifying_launches(recs, pctx) == 2


def test_experimentation_distinct_and_threshold():
    pctx = PeriodContext(date(2026, 8, 15))
    recs = [
        {"experiment_id": "a", "start_date": "2026-07-10", "unique_objects": 2000},
        {"experiment_id": "a", "start_date": "2026-07-11", "unique_objects": 3000},  # dup id
        {"experiment_id": "b", "start_date": "2026-08-01", "unique_objects": 500},   # below thr
        {"experiment_id": "c", "start_date": "2026-08-02", "unique_objects": 1500},
        {"experiment_id": "d", "start_date": "2026-06-01", "unique_objects": 9999},  # pre-quarter
    ]
    assert ev.count_distinct_experiments(recs, pctx) == 2  # a, c


def test_sota_latest_dated_grade():
    text = (
        "Jan 2026 readout grade: C\n"
        "Aug 2026 readout — grade B+\n"
        "old note grade A but no date on this analysis line without a year token\n"
    )
    found = sota.latest_dated_grade(text)
    assert found is not None
    d, g = found
    assert g == "B+" and d.year == 2026 and d.month == 8


def test_sm_fte_headcount_only_series():
    totals = {"2025-07": 725.0, "2026-06": 926.0, "2026-07": 958.0}
    out = fte.fte_from_series(totals, "2026-09")   # latest <= as_of is 2026-07
    assert _approx(out.value, 958.0)
    assert _approx(out.MoM, 958.0 / 926.0 - 1)      # vs prior month (Jun)
    assert _approx(out.QoQ, 958.0 / 926.0 - 1)      # vs prior quarter-end (Jun)
    assert _approx(out.YoY, 958.0 / 725.0 - 1)      # vs same month last year (Jul-25)
    assert out.as_of == "2026-07"


def test_shopping_weekly_value_and_wow_check():
    rows = [
        {"week": "2026-09-06", "qtd_rev_usd": 15800000},
        {"week": "2026-09-13", "qtd_rev_usd": 17600000},
        {"week": "2026-09-20", "qtd_rev_usd": 18000000},
        {"week": "2026-09-27", "qtd_rev_usd": 99},      # future, ignored at as_of 9/20
    ]
    out = shop.qtd_from_weekly(rows, date(2026, 9, 20))
    assert _approx(out.value, 18000000)
    assert out.as_of == "2026-09-20"
    assert out.reason == ""                             # WoW changed -> no flag
    # Unchanged current week vs prior -> NEEDS VERIFICATION.
    stale = shop.qtd_from_weekly(
        [{"week": "2026-09-13", "qtd_rev_usd": 18000000},
         {"week": "2026-09-20", "qtd_rev_usd": 18000000}], date(2026, 9, 20))
    assert stale.reason and "unchanged" in stale.reason.lower()


def test_shopping_pace_status_bands():
    from cats_ingest.goals import shopping_pace_status
    assert shopping_pace_status(90, 100) == "Green"     # >=85%
    assert shopping_pace_status(80, 100) == "Yellow"    # 70-85%
    assert shopping_pace_status(60, 100) == "Red"       # <70%
    assert shopping_pace_status(80, None) == "Grey"


def test_revenue_fte_matches_month_and_blocks_on_lag():
    # Newer revenue than headcount -> BLOCKED (no cross-month pairing).
    rev = {"2026-06": 600.0, "2026-07": 700.0, "2026-08": 800.0}
    fte = {"2026-06": 6.0, "2026-07": 7.0}  # Aug headcount missing
    out = rf.revenue_per_fte(rev, fte, "2026-08")
    assert out.blocked and out.value is None

    # Aligned months -> compute ratio + MoM.
    fte2 = {"2026-06": 6.0, "2026-07": 7.0, "2026-08": 8.0}
    out2 = rf.revenue_per_fte(rev, fte2, "2026-08")
    assert _approx(out2.value, 100.0)          # 800/8
    assert _approx(out2.MoM, 100.0 / 100.0 - 1)  # prev 700/7=100
