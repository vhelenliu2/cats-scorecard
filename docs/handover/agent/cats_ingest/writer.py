"""Idempotent staging writer.

MVP default: an isolated local .xlsx (never a dashboard/source). A guarded
Google Sheets path exists for prod but refuses any forbidden target.

Idempotency (BUILD_PLAN.md §8/§11): output is keyed by (run_id, metric, as_of).
Re-running identical inputs reproduces an identical file. The "last known good"
copy is only overwritten when the whole run is clean (no BLOCKED, >=1 PASS), so
a failed run can never clobber the last good result.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from . import safety
from .config import Config
from .schema import OUTPUT_COLUMNS, MetricRow, V_PASS, V_BLOCKED

REPO_ROOT = Path(__file__).resolve().parent.parent


def _rows_df(rows: List[MetricRow]) -> pd.DataFrame:
    data = [r.to_dict() for r in rows]
    df = pd.DataFrame(data)
    for c in OUTPUT_COLUMNS:
        if c not in df.columns:
            df[c] = None
    return df[OUTPUT_COLUMNS]


def _is_clean(rows: List[MetricRow]) -> bool:
    if not rows:
        return False
    if any(r.validation_status == V_BLOCKED for r in rows):
        return False
    return any(r.validation_status == V_PASS for r in rows)


def write_staging(cfg: Config, rows: List[MetricRow], audit, methodology_text: str,
                  write_mode: str) -> Dict[str, Any]:
    tgt = cfg.staging_target
    kind = tgt.get("kind", "local_xlsx")

    # HARD SAFETY GATE: refuse any write aimed at a dashboard/source id.
    target_id = tgt.get("google_spreadsheet_id") if kind == "google_sheet" else None
    safety.assert_safe_write_target(target_id, kind)

    if write_mode == "dry_run":
        return {"written": False, "mode": "dry_run", "kind": kind,
                "target": target_id or tgt.get("local_dir"),
                "clean": _is_clean(rows), "n_rows": len(rows)}

    if kind == "local_xlsx":
        return _write_local(cfg, rows, audit, methodology_text)
    if kind == "google_sheet":
        return _write_google(cfg, rows, audit, methodology_text, target_id)
    raise ValueError("Unknown staging_target.kind=%r" % kind)


def _write_local(cfg: Config, rows: List[MetricRow], audit,
                 methodology_text: str) -> Dict[str, Any]:
    tgt = cfg.staging_target
    out_dir = REPO_ROOT / tgt.get("local_dir", "staging_output")
    out_dir.mkdir(parents=True, exist_ok=True)
    tabs = tgt.get("tabs", {})
    run_id = audit.run_id
    path = out_dir / ("staging_%s.xlsx" % run_id)

    out_df = _rows_df(rows)
    raw_df = pd.DataFrame(audit.raw_rows) if audit.raw_rows else pd.DataFrame({"info": ["no raw rows"]})
    audit_df = pd.DataFrame(audit.source_rows) if audit.source_rows else pd.DataFrame()
    find_df = pd.DataFrame(audit.findings) if audit.findings else pd.DataFrame()
    method_df = pd.DataFrame({"methodology": methodology_text.splitlines()})

    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        out_df.to_excel(xl, sheet_name=tabs.get("output", "Staging Output")[:31], index=False)
        if not audit_df.empty:
            audit_df.to_excel(xl, sheet_name=tabs.get("audit", "Run Audit")[:31], index=False)
        if not find_df.empty:
            find_df.to_excel(xl, sheet_name="Findings", index=False)
        raw_df.to_excel(xl, sheet_name=tabs.get("raw_rows", "Raw Rows")[:31], index=False)
        method_df.to_excel(xl, sheet_name=tabs.get("methodology", "Methodology")[:31], index=False)

    latest = out_dir / "staging_latest.xlsx"
    shutil.copyfile(path, latest)

    clean = _is_clean(rows)
    lkg = out_dir / "staging_last_known_good.xlsx"
    if clean:
        shutil.copyfile(path, lkg)

    return {"written": True, "kind": "local_xlsx", "path": str(path),
            "latest": str(latest),
            "last_known_good": str(lkg) if lkg.exists() else None,
            "last_known_good_updated": clean, "clean": clean, "n_rows": len(rows)}


def _write_google(cfg: Config, rows: List[MetricRow], audit,
                  methodology_text: str, target_id: str) -> Dict[str, Any]:
    from .adapters import _gauth  # local import; only when actually writing

    # Writing requires a writable scope, which the read-only helper never grants.
    # This is intentional: enabling prod writes is a separate, explicit change
    # (add a write scope + credential) so staging-write can't happen by accident.
    raise NotImplementedError(
        "google_sheet staging write is not enabled in the MVP. Target %r passed "
        "the safety gate, but enabling writes requires an explicit writable "
        "credential/scope wired here on purpose. Use local_xlsx for the MVP."
        % target_id
    )
