#!/usr/bin/env python3
"""Run the MAA + DAUq ingest pilot.

Modes:
  fixture  — golden layouts, no credentials (default)
  gsheet   — live Google Sheets
  xlsx     — Excel exports of the MAB + DAUq source tabs
  dump     — replay a JSON dump from the Hex ingest_pilot_dump cell
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
REPO = SKILL.parents[2]
sys.path.insert(0, str(SCRIPTS))

from dates import parse_date, quarter_bounds  # noqa: E402
from diff_runs import apply_change_holds  # noqa: E402
from extract_dauq import extract_dauq_goals  # noqa: E402
from extract_maa import extract_maa_goals  # noqa: E402
from schema import STAGING_HEADERS, utcnow_iso  # noqa: E402
from validate import validate_rows  # noqa: E402

CATALOG_PATH = SKILL / "catalog.json"
STATE_DIR = REPO / "docs" / "ingestion" / "_state"
RUNS_DIR = REPO / "docs" / "ingestion" / "runs"
FIXTURES = SCRIPTS / "fixtures"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text())


def metric(catalog: dict, metric_id: str) -> dict:
    for row in catalog["pilot_metrics"]:
        if row["metric_id"] == metric_id:
            return row
    raise KeyError(metric_id)


def write_md_table(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    headers = headers or [
        "metric_id",
        "display_name",
        "period_type",
        "planning_period",
        "value",
        "publish_ready",
        "confidence",
        "review_reason",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "") or "") for h in headers) + " |")
    path.write_text("\n".join(lines) + "\n")


def write_outputs(run_dir: Path, payload: dict, rows: list[dict]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "staging_facts.json").write_text(json.dumps(payload, indent=2) + "\n")
    with (run_dir / "staging_facts.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STAGING_HEADERS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if row.get(k) is None else row.get(k) for k in STAGING_HEADERS})
    write_md_table(run_dir / "staging_facts.md", rows)
    held = [r for r in rows if not r.get("publish_ready")]
    write_md_table(run_dir / "review_queue.md", held)


def update_pilot_state(catalog: dict, payload: dict, rows: list[dict], staging_id: str | None) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "last_staging.json").write_text(json.dumps(payload, indent=2) + "\n")
    ready = [r for r in rows if r.get("publish_ready")]
    held = [r for r in rows if not r.get("publish_ready")]
    lines = [
        f"# Ingest pilot state",
        f"_Updated: {payload['pulled_at']}_",
        "",
        f"- Mode: `{payload['mode']}`",
        f"- As-of: `{payload['as_of']}`",
        f"- Staging sheet: `{staging_id or payload.get('staging_spreadsheet_id') or 'local only'}`",
        f"- Publish-ready: **{len(ready)}** · Review: **{len(held)}**",
        "",
        "| metric_id | display_name | period_type | value | publish_ready | note |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        if row.get("parent_metric_id") and row.get("period_type") != "current_quarter":
            continue
        lines.append(
            f"| {row.get('metric_id') or ''} | {row['display_name']} | {row['period_type']} | "
            f"{row.get('value') if row.get('value') is not None else ''} | "
            f"{'yes' if row.get('publish_ready') else 'hold'} | {row.get('review_reason') or ''} |"
        )
    (STATE_DIR / "pilot.md").write_text("\n".join(lines) + "\n")


def load_fixture_dump(as_of: date) -> dict:
    maa = json.loads((FIXTURES / "maa_daily_goals_allocation.json").read_text())
    dauq = json.loads((FIXTURES / "dauq_latest_forecast.json").read_text())
    _, q_start, q_end = quarter_bounds(as_of)
    return {
        "as_of": as_of.isoformat(),
        "start_of_quarter": q_start.isoformat(),
        "end_of_quarter": q_end.isoformat(),
        "maa_all_values": maa["all_values"],
        "dauq_all_values": dauq["all_values"],
        "expected": {
            "maa_eoq": maa["expected"]["eoq_overall"],
            "maa_qtd": maa["expected"]["qtd_overall"],
            "maa_fy": maa["expected"]["fy_overall"],
            "dauq_total": dauq["expected"]["total_users"],
            "dauq_us": dauq["expected"]["us_users"],
            "dauq_row": dauq["expected"]["row_users"],
        },
    }


def load_xlsx_exports(catalog: dict, maa_path: str, dauq_path: str) -> dict:
    from xlsx_reader import read_tab

    maa_cat = metric(catalog, "MET-B61F39994E32")
    dauq_cat = metric(catalog, "MET-419D6C123B19")
    maa_tab, maa_vals = read_tab(maa_path, maa_cat.get("source_tab"))
    dauq_tab, dauq_vals = read_tab(dauq_path, dauq_cat.get("source_tab"))
    maa_cat = dict(maa_cat)
    dauq_cat = dict(dauq_cat)
    maa_cat["source_tab"] = maa_tab
    dauq_cat["source_tab"] = dauq_tab
    return {"maa_all_values": maa_vals, "dauq_all_values": dauq_vals, "maa_cat": maa_cat, "dauq_cat": dauq_cat}


def load_live_sheets(catalog: dict) -> dict:
    from gsheets import get_all_values

    maa_cat = metric(catalog, "MET-B61F39994E32")
    dauq_cat = metric(catalog, "MET-419D6C123B19")
    maa_tab, maa_vals = get_all_values(
        maa_cat["source_sheet_id"], maa_cat["source_tab"], maa_cat.get("source_gid")
    )
    dauq_tab, dauq_vals = get_all_values(
        dauq_cat["source_sheet_id"], dauq_cat["source_tab"], dauq_cat.get("source_gid")
    )
    maa_cat = dict(maa_cat)
    dauq_cat = dict(dauq_cat)
    maa_cat["source_tab"] = maa_tab
    dauq_cat["source_tab"] = dauq_tab
    return {"maa_all_values": maa_vals, "dauq_all_values": dauq_vals, "maa_cat": maa_cat, "dauq_cat": dauq_cat}


def compare_expected(rows: list[dict], expected: dict | None) -> list[str]:
    if not expected:
        return []
    errors = []

    def find(metric_id: str, period_type: str):
        for row in rows:
            if row.get("metric_id") == metric_id and row.get("period_type") == period_type:
                return row
        return None

    checks = [
        ("MET-B61F39994E32", "current_quarter", "maa_eoq", 0),
        ("MET-B61F39994E32", "qtd", "maa_qtd", 0),
        ("MET-B61F39994E32", "fy", "maa_fy", 0),
        ("MET-419D6C123B19", "current_quarter", "dauq_total", 50_000),
    ]
    for mid, ptype, key, tol in checks:
        if key not in expected:
            continue
        row = find(mid, ptype)
        want = expected[key]
        got = None if row is None else row.get("value")
        if row is None:
            errors.append(f"missing {mid} {ptype}")
            continue
        if got is None or abs(float(got) - float(want)) > tol:
            errors.append(f"{mid} {ptype}: got {got} want {want} (±{tol})")
    return errors


def extract_all(catalog: dict, dump: dict, as_of: date) -> list[dict]:
    maa_cat = dump.get("maa_cat") or metric(catalog, "MET-B61F39994E32")
    dauq_cat = dump.get("dauq_cat") or metric(catalog, "MET-419D6C123B19")
    q_start = parse_date(dump.get("start_of_quarter"))
    q_end = parse_date(dump.get("end_of_quarter"))
    rows = extract_maa_goals(
        dump["maa_all_values"],
        as_of=as_of,
        catalog_row=maa_cat,
        q_start=q_start,
        q_end=q_end,
    )
    rows.extend(
        extract_dauq_goals(dump["dauq_all_values"], as_of=as_of, catalog_row=dauq_cat)
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="CATS scorecard ingest pilot (MAA + DAUq goals)")
    parser.add_argument("--mode", choices=("fixture", "gsheet", "xlsx", "dump"), default="fixture")
    parser.add_argument("--as-of", dest="as_of", default="2026-09-01")
    parser.add_argument("--dump", dest="dump_path")
    parser.add_argument("--maa-xlsx", dest="maa_xlsx", default="")
    parser.add_argument("--dauq-xlsx", dest="dauq_xlsx", default="")
    parser.add_argument("--push", action="store_true", help="Write the staging Google Sheet")
    parser.add_argument("--staging-id", dest="staging_id", default="")
    args = parser.parse_args()

    catalog = load_catalog()
    as_of = parse_date(args.as_of)
    if as_of is None:
        print("invalid --as-of", file=sys.stderr)
        return 2

    if args.mode == "fixture":
        dump = load_fixture_dump(as_of)
    elif args.mode == "dump":
        if not args.dump_path:
            print("--dump path required", file=sys.stderr)
            return 2
        dump = json.loads(Path(args.dump_path).read_text())
        if dump.get("as_of"):
            as_of = parse_date(dump["as_of"]) or as_of
    elif args.mode == "xlsx":
        if not args.maa_xlsx or not args.dauq_xlsx:
            print("--maa-xlsx and --dauq-xlsx required for xlsx mode", file=sys.stderr)
            return 2
        live = load_xlsx_exports(catalog, args.maa_xlsx, args.dauq_xlsx)
        _, q_start, q_end = quarter_bounds(as_of)
        dump = {
            "as_of": as_of.isoformat(),
            "start_of_quarter": q_start.isoformat(),
            "end_of_quarter": q_end.isoformat(),
            **live,
        }
    else:
        live = load_live_sheets(catalog)
        _, q_start, q_end = quarter_bounds(as_of)
        dump = {
            "as_of": as_of.isoformat(),
            "start_of_quarter": q_start.isoformat(),
            "end_of_quarter": q_end.isoformat(),
            **live,
        }

    rows = extract_all(catalog, dump, as_of)
    prev_path = STATE_DIR / "last_staging.json"
    previous = None
    if prev_path.exists() and args.mode != "fixture":
        previous = json.loads(prev_path.read_text()).get("rows")
    rows = apply_change_holds(rows, previous)

    schema_errors = validate_rows(rows, catalog)
    expected_errors = compare_expected(rows, dump.get("expected"))
    errors = schema_errors + expected_errors

    pulled_at = utcnow_iso()
    for row in rows:
        row["pulled_at"] = pulled_at
        row["as_of_date"] = as_of.isoformat()

    run_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    payload = {
        "run_id": run_id,
        "mode": args.mode,
        "as_of": as_of.isoformat(),
        "pulled_at": pulled_at,
        "catalog": "MET-B61F39994E32 + MET-419D6C123B19",
        "rows": rows,
        "errors": errors,
    }

    run_dir = RUNS_DIR / run_id
    if args.mode == "dump" and dump.get("maa_all_values"):
        (run_dir).mkdir(parents=True, exist_ok=True)
        (run_dir / "raw_maa.json").write_text(json.dumps(dump["maa_all_values"]))
        (run_dir / "raw_dauq.json").write_text(json.dumps(dump["dauq_all_values"]))
    write_outputs(run_dir, payload, rows)

    staging_id = args.staging_id or __import__("os").environ.get("CATS_STAGING_SHEET_ID")
    if args.push:
        from gsheets import upsert_facts

        staging_id = upsert_facts(staging_id or None, catalog, rows, run_id)
        payload["staging_spreadsheet_id"] = staging_id
        (run_dir / "staging_facts.json").write_text(json.dumps(payload, indent=2) + "\n")

    if args.mode != "fixture":
        update_pilot_state(catalog, payload, rows, staging_id)
    else:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        ready = [r for r in rows if r.get("publish_ready")]
        held = [r for r in rows if not r.get("publish_ready")]
        (STATE_DIR / "pilot.md").write_text(
            "\n".join(
                [
                    "# Ingest pilot state",
                    f"_Updated: {pulled_at}_",
                    "",
                    "- Mode: `fixture` (self-test; not a live sheet pull)",
                    f"- As-of: `{as_of.isoformat()}`",
                    f"- Publish-ready: **{len(ready)}** · Review: **{len(held)}**",
                    f"- Artifacts: [runs/{run_id}/](../runs/{run_id}/)",
                    "",
                ]
            )
            + "\n"
        )

    ready = sum(1 for r in rows if r.get("publish_ready"))
    print(f"run {run_id} mode={args.mode} as_of={as_of} rows={len(rows)} publish_ready={ready}")
    for row in rows:
        flag = "READY" if row.get("publish_ready") else "HOLD "
        print(
            f"  {flag} {row.get('metric_id') or 'unreg':16} {row['display_name'][:32]:32} "
            f"{row['period_type']:16} {row.get('value')} {row.get('review_reason') or ''}"
        )
    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("OK")
    if staging_id:
        print(f"staging: https://docs.google.com/spreadsheets/d/{staging_id}")
    print(f"artifacts: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
