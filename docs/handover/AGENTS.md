# CATS Scale + Revenue/FTE Ingestion Skill — MVP Build Plan

## 1. Outcome

A repeatable agent that reads approved source data, computes the CATS **Scale**, **Revenue / S+M FTE**, and **Shopping Revenue pacing** metrics using the [Operations Runbook](OPERATIONS_RUNBOOK.md) methodology, validates the result, and writes a **staging sheet**.

**Staging-only, always.** The skill reads sources read-only and writes only to the staging output. It never edits the Hex dashboard or any source workbook. When a source, schema, goal, or reconciliation check fails, it stops with a clearly labelled review result instead of guessing or forward-filling.

## 2. Scope

### Metrics and cadence

| Metric | Cadence |
|---|---|
| Operational Excellence, Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML, Revenue / S+M FTE | Monthly (actuals) |
| Shopping Revenue — paced QTD goal vs warehouse actual | Weekly |
| Goals for all of the above | Quarterly (confirmed at roll) |

### Staging columns (one row per metric)

Required: `metric`, `value`, `MoM`, `QoQ`, `YoY`, `current_quarter_goal`, `QTD_goal`, `pacing_to_QTD_goal`, `goal_2026`.

Auditability (also written): `unit`, `as_of`, `quarter`, `status`, `source_status`, `validation_status`, `review_reason`, `source_url`, `source_tab`, `run_id`.

### Out of scope for the MVP

- Promoting to / editing the production dashboard, or editing any source workbook.
- New metric definitions not in the runbook.
- Silent forward-filling of stale/missing actuals.
- Guessing source tabs, header rows, goal values, grade mappings, or manual overrides.

## 3. Sources, owners, and triggers

Canonical links and **exact tabs/header rows** live in `config/metric_config.yaml`. Do not rely on Hex notebook dataframe names. Each source declares: URL, type, tab/query, header row, cadence, `source_as_of`, and a freshness SLA. Credentials are referenced **by name only** from the runtime secret store.

