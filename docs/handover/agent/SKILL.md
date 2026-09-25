---
name: cats-staging-ingestion
description: Refresh the CATS Scorecard STAGING output for the seven Tier-1 metrics — the five Scale rows (Operational Excellence, Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML), Revenue / S+M FTE, and Shopping Revenue pacing. Reads approved sources read-only, applies the Operations Runbook methodology, validates, and writes an isolated staging workbook. Use when asked to automate, refresh, or dry-run the CATS Tier-1 dashboard data. NEVER edits the Hex dashboard or any source workbook.
---

# CATS Tier-1 Staging Ingestion

Staging-only automation for the CATS Scorecard. Implements the Tier-1 half of
the [`agent_build_plan.md`](agent_build_plan.md) build plan against the methodology in
[`OPERATIONS_RUNBOOK.md`](../OPERATIONS_RUNBOOK.md).

**Scope note:** only **Tier 1 (ingest)** is implemented in code. **Tier 2
(verify)** is specified in `agent_build_plan.md` §8 but has no runner yet — there is no
`--verify` flag and no `check_status` output. Do not claim Tier-2 coverage.

## Safety contract (read this first)

- **Staging-only.** The only write target is the isolated staging sheet declared
  in `config/metric_config.yaml → staging_target`. `cats_ingest/safety.py` holds
  a deny-list of every dashboard and source id and **aborts any write** that
  targets one. The Google-Sheets write path is deliberately not wired for prod.
- **Sources are read-only.** Adapters request only `*.readonly` OAuth scopes;
  the warehouse adapter refuses any non-SELECT SQL; the Hex adapter is an
  explicit block (a Google service account reads shared Sheets, not Hex).
- **Never guess.** Missing header rows, goal values, grade mappings, or source
  tabs stay as `CONFIRM`/`null` in config, and the affected metric is emitted as
  `REVIEW`/`BLOCKED` — never a fabricated number.
- **Zero ≠ missing.** A real `0` is kept; an unreadable value is `null` + reason.
- **Idempotent.** Re-running identical inputs reproduces an identical file. A
  failed run never overwrites `staging_last_known_good.xlsx`.

## How to run

```bash
cd docs/handover/agent
python3 -m cats_ingest.cli --as-of 2026-09-25 --write-mode dry_run     # preview
python3 -m cats_ingest.cli --as-of 2026-09-25 --write-mode write_staging
python3 -m cats_ingest.cli --as-of 2026-09-25 --write-mode write_staging --json
python3 tests/run_tests.py                                             # 28 tests
```

Outputs land in `staging_output/`: `staging_<run_id>.xlsx`,
`staging_latest.xlsx`, and (only on a clean run)
`staging_last_known_good.xlsx`, each with tabs **Staging Output**, **Run
Audit**, **Findings**, **Raw Rows**, **Methodology**.

## Inputs

- `--as-of YYYY-MM-DD` (default: today) — drives every period calculation.
- `--write-mode dry_run|write_staging` (default `dry_run`).
- `--environment staging` (staging-only).
- `--config` — path to an alternate `metric_config.yaml`.
- `--json` — full machine-readable run report.
- Credentials by **name** via env vars declared in config
  (`GOOGLE_SHEETS_CONNECTION`, `WAREHOUSE_CONNECTION`). Never inline secrets.

## Source wiring

Every source is currently a `local_export`: a read-only JSON transcription of a
human-downloaded export in `source_exports/`. This lets the full
normalize → validate → compute → stage path run without live credentials, while
provenance still points at the real (deny-listed) source id. Swapping a source
to live means changing `type:` to `gsheet` or `warehouse` and confirming the
tab and header row — nothing in the calc layer changes.

Ads SOTA ML reads the **S-pillar updates sheet**, not the 2026 S-Scale Pillar
doc: the Google Docs API is not enabled for the Hex service account, only
Sheets. Its `tab_name` is still `CONFIRM`.

## Turning a metric from REVIEW → PASS

1. Confirm the source with its owner (see `agent_build_plan.md` §8.5 contact directory).
2. Fill the exact `tab_name` + `header_row` in `config/metric_config.yaml`.
3. Set the goal record's values and flip `approval_status: approved` with
   `approval_evidence`.
4. For warehouse metrics, register a read-only runner
   (`cats_ingest.adapters.warehouse.register_runner`) and set the real table in
   the `sql/*.sql` file.
5. Re-run `dry_run`, confirm the row is `PASS`, then `write_staging`.

## Output columns

`metric, value, MoM, QoQ, YoY, current_quarter_goal, QTD_goal,
pacing_to_QTD_goal, goal_2026` plus audit fields `unit, as_of, quarter, status,
source_status, validation_status, review_reason, source_url, source_tab,
run_id`.

## Agent prompt

> Refresh the CATS Scorecard staging output for Scale, S+M FTE, and Shopping
> Revenue pacing (Tier 1), using the Operations Runbook as the source of truth.
> Read sources read-only for the configured as-of date; normalize, then validate
> schema, freshness, keys, row counts, zero-vs-missing, and reconciliation.
> Compute value, MoM, QoQ, YoY, current-quarter goal, QTD goal, pace, and 2026
> goal. Do not guess goals, mappings, or periods. Write only to staging,
> idempotently. On any failed check, preserve the last known good result, mark
> the metric REVIEW or BLOCKED with a reason, and never fill gaps. Never expose
> credentials or touch the dashboard or sources. Return a run report: status,
> as-of, source status, each row, findings, overrides, and evidence.

## Layout

```
config/metric_config.yaml     # source + goal registry (single source of truth)
cats_ingest/
  safety.py                   # deny-list + read-only enforcement (the guardrail)
  config.py periods.py schema.py goals.py validation.py audit.py writer.py
  pipeline.py cli.py
  adapters/                   # gsheet, gdoc, warehouse, hex_blocked, local_export
  calculations/               # the 7 metric modules (pure numeric cores)
source_exports/               # read-only JSON transcriptions of source exports
sql/                          # read-only SELECT templates (confirm tables)
tests/                        # safety, validation, calculation, pipeline tests
```
