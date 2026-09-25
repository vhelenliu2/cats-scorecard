"""End-to-end pipeline smoke test: safe, staging-only, and honest about gaps."""

from __future__ import annotations

from pathlib import Path

from cats_ingest.pipeline import run
from cats_ingest import safety


def test_pipeline_runs_staging_only_and_marks_gaps():
    report = run(as_of_date="2026-09-16", environment="staging",
                 write_mode="write_staging")
    # Seven metrics produced (Scale x5 + S+M FTE + Shopping Revenue).
    assert report["n_metrics"] == 7
    # Nothing was written to a dashboard/source: the only path is local_xlsx.
    wr = report["write_result"]
    assert wr["kind"] == "local_xlsx"
    assert Path(wr["path"]).exists()
    assert "staging_output" in wr["path"]
    # Metrics still missing an input (revenue actual, grade map, col AO, SQL) must
    # NOT silently PASS.
    rows = {r["metric"]: r for r in report["rows"]}
    for m in ("Revenue / S+M FTE", "Ads SOTA ML", "Shopping Revenue (pacing)",
              "Experimentation Velocity"):
        assert rows[m]["validation_status"] == "REVIEW"
    # Approved goals pulled from Roadmap KPIs pace end-to-end -> PASS.
    assert rows["Cloud Savings"]["validation_status"] == "PASS"
    assert rows["Cloud Savings"]["status"] == "Green"
    # OE carries the score as value AND paces its QoQ growth vs the +5% rate.
    assert rows["Operational Excellence"]["validation_status"] == "PASS"
    assert rows["Operational Excellence"]["value"] is not None
    assert rows["Operational Excellence"]["QoQ"] is not None
    # Model Velocity paces its QTD count vs the +25% YoY bar (may be Red, but PASS).
    assert rows["Model Velocity"]["validation_status"] == "PASS"
    assert rows["Model Velocity"]["pacing_to_QTD_goal"] is not None
    counts = report["status_counts"]
    assert counts.get("PASS", 0) >= 3


def test_run_is_idempotent():
    r1 = run(as_of_date="2026-09-16", write_mode="dry_run")
    r2 = run(as_of_date="2026-09-16", write_mode="dry_run")
    assert r1["run_id"] == r2["run_id"]
    # Same inputs -> same row values/statuses.
    assert [r["validation_status"] for r in r1["rows"]] == \
           [r["validation_status"] for r in r2["rows"]]


def test_experimentation_uses_evidenced_fallback_and_flags_review():
    # SQL is unavailable; the documented _EXP_COUNTS fallback is fully evidenced
    # (value/owner/timestamp/reason/evidence), so it is staged but flagged REVIEW
    # (needs human sign-off) — never silently trusted, never guessed.
    report = run(as_of_date="2026-09-16", write_mode="dry_run")
    rows = {r["metric"]: r for r in report["rows"]}
    exp = rows["Experimentation Velocity"]
    assert exp["value"] == 141.0
    assert exp["validation_status"] == "REVIEW"