| Metric | Actuals source | Goal source | Owner / verifier | Trigger |
|---|---|---|---|---|
| Operational Excellence | [Manager Dashboard](https://docs.google.com/spreadsheets/d/1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU/edit?gid=876519945) team scores | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Nikhil Khanted | New month column landed |
| Cloud Savings | [Efficiencies tracker](https://docs.google.com/spreadsheets/d/1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY/edit?gid=915660352) (C1) | Roadmap KPIs | Scale team / Nikhil Khanted | C1 moved |
| Model Velocity | [Ranking/Retrieval](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4) + [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) launches | Roadmap KPIs | Scale team / Nikhil Khanted | New launches on 2026 tabs |
| Experimentation Velocity | Ads experiment SQL, else [Insights QTD card](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) fallback | Roadmap KPIs | Scale team / Nikhil Khanted | Month close; or SQL down |
| Ads SOTA ML | [2026 S-Scale Pillar doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c) latest dated grade | Roadmap KPIs | Scale team / Virgilio Pigliucci | New readout posted |
| Revenue / S+M FTE | Revenue warehouse + [Rev/S+M FTE sheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) | Revenue goal plan | Aaron Nelson / Nick Asaad | New FTE month lands |
| Shopping Revenue (pacing) | Revenue warehouse | [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712) col **AO** (paced QTD) + Roadmap KPIs (CQ/FY) | Vinay Sridhar / Ryan Sekulic | Col AO updated; run Mon after the 9:00 run |
| Goals (all) | — | Roadmap KPIs (auto-pull) | Metric owners | Quarter roll |

Owner/source of record for every metric: [CATS Scorecard Data Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).

## 4. Metric methodology

Calculations run after normalization, before rendering. The as-of date is supplied by the run, never hard-coded.

For **every** metric the automatic path is the same: **read (read-only) → normalize → validate → compute → stage + audit.** The human step is always the same shape too: **confirm the upstream source actually landed — a populated cell is never treated as confirmation.** The per-metric human check below names who confirms what.

### Operational Excellence
- Latest completed month-end; sum team scores, exclude summary rows.
- MoM vs prior month · QoQ vs prior quarter-end · YoY vs December 2025.
- **Human check:** new month column landed (Nikhil Khanted).

### Cloud Savings
- YTD savings from the Efficiencies tracker (C1).
- **MoM / QoQ / YoY intentionally blank** — no reliable as-of date to time-phase against, so any period-over-period figure would mislead. Emitted null by design, not as a missing source.
- Preserve zero savings vs missing savings.
- **Human check:** C1 moved (Nikhil Khanted).

### Model Velocity
- Count qualifying launches QTD across Ranking + Retrieval + Shopping.
- Exclude backtests, bug fixes, deprecations, zero-impact, and undated records.
- MoM / QoQ / YoY use the runbook's approved comparison periods.
- **Human check:** new launches logged on the 2026 tabs (Nikhil Khanted).

### Experimentation Velocity
- Count distinct Ads experiments QTD with `unique_objects > 1000` via the approved SQL. Read **QTD, not YTD**.
- **`_EXP_COUNTS` fallback:** when SQL is down, a manually entered QTD count keyed by `(year, quarter)`, read off the [Insights QTD card](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest). Accepted **only** with `value`, `owner`, `timestamp`, `reason`, `evidence`; flagged `REVIEW`; replaced by SQL once restored and reconciled.
- **Human check:** if the fallback is used, its owner confirms it (Nikhil Khanted).

### Ads SOTA ML
- Most recent dated grade from the pillar doc. MoM / QoQ / YoY blank unless comparable historical grades exist.
- **No pace** until the approved grade→rank mapping is configured — a missing mapping produces `REVIEW`, never a guessed numeric pace.
- **Human check:** new readout posted; Virgilio Pigliucci approves the grade→rank map.

### Revenue / S+M FTE
- Join warehouse revenue to the Rev/S+M FTE sheet by month; use the latest month with **both** revenue and headcount. **Never pair newer revenue with older headcount.**
- `value` = revenue ÷ matched FTE. MoM / QoQ / YoY use the matched monthly series.
- CQ and QTD goals interpolate between the approved quarterly waypoints (linear path).
- **Human check:** new FTE month landed (Nick Asaad).

### Shopping Revenue (weekly pacing)
- `value` = warehouse Shopping Revenue QTD. `QTD_goal` = pacing sheet col **AO**, current-week row (**read from the sheet, not computed**). `current_quarter_goal`/`goal_2026` = Roadmap KPIs. `pace = value / QTD_goal`; status = `shopping_pace`.
- **Week-over-week movement check:** an unchanged goal vs last week is allowed but flagged `NEEDS VERIFICATION`, since an unmoved cell can mean the sheet wasn't updated.
- **Human check:** Vinay Sridhar updated the current-week AO number; at roll, confirm the `Q{n} DPA tracker` tab and CQ/FY (Ryan Sekulic · Vinay Sridhar).

## 5. Goals, pacing, and status

### Goal & pacing contract
- Goals are explicit config records: source link, effective period, unit, direction, owner, approval status.
- `current_quarter_goal` = full-quarter target; `QTD_goal` = time-phased goal through the as-of date; `pacing_to_QTD_goal = value / QTD_goal` for positive metrics.
- Pacing rules: **Scale** = runbook linear pacing across the year; **Revenue / S+M FTE** = interpolate approved quarterly waypoints; **Shopping Revenue** = `external_weekly_paced` (goal taken from col AO, not computed).
- **Never compute a pace** when the goal is missing, stale, unit-incompatible, or not approved → `REVIEW`.

### Status colour (business signal)
| Rule | Green | Yellow | Red | Applies to |
|---|---|---|---|---|
| `goal_binary` | ≥100% | — | <100% | Scale rows + Revenue / S+M FTE |
| `shopping_pace` | ≥85% | 70–85% | <70% | Shopping Revenue only |

Yellow is a **healthy** status, not a verification flag. Rows with no computable target are grey.

### Run flag (publish decision) — separate from colour
- **PASS** — all gates pass; publishable to staging.
- **NEEDS VERIFICATION** (`REVIEW`) — staged with a reason but **not** published; needs a human.
- **FAIL** (`BLOCKED`) — a hard gate failed; not published and the last known good result is preserved.

## 6. Deterministic pipeline

```text
Identify source → Extract raw rows → Normalize schema & units → Validate source & keys
→ Calculate actuals & comparisons → Reconcile to source totals/cards
→ Write staging output → Write audit & provenance → Report status
```

Every source adapter returns the same envelope: `source_id`, `source_url`, `source_tab_or_query`, `pulled_at`, `source_as_of`, `raw_rows`, `source_status`. Hex-only sources use a separate adapter that is **explicitly blocked** — a Google service account can read shared Sheets but does not grant Hex access.

## 7. Validation gates

A metric is publishable (**PASS**) only when all applicable checks pass:

1. Required columns and data types exist.
2. Dates parse; periods fall in the expected reporting window.
3. Metric-period keys are unique.
4. Required keys are not missing.
5. Source freshness is within the metric SLA.
6. Row-count change vs the previous good run is within tolerance.
7. Zero is distinguished from null/missing.
8. Derived totals reconcile to the source total/approved card within tolerance.
9. Manual overrides include value, reason, owner, timestamp, and evidence link.
10. Revenue and FTE are joined to the same month.
11. Units are compatible before ratios or comparisons.
12. Weekly pacing: current-quarter DPA tracker tab exists and col AO has a non-blank current-week row (unchanged vs last week → `NEEDS VERIFICATION`).

A failure blocks only the affected metric and is visible in `Run Audit`; it must never silently produce a complete-looking row.

## 8. Safe failure and credential boundaries

- Reference credentials by name (`GOOGLE_SHEETS_CONNECTION`, `WAREHOUSE_CONNECTION`); never log or write the JSON. Keep dev and prod credentials separate; use least-privilege **read-only** access.
- Retry transient reads with bounded exponential backoff.
- Staging writes are idempotent by `run_id`, `metric`, `as_of`.
- A failed run preserves the last known good staging result and is clearly marked failed.
- Alert after the configured repeated-failure threshold.

## 9. Skill interface and agent prompt

**Inputs:** `as_of_date` (default: latest completed reporting date) · `environment` (`staging`) · `write_mode` (`dry_run` | `write_staging`) · source + approved-goal config · runtime credential reference.

**Agent prompt:**

```text
Refresh the CATS Scorecard staging output for Scale, Revenue / S+M FTE, and Shopping
Revenue pacing using the Operations Runbook as the source of truth.

Run only for approved sources and the configured as-of date. Read raw source rows
read-only, normalize to the metric contract, validate schema, freshness, keys, row
counts, zero-vs-missing, and reconciliation, then compute value, MoM, QoQ, YoY,
current-quarter goal, QTD goal, pacing, and 2026 goal.

Use the runbook methodology exactly. Do not guess missing goals, source/grade mappings,
manual overrides, or comparison periods. Keep ingestion, calculation, and rendering
separate. Preserve raw rows and write run audit/provenance every run.

Write only to the staging output, idempotently. If a check fails, preserve the last
known good result, mark the metric REVIEW or BLOCKED, describe the failure, and do not
fill gaps. Never expose credentials or touch the dashboard/sources.

Return a concise run report: run status, as-of date, source status, each metric's row,
validation findings, manual overrides, and the evidence needed for review.
```

## 10. Implementation steps

1. Freeze the **source registry**: URLs, exact tabs/queries, header rows, owners, cadence, SLAs (incl. `shopping_pacing_sheet`).
2. Freeze the **goal registry**: quarterly waypoints, 2026 goals, units, direction, approval evidence, the SOTA grade-map decision, and `shopping_revenue` (`external_weekly_paced`).
3. Implement source adapters for Scale + warehouse/FTE + shopping pacing; explicitly block Hex-only reads.
4. Implement the normalized schema: `metric`, `period`, `value`, `unit`, `source_id`, `source_as_of`, optional `manual_override`.
5. Implement the calculation modules with dynamic period selection and no hard-coded dates.
6. Implement validation gates (incl. `shopping_pace` and the weekly movement check) and an audit record before enabling writes.
7. Add the idempotent staging writer with output, raw-rows, audit, and methodology tabs.
8. Test against a staging workbook with known values: zeros, nulls, duplicate keys, stale sources, missing FTE, the manual experiment-count fallback, and an unchanged weekly AO.
9. Run two consecutive live staging cycles and reconcile every row with source evidence.
10. Pilot with the scorecard owners; promote only after both cycles pass and false-positive behavior is acceptable.

## 11. Acceptance criteria

- Every output row has the eight metric fields or an explicit null plus reason.
- Every non-null value has source and as-of provenance; no stale source is presented as current.
- Revenue / FTE never mixes months across revenue and headcount.
- A failed source cannot overwrite the last known good result.
- Re-running the same inputs produces the same staging output (idempotent).
- Two consecutive live staging runs pass schema, freshness, uniqueness, reconciliation, and goal checks before any dashboard promotion.

## 12. Validation examples

- **Successful run** — all sources current, goals approved, totals reconcile; the sheet is written `PASS` with metric-level Green/Red (or `shopping_pace` Yellow).
- **Failed run** — the FTE sheet is one month behind revenue. Revenue / S+M FTE is `BLOCKED` for the new period, the last known good result is preserved, and the audit names the missing month and owner without filling the gap.
- **Manual fallback** — Experimentation SQL is unavailable; the approved `_EXP_COUNTS` value is used only with owner, timestamp, reason, and evidence link, flagged `REVIEW` until SQL is restored and reconciled.
- **Weekly pacing** — Vinay updates col AO; the Monday post-9:00 run stages Shopping Revenue with its `shopping_pace` colour. If col AO is unchanged from last week, the row is flagged `NEEDS VERIFICATION` and not published until confirmed.
