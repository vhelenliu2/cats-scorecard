#!/usr/bin/env python3
"""Validate Shopping Revenue goals pulled from the pacing sheet (backend, not Hex).

Usage:
  python3 validate_shopping_goals.py --mode gsheet --as-of 2026-09-12
  python3 validate_shopping_goals.py --mode fixture --as-of 2026-09-12
  python3 validate_shopping_goals.py --mode dump --dump path/to/q3_dpa.json --as-of 2026-09-12

Exit 0 when extraction succeeds and matches the oracle for the as-of date.
Requires GOOGLE_SHEETS_CONNECTION or GOOGLE_APPLICATION_CREDENTIALS for gsheet mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from dates import parse_date, quarter_of  # noqa: E402
from extract_shopping import (  # noqa: E402
    SHOPPING_PACING_GID,
    SHOPPING_PACING_SHEET_ID,
    extract_shopping_goals,
)
from gsheets import get_all_values  # noqa: E402

FIXTURES = SCRIPTS / "fixtures"
ORACLE_PATH = FIXTURES / "shopping_goals_oracle.json"
FIXTURE_ROWS = FIXTURES / "shopping_q3_dpa_tracker.json"


def load_oracle(as_of: date) -> dict | None:
    if not ORACLE_PATH.exists():
        return None
    data = json.loads(ORACLE_PATH.read_text())
    key = as_of.isoformat()
    if key in data:
        return data[key]
    if "default" in data:
        return data["default"]
    return data if isinstance(data, dict) and "current_quarter" in data else None


def load_rows(mode: str, dump_path: Path | None) -> tuple[str, list[list]]:
    if mode == "fixture":
        path = FIXTURE_ROWS
        if not path.exists():
            raise FileNotFoundError(f"fixture missing: {path}")
        payload = json.loads(path.read_text())
        if isinstance(payload, dict) and "rows" in payload:
            return payload.get("tab", "Q3 DPA tracker"), payload["rows"]
        if isinstance(payload, list):
            return "Q3 DPA tracker", payload
        raise ValueError(f"{path} must be a row list or {{tab, rows}} object")
    if mode == "dump":
        if dump_path is None:
            raise ValueError("--dump required for dump mode")
        payload = json.loads(dump_path.read_text())
        if isinstance(payload, dict) and "rows" in payload:
            return payload.get("tab", "Q3 DPA tracker"), payload["rows"]
        if isinstance(payload, list):
            return dump_path.stem, payload
        raise ValueError(f"{dump_path} must be a row list or {{tab, rows}} object")
    tab = f"Q{quarter_of(date.today())} DPA tracker"
    tab, rows = get_all_values(SHOPPING_PACING_SHEET_ID, tab=tab, gid=SHOPPING_PACING_GID)
    return tab, rows


def validate_extracted(extracted: dict, oracle: dict | None) -> list[str]:
    errors: list[str] = []
    cq = extracted.get("current_quarter")
    paced = extracted.get("qtd")
    if cq is None:
        errors.append("current_quarter goal is None — Q{n} Goal not found on pacing tab")
    if paced is None:
        errors.append(
            "qtd paced goal is None — no row with col B week <= as_of under $22m pacing"
        )
    if oracle is None:
        return errors
    if cq is not None and oracle.get("current_quarter") is not None:
        if float(cq) != float(oracle["current_quarter"]):
            errors.append(
                f"current_quarter: got {cq:,.0f}, expected {oracle['current_quarter']:,.0f}"
            )
    if paced is not None and oracle.get("qtd") is not None:
        if float(paced) != float(oracle["qtd"]):
            errors.append(f"qtd: got {paced:,.0f}, expected {oracle['qtd']:,.0f}")
    if oracle.get("week_start") and extracted.get("week_start"):
        if extracted["week_start"] != oracle["week_start"]:
            errors.append(
                f"week_start: got {extracted['week_start']}, expected {oracle['week_start']}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("gsheet", "fixture", "dump"),
        default="gsheet",
        help="gsheet=live pull; fixture=checked-in layout; dump=replay JSON export",
    )
    parser.add_argument("--as-of", required=True, help="Dashboard as-of date (YYYY-MM-DD)")
    parser.add_argument("--dump", type=Path, help="JSON row dump for --mode dump")
    parser.add_argument(
        "--no-oracle",
        action="store_true",
        help="Only require non-null extraction; skip golden-value compare",
    )
    args = parser.parse_args(argv)

    as_of = parse_date(args.as_of)
    if as_of is None:
        print(f"invalid --as-of: {args.as_of!r}", file=sys.stderr)
        return 2

    try:
        tab, rows = load_rows(args.mode, args.dump)
    except Exception as exc:
        print(f"FAIL load: {exc}", file=sys.stderr)
        return 1

    extracted = extract_shopping_goals(rows, as_of=as_of)
    extracted["source_tab"] = tab
    oracle = None if args.no_oracle else load_oracle(as_of)
    errors = validate_extracted(extracted, oracle)

    print(json.dumps(extracted, indent=2))
    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("OK Shopping Revenue goals validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
