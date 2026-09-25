"""Deterministic pipeline (BUILD_PLAN.md §6).

Identify source -> Extract -> Normalize -> Validate -> Calculate -> Reconcile
-> Write staging -> Write audit/provenance -> Report status.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import adapters, safety
from .audit import AuditLog
from .calculations import REGISTRY as CALC_REGISTRY
from .calculations.base import CalcContext
from .config import Config, load_config
from .goals import resolve_goal, status_for, pacing
from .periods import PeriodContext, parse_as_of
from .schema import (
    MetricRow, SourceEnvelope, utcnow_iso,
    SRC_OK, SRC_STALE, SRC_MISSING, SRC_BLOCKED, SRC_ERROR, VAL_GREY,
)
from . import validation
from .writer import write_staging, REPO_ROOT


def _run_id(as_of: str, cfg_path: Path) -> str:
    h = hashlib.sha256()
    h.update(as_of.encode())
    h.update(Path(cfg_path).read_bytes())
    return "R" + h.hexdigest()[:12]


def _agg_source_status(statuses: List[str]) -> str:
    if not statuses:
        return SRC_MISSING
    for worst in (SRC_BLOCKED, SRC_ERROR, SRC_MISSING, SRC_STALE):
        if worst in statuses:
            return worst
    return SRC_OK


def _load_prev_good(cfg: Config) -> Dict[str, Dict[str, Any]]:
    """Return {metric: prev_row} from the last known good staging file, if any."""
    tgt = cfg.staging_target
    if tgt.get("kind") != "local_xlsx":
        return {}
    lkg = REPO_ROOT / tgt.get("local_dir", "staging_output") / "staging_last_known_good.xlsx"
    if not lkg.exists():
        return {}
    try:
        import pandas as pd
        df = pd.read_excel(lkg, sheet_name=tgt.get("tabs", {}).get("output", "Staging Output"))
        return {r["metric"]: dict(r) for _, r in df.iterrows()}
    except Exception:
        return {}


def _methodology_text(cfg: Config) -> str:
    return (
        "CATS Scale + Revenue/FTE staging ingestion — methodology\n"
        "Source of truth: Operations Runbook (14 Sep 2026).\n"
        "Staging-only: this run never writes to the Hex dashboard or any source sheet.\n"
        "Operational Excellence: sum team scores at latest completed month-end; "
        "MoM vs prior month, QoQ vs prior quarter-end, YoY vs Dec 2025.\n"
        "Cloud Savings: YTD from Efficiencies C1; MoM/QoQ/YoY intentionally blank "
        "(no reliable as-of date to phase a comparison).\n"
        "Model Velocity: QTD qualifying launches (>0 impact; exclude bug fixes, "
        "backtests, deprecations, undated) across Ranking+Retrieval+Shopping.\n"
        "Experimentation Velocity: QTD distinct Ads experiments, unique_objects>1000; "
        "manual _EXP_COUNTS fallback only with owner/timestamp/reason/evidence.\n"
        "Ads SOTA ML: most recent dated grade; pace only with approved grade->rank map.\n"
        "Revenue / S+M FTE: revenue / matched-month FTE; never pair newer revenue "
        "with older headcount.\n"
        "Goals/pacing: Scale=linear pacing; Rev/FTE=waypoint interpolation. No pace "
        "when a goal is missing/unapproved/CONFIRM. goal_binary: Green>=100%, Red<100%.\n"
    )


def run(as_of_date: Optional[str] = None, environment: str = "staging",
        write_mode: str = "dry_run", config_path: Optional[str] = None) -> Dict[str, Any]:
    cfg = load_config(Path(config_path) if config_path else None)
    as_of = str(parse_as_of(as_of_date))
    pctx = PeriodContext(parse_as_of(as_of_date))
    run_id = _run_id(as_of, cfg.path)

    audit = AuditLog(run_id=run_id, as_of=as_of, write_mode=write_mode)
    audit.notes.append("environment=%s" % environment)
    prev_good = _load_prev_good(cfg)

    rows: List[MetricRow] = []
    for metric_key, spec in cfg.metrics.items():
        # ---- Identify + Extract (all actual + fallback sources) --------------
        envelopes: Dict[str, SourceEnvelope] = {}
        source_ids = list(spec.get("actual_sources", [])) + list(spec.get("fallback_sources", []))
        for sid in source_ids:
            env = adapters.read_source(cfg, sid)
            envelopes[sid] = env
            audit.record_source(metric_key, env)

        # ---- Calculate ------------------------------------------------------
        goal = cfg.goal(spec.get("goal_ref", ""))
        calc_fn = CALC_REGISTRY[spec["calc"]]
        cctx = CalcContext(metric_key, spec, goal, envelopes, pctx, spec.get("unit", ""))
        calc = calc_fn(cctx)

        # ---- Goals / pacing -------------------------------------------------
        goal_res = resolve_goal(goal, pctx)
        qtd_goal = goal_res.QTD_goal if goal_res.ok else None
        # Most metrics pace their value; some (e.g. OE) pace a comparison field such
        # as QoQ growth against a rate goal (build plan / runbook: OE compares QoQ).
        cmp_field = spec.get("compare_field", "value")
        cmp_val = getattr(calc, cmp_field, calc.value)
        pace = pacing(cmp_val, qtd_goal) if goal_res.ok else None
        status = status_for(spec.get("status_rule", "goal_binary"), cmp_val, qtd_goal,
                            spec.get("direction", "up")) if goal_res.ok else VAL_GREY

        # ---- Assemble row ---------------------------------------------------
        first_sid = (spec.get("actual_sources") or [None])[0]
        src_url = cfg.source_url(first_sid) if first_sid else ""
        src_tab = envelopes[first_sid].source_tab_or_query if first_sid in envelopes else ""
        agg_status = _agg_source_status([envelopes[s].source_status for s in
                                         spec.get("actual_sources", []) if s in envelopes])

        row = MetricRow(
            metric=spec.get("display", metric_key),
            value=calc.value, MoM=calc.MoM, QoQ=calc.QoQ, YoY=calc.YoY,
            current_quarter_goal=goal_res.current_quarter_goal,
            QTD_goal=qtd_goal, pacing_to_QTD_goal=pace, goal_2026=goal_res.goal_2026,
            unit=spec.get("unit", ""), as_of=calc.as_of or as_of,
            quarter=pctx.quarter_label, status=status,
            source_status=agg_status, source_url=src_url, source_tab=str(src_tab),
            run_id=run_id,
        )

        # ---- Validate + finalize -------------------------------------------
        findings = validation.run_gates(row, calc, goal_res, spec, cfg, envelopes,
                                        pctx, prev_good.get(row.metric),
                                        cfg.tolerances)
        audit.record_findings(findings)
        row.validation_status = validation.finalize_status(calc, goal_res, findings)
        row.review_reason = validation.review_reason(calc, goal_res, findings)
        for n in calc.notes:
            audit.notes.append("%s: %s" % (metric_key, n))
        rows.append(row)

    # ---- Write staging + audit ---------------------------------------------
    write_result = write_staging(cfg, rows, audit, _methodology_text(cfg), write_mode)

    report = {
        "run_id": run_id,
        "as_of": as_of,
        "quarter": pctx.quarter_label,
        "environment": environment,
        "write_mode": write_mode,
        "write_result": write_result,
        "n_metrics": len(rows),
        "status_counts": _count_statuses(rows),
        "rows": [r.to_dict() for r in rows],
        "source_pulls": audit.source_rows,
        "generated_at": utcnow_iso(),
    }
    return report


def _count_statuses(rows: List[MetricRow]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in rows:
        out[r.validation_status] = out.get(r.validation_status, 0) + 1
    return out
