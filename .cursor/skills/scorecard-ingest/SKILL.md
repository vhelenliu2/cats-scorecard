---
name: scorecard-ingest
description: >-
  Extracts CATS scorecard Google Sheet sources into a DS staging workbook with a
  stable schema, then validates publish-ready rows. Use when ingesting scorecard
  metrics from Google Sheets, building or refreshing the staging gsheet, pulling
  MAA or DAUq goals, or running Phase 1 sheet-to-dashboard ingestion.
---

# CATS Scorecard Ingest (Phase 1)

**Your role**: pull the existing source Google Sheet, normalize it into the DS
staging workbook, and hold anything uncertain. You do **not** set goals, rewrite
Hex parsers, or publish unconfirmed values as current.

This is the Phase 1 bridge from the source-review plan: agent extracts → DS
staging table → DS validates changed / late / unmatched rows. Hex should
eventually read **Staging Facts**, not the messy source layout.

Sibling workflow: goal *setting* is [goal-workflow-orchestrator](../goal-workflow-orchestrator/SKILL.md).
This skill only **moves a value from a sheet into staging**.

---

## Pilot scope (do not expand until this passes)

| metric_id | Registry name | Source | What we stage |
|---|---|---|---|
| `MET-B61F39994E32` | MAA (R28D), # | MAB Goaling 2026 → `Daily Goals Allocation` | CQ / QTD / FY **goals** |
| `MET-419D6C123B19` | DAUq (QTD), M | DAUq Master Sheet → `Latest Forecast` | CQ **goal** (QTD target = CQ) |

Catalog: [`catalog.json`](catalog.json). Schema and Hex cell IDs: [`reference.md`](reference.md).

Why these two: both are Tier 0, DS-managed Google Sheet **targets**, already
parsed in Hex, and they exercise two extractor shapes (tidy daily table vs
nested forecast). Segments (MAA LCS/MM/SMB, DAUq US/ROW) are extracted but
**not publish-ready** until they have Metric Registry rows.

Do **not** rewire the live dashboard to read staging until the user confirms
promotion. Validation = staging matches the live Hex parse.

---

## How to start

**"Ingest MAA/DAUq"** / **"refresh the staging sheet"** / **"validate sheet
goals"** → run the checklist below.

Default command (fixture self-test, no credentials):

```bash
python3 .cursor/skills/scorecard-ingest/scripts/run_pilot.py --mode fixture
```

Live pull (Hex secret or local service account):

```bash
python3 .cursor/skills/scorecard-ingest/scripts/run_pilot.py --mode gsheet --as-of YYYY-MM-DD --push
```

Excel export (when G-Sheet API access is blocked — export tabs from Drive first):

```bash
python3 .cursor/skills/scorecard-ingest/scripts/run_pilot.py \
  --mode xlsx --maa-xlsx path/to/mab.xlsx --dauq-xlsx path/to/dauq.xlsx \
  --as-of YYYY-MM-DD
```

`--as-of` must be Hex `latest_date` (max dt with data), not today.

---

## Checklist (copy and track)

```
Ingest Progress:
- [ ] 0. Pin metric_id from catalog (never hash a Hex display name)
- [ ] 1. Pull source sheet (gspread or Hex cell run)
- [ ] 2. Extract tidy staging rows
- [ ] 3. Validate (schema, units, parent/segment arithmetic)
- [ ] 4. Diff against last run — hold changed/unmatched rows
- [ ] 5. Write Staging Facts + Review Queue + Run Log
- [ ] 6. Compare to live Hex parse; report pass/fail
- [ ] 7. Update docs/ingestion/_state/pilot.md
```

### Step 0 — Pin IDs

Read [`catalog.json`](catalog.json) and the Metric Registry. **DAUq registry
name is `DAUq (QTD), M`; Hex parent is `DAUq (QTD), #`.** Hashing the Hex
name produces `MET-AA468AF6805F`, which will not join. Always use
`MET-419D6C123B19`.

### Step 1 — Pull

Prefer `run_pilot.py --mode gsheet` with `GOOGLE_SHEETS_CONNECTION` (same JSON
as the Hex secret) or `GOOGLE_APPLICATION_CREDENTIALS`.

If those are missing, run the Hex cells in [`catalog.json`](catalog.json)
`hex_cells` (Maa goals df, DAUq official targets df), save the printed
oracle, and/or paste [`hex_edits/TO_PASTE/ingest_pilot_dump.py`](../../../hex_edits/TO_PASTE/ingest_pilot_dump.py)
to dump `get_all_values()` into a JSON the local script can replay:

```bash
python3 .cursor/skills/scorecard-ingest/scripts/run_pilot.py --mode dump --dump path/to/dump.json
```

Do not query inaccessible tables. Do not stub source data as `None`.

### Step 2 — Extract

Call the extractor named on the catalog row. Extractors live in
`scripts/extract_maa.py` and `scripts/extract_dauq.py`. They take raw
`get_all_values()` lists — no pandas required.

Output is the Staging Facts contract in [`reference.md`](reference.md). Values
are **absolute and unformatted** (DAUq in users, not millions).

### Step 3 — Validate

```bash
python3 .cursor/skills/scorecard-ingest/scripts/validate.py path/to/staging_facts.json
```

Must fail loud on: missing `Date`/`Overall` (MAA), missing quarter column
(DAUq), DAUq still in millions (`0 < value < 1000`), unregistered segments
marked `publish_ready`, or `metric_id` that does not match the catalog.

**Shopping Revenue goals** (pacing sheet — not in the Hex notebook):

```bash
# Live pull (GOOGLE_SHEETS_CONNECTION or GOOGLE_APPLICATION_CREDENTIALS)
python3 .cursor/skills/scorecard-ingest/scripts/validate_shopping_goals.py \
  --mode gsheet --as-of 2026-09-12

# Offline fixture self-test (no credentials)
python3 .cursor/skills/scorecard-ingest/scripts/validate_shopping_goals.py \
  --mode fixture --as-of 2026-09-12
```

Oracle values live in `scripts/fixtures/shopping_goals_oracle.json`. Update
that file when the quarter goal or paced target changes — do not hardcode
fallbacks in Hex.

### Step 4 — Diff and hold

Compare to [`docs/ingestion/_state/last_staging.json`](../../../docs/ingestion/_state/last_staging.json)
when it exists.

| Situation | `confidence` | `publish_ready` |
|---|---|---|
| First clean extract | `high` | `true` (`approval_status=extracted_unconfirmed`) |
| Unchanged vs last run | `high` | `true` |
| Value changed | `review` | `false` — DS confirms |
| Unmatched / missing column / incomplete DAUq geo | `review` | `false` |
| Unregistered segment | `review` | `false` |
| Late vs SLA (no row for as-of / quarter) | `review` | `false` |

Unconfirmed goals stay in staging with `freshness_flag=unconfirmed`. They are
**not** silently blanked and **not** written as zero.

### Step 5 — Write staging

Always write the local run folder under `docs/ingestion/runs/<timestamp>/`.

With `--push`, upsert the Google Sheet tabs. Create the workbook on first run
and share with `staging.share_with`. **Never** touch governance original tabs
(`CATS-SC KPIS`, `Company-level goals summary`, `Company-level goals target and`).

Upsert by `metric_id + field_kind + period_type + planning_period`. Do not
wipe other metrics' rows.

### Step 6 — Validate against Hex

Oracle is the live Hex parse, not a second guess:

- MAA: `maa_eoq_goal` / `maa_qtd_goal` / `maa_2026_goal` printed by Company
  Level Goals Metrics
- DAUq: `dauq_sheet_goals` printed by `DAUq official targets df`

Pass only if parent CQ (and MAA QTD/FY) match within the tolerances in
[`reference.md`](reference.md). On mismatch, **do not push publish-ready
rows** — write Review Queue and stop.

### Step 7 — State

Update [`docs/ingestion/_state/pilot.md`](../../../docs/ingestion/_state/pilot.md)
after every run. A multi-day ingest is lost if you only track it in chat.

---

## Quality rules (from the source-review plan)

- Preserve the approved value, the period it applies to, the source link, and
  the confirmation date. A populated target is not necessarily current.
- Show overdue or unconfirmed goals as stale / unconfirmed — never as a
  confident green number with no provenance.
- Do not publish **manual actuals** that lack owner, evidence, or cadence.
  This pilot is **goals**, not actuals; warehouse actuals stay on their
  existing Hex SQL path.
- Promotion to Phase 2 (owner-filled template) only after fields, owner,
  refresh cadence, and exception path are stable for these two metrics.

## Do not

- Invent a `metric_id` for a display name. Unregistered → review queue.
- Average conflicting Hex vs sheet values. Hold and report both.
- Run `hex project run` for this workflow. Run the 1–2 gsheet cells, or the
  dump cell, then the local script.
- Edit source planning sheets. Staging is the write target.
