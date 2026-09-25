"""Validate Staging Facts JSON. Exit 0 if every row passes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from schema import STAGING_HEADERS

METRIC_RE = re.compile(r"^MET-[A-F0-9]{12}$")
PERIOD_TYPES = {"current_quarter", "qtd", "fy"}
FIELD_KINDS = {"goal", "actual"}
CONFIDENCE = {"high", "review", "blocked"}
DAUQ_PARENT = "MET-419D6C123B19"
MAA_PARENT = "MET-B61F39994E32"


def load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "rows" in data:
        return data["rows"]
    if isinstance(data, list):
        return data
    raise ValueError(f"{path} must be a list or an object with 'rows'")


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_rows(rows: list[dict], catalog: dict | None = None) -> list[str]:
    errors: list[str] = []
    catalog_ids = set()
    if catalog:
        catalog_ids = {m["metric_id"] for m in catalog.get("pilot_metrics", [])}

    for i, row in enumerate(rows):
        loc = f"row[{i}] {row.get('display_name') or row.get('metric_id') or '?'}"
        missing = [h for h in STAGING_HEADERS if h not in row]
        if missing:
            errors.append(f"{loc}: missing columns {missing}")
            continue
        mid = str(row.get("metric_id") or "").strip()
        parent = str(row.get("parent_metric_id") or "").strip()
        if mid and not METRIC_RE.match(mid):
            errors.append(f"{loc}: bad metric_id {mid!r}")
        if catalog_ids and mid and mid not in catalog_ids and not parent:
            errors.append(f"{loc}: metric_id {mid} is not a pilot catalog parent")
        if row.get("field_kind") not in FIELD_KINDS:
            errors.append(f"{loc}: bad field_kind")
        if row.get("period_type") not in PERIOD_TYPES:
            errors.append(f"{loc}: bad period_type")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{loc}: bad confidence")

        publish = _as_bool(row.get("publish_ready"))
        matched = _as_bool(row.get("row_matched"))
        value = row.get("value")

        if parent and publish:
            errors.append(f"{loc}: unregistered/segment row cannot be publish_ready")
        if not mid and publish:
            errors.append(f"{loc}: blank metric_id cannot be publish_ready")
        if publish and value is None:
            errors.append(f"{loc}: publish_ready requires a value")
        if publish and not matched:
            errors.append(f"{loc}: publish_ready requires row_matched")

        if mid == DAUQ_PARENT and value not in (None, ""):
            try:
                num = float(value)
            except (TypeError, ValueError):
                errors.append(f"{loc}: DAUq value is not numeric")
            else:
                if 0 < num < 1000:
                    errors.append(
                        f"{loc}: DAUq value {num} looks like millions; staging stores users"
                    )

        if mid == "MET-AA468AF6805F":
            errors.append(
                f"{loc}: hashed Hex name DAUq (QTD), # — use registry MET-419D6C123B19"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: validate.py path/to/staging_facts.json [catalog.json]", file=sys.stderr)
        return 2
    rows_path = Path(args[0])
    catalog = None
    if len(args) > 1:
        catalog = json.loads(Path(args[1]).read_text())
    else:
        default_catalog = Path(__file__).resolve().parents[1] / "catalog.json"
        if default_catalog.exists():
            catalog = json.loads(default_catalog.read_text())
    errors = validate_rows(load_rows(rows_path), catalog)
    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK {len(load_rows(rows_path))} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
