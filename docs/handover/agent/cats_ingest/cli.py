"""CLI entrypoint for the CATS staging ingestion skill.

Examples:
  python -m cats_ingest.cli --as-of 2026-09-16 --write-mode dry_run
  python -m cats_ingest.cli --as-of 2026-09-16 --write-mode write_staging
"""

from __future__ import annotations

import argparse
import json
import sys

from .pipeline import run


def _fmt_num(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        return "%.4g" % v
    return str(v)


def _print_report(report: dict) -> None:
    print("=" * 72)
    print("CATS staging ingestion — run %s" % report["run_id"])
    print("as_of=%s  quarter=%s  env=%s  mode=%s"
          % (report["as_of"], report["quarter"], report["environment"], report["write_mode"]))
    wr = report["write_result"]
    print("write: %s" % json.dumps(wr))
    print("status: %s" % json.dumps(report["status_counts"]))
    print("-" * 72)
    hdr = "%-26s %-8s %-8s %-8s %-10s" % ("metric", "value", "pace", "status", "validation")
    print(hdr)
    for r in report["rows"]:
        print("%-26s %-8s %-8s %-8s %-10s"
              % (r["metric"][:26], _fmt_num(r["value"]),
                 _fmt_num(r["pacing_to_QTD_goal"]), r["status"], r["validation_status"]))
        if r["review_reason"]:
            print("    ↳ %s" % r["review_reason"][:200])
    print("=" * 72)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="CATS Scale + Rev/FTE staging ingestion (staging-only).")
    p.add_argument("--as-of", dest="as_of", default=None,
                   help="Reporting as-of date YYYY-MM-DD (default: today).")
    p.add_argument("--environment", default="staging", choices=["staging"],
                   help="MVP is staging-only.")
    p.add_argument("--write-mode", dest="write_mode", default="dry_run",
                   choices=["dry_run", "write_staging"])
    p.add_argument("--config", default=None, help="Path to metric_config.yaml.")
    p.add_argument("--json", action="store_true", help="Print full JSON report.")
    args = p.parse_args(argv)

    report = run(as_of_date=args.as_of, environment=args.environment,
                 write_mode=args.write_mode, config_path=args.config)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        _print_report(report)
    # Exit non-zero if nothing is publishable, so schedulers can alert.
    return 0 if report["status_counts"].get("PASS", 0) > 0 else 3


if __name__ == "__main__":
    sys.exit(main())
