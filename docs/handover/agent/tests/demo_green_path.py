"""Fixture demo of the GREEN/PASS path (not a unit test; run manually).

Proves the full assemble -> validate -> write chain when sources ARE available
and goals ARE approved, including:
  * populated numeric rows with pacing + goal_binary status,
  * a clean run creating staging_last_known_good.xlsx,
  * a subsequent FAILED run NOT clobbering last_known_good.

Uses in-memory OK envelopes + the pure calc cores, so it needs no live creds and
still never touches a dashboard/source (writer target is a local demo dir).

Run:  python3 tests/demo_green_path.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from cats_ingest.audit import AuditLog
from cats_ingest.config import load_config, Config
from cats_ingest.periods import PeriodContext
from cats_ingest.goals import resolve_goal, goal_binary_status, pacing
from cats_ingest.schema import MetricRow, V_PASS
from cats_ingest.writer import write_staging, REPO_ROOT
from cats_ingest.calculations import cloud_savings as cs, model_velocity as mv


def _demo_config() -> Config:
    cfg = load_config()
    # Redirect the writer to an isolated demo dir (still local, still safe).
    cfg._d["staging_target"] = {
        "kind": "local_xlsx",
        "local_dir": "staging_output/demo",
        "tabs": load_config().staging_target.get("tabs", {}),
    }
    # Approve two goals with real numbers so pacing computes.
    cfg._d["goals"]["cloud_savings"].update(
        {"approval_status": "approved", "goal_2026": 1200.0,
         "approval_evidence": "demo"})
    cfg._d["goals"]["model_velocity"].update(
        {"approval_status": "approved", "pacing_rule": "yoy_elapsed",
         "fy_yoy_rate": 0.2, "ly_same_elapsed_count": 10, "goal_2026": 60,
         "approval_evidence": "demo"})
    return cfg


def build_rows(pctx: PeriodContext, cfg: Config, run_id: str):
    rows = []

    # Cloud Savings via pure core (YTD=900; MoM/QoQ/YoY blank by design).
    co = cs.cloud_from_ytd(900.0)
    g = resolve_goal(cfg.goal("cloud_savings"), pctx)
    rows.append(_row("Cloud Savings", "usd", co, g, pctx, run_id))

    # Model Velocity via pure core with synthetic qualifying launches.
    recs = [{"date": "2026-07-05", "impact": 3, "type": "launch"},
            {"date": "2026-08-12", "impact": 4, "type": "launch"},
            {"date": "2026-09-01", "impact": 2, "type": "launch"}]
    n = mv.count_qualifying_launches(recs, pctx)
    from cats_ingest.calculations.base import CalcOutput
    mo = CalcOutput(value=float(n), as_of=pctx.month_label)
    g2 = resolve_goal(cfg.goal("model_velocity"), pctx)
    rows.append(_row("Model Velocity", "count", mo, g2, pctx, run_id))
    return rows


def _row(name, unit, calc, g, pctx, run_id):
    qtd = g.QTD_goal if g.ok else None
    return MetricRow(
        metric=name, value=calc.value, MoM=calc.MoM, QoQ=calc.QoQ, YoY=calc.YoY,
        current_quarter_goal=g.current_quarter_goal, QTD_goal=qtd,
        pacing_to_QTD_goal=pacing(calc.value, qtd) if g.ok else None,
        goal_2026=g.goal_2026, unit=unit, as_of=calc.as_of, quarter=pctx.quarter_label,
        status=goal_binary_status(calc.value, qtd) if g.ok else "Grey",
        source_status="OK", validation_status=V_PASS, run_id=run_id,
    )


def main():
    cfg = _demo_config()
    pctx = PeriodContext(date(2026, 9, 16))
    audit = AuditLog(run_id="DEMOGREEN", as_of="2026-09-16", write_mode="write_staging")
    rows = build_rows(pctx, cfg, "DEMOGREEN")
    res = write_staging(cfg, rows, audit, "demo methodology", "write_staging")
    print("GREEN run write:", res)
    assert res["clean"] is True and res["last_known_good_updated"] is True
    lkg = REPO_ROOT / "staging_output/demo/staging_last_known_good.xlsx"
    assert lkg.exists(), "last_known_good must be created on a clean run"

    # Now a FAILED run must NOT overwrite last_known_good.
    from cats_ingest.schema import V_BLOCKED
    bad = rows[:1]
    bad[0].validation_status = V_BLOCKED
    audit2 = AuditLog(run_id="DEMOFAIL", as_of="2026-09-16", write_mode="write_staging")
    before = lkg.read_bytes()
    res2 = write_staging(cfg, bad, audit2, "demo", "write_staging")
    print("FAILED run write:", res2)
    assert res2["last_known_good_updated"] is False
    assert lkg.read_bytes() == before, "failed run must not clobber last_known_good"

    for r in rows:
        print("  %-16s value=%s pace=%s status=%s"
              % (r.metric, r.value, round(r.pacing_to_QTD_goal, 3)
                 if r.pacing_to_QTD_goal else None, r.status))
    print("OK: green path populated, last_known_good preserved on failure.")


if __name__ == "__main__":
    main()
