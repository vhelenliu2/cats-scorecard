# CATS staging ingestion agent

Staging-only automation for the CATS Scorecard Tier-1 rows. It reads approved
sources read-only, computes each metric per the runbook, validates, and writes
an isolated staging workbook. It never touches the Hex dashboard or any source.

| File | What it is |
|---|---|
| [`agent_build_plan.md`](agent_build_plan.md) | **Build plan** — tiers, cadence, metric register, methodology, status rules, validation gates, contact directory |
| [`SKILL.md`](SKILL.md) | **Skills pack** — the agent skill definition: safety contract, how to run, inputs, REVIEW→PASS procedure, agent prompt |
| [`skills/`](skills/README.md) | The eight skill packs built from the build plan and runbook — goal workflow (step 0 → 5 + orchestrator) and scorecard-ingest. Documentation only; see that index to make one runnable again |
| [`../OPERATIONS_RUNBOOK.md`](../OPERATIONS_RUNBOOK.md) | Source of truth for the methodology this implements |

## Run it

```bash
cd docs/handover/agent
pip install -r requirements.txt
python3 tests/run_tests.py                                          # 28 tests
python3 -m cats_ingest.cli --as-of 2026-09-25 --write-mode dry_run
python3 -m cats_ingest.cli --as-of 2026-09-25 --write-mode write_staging
```

Output lands in `staging_output/` (git-ignored — regenerate it, don't commit
it) as `staging_<run_id>.xlsx` plus `staging_latest.xlsx`, with tabs **Staging
Output**, **Run Audit**, **Findings**, **Raw Rows**, **Methodology**.

## What state it is in

**Tier 1 (ingest) is implemented.** Seven metrics: Operational Excellence,
Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML,
Revenue / S+M FTE, Shopping Revenue pacing.

**Tier 2 (verify) is not built.** `agent_build_plan.md` §8 specifies the per-row check
battery, the `check_status` values, and the routed-notification behaviour, but
no code implements it — there is no `--verify` flag.

A `dry_run` at `as_of=2026-09-25` currently reports 3 `PASS` and 4 `REVIEW`.
Every `REVIEW` is a deliberate refusal to guess, not a bug:

| Metric | Why it is REVIEW | Who clears it |
|---|---|---|
| Experimentation Velocity | Experimentation SQL unavailable; the evidenced `_EXP_COUNTS` manual fallback (141 QTD) is staged but needs sign-off | Nikhil Khanted |
| Ads SOTA ML | Grade `B-` reads fine, but pacing needs the approved grade→rank map, which is not configured | Virgilio Pigliucci |
| Revenue / S+M FTE | No warehouse runner registered, so the revenue leg is MISSING | Nick Asaad · Aaron Nelson |
| Shopping Revenue | Col AO QTD goal and the FY goal are still `CONFIRM` | Vinay Sridhar · Ryan Sekulic |

## Sources are stubbed, deliberately

Every source is wired as `local_export`: a read-only JSON transcription in
`source_exports/` of an export a human downloaded. This runs the full
normalize → validate → compute → stage path without live credentials, while
provenance still points at the real source id. Going live means changing
`type:` to `gsheet` or `warehouse` in `config/metric_config.yaml` and
confirming the tab and header row. The calc layer does not change.

**Known gap:** Ads SOTA ML now points at the S-pillar updates sheet rather than
the 2026 S-Scale Pillar doc, because the Google Docs API is not enabled for the
Hex service account. Its `tab_name` is still `CONFIRM` — confirm the tab before
reading it live.

## Guardrails

`cats_ingest/safety.py` is the hard boundary and is covered by tests:

- Writes are refused against any known dashboard or source id (deny-list).
- Source reads request `*.readonly` OAuth scopes only; a writable scope raises.
- The warehouse adapter refuses any non-SELECT SQL.
- The Hex adapter is an explicit block — a Google service account reads shared
  Sheets, not Hex.
- Nothing is guessed: unknown tabs, header rows, goals, and mappings stay
  `CONFIRM`/`null` and the metric is emitted `REVIEW`/`BLOCKED`.
- A real `0` is preserved; an unreadable value is `null` plus a reason.
- Re-running identical inputs reproduces an identical file; a failed run never
  overwrites `staging_last_known_good.xlsx`.
