# CATS Scale + FTE Ingestion Skill — MVP Build Plan

## 1. Outcome

A repeatable agent that reads approved source data, computes the CATS **Scale**, **S+M FTE**, and **Shopping Revenue pacing** metrics using the [Operations Runbook](OPERATIONS_RUNBOOK.md) methodology, validates the result, and writes a **staging sheet**.

**Staging-only, always.** The skill reads sources read-only and writes only to the staging output. It never edits the Hex dashboard or any source workbook. When a source, schema, goal, or reconciliation check fails, it stops with a clearly labelled review result instead of guessing or forward-filling.

## 2. Scope

### Metrics and cadence

| Metric | Cadence | Trigger |
|---|---|---|
| Operational Excellence, Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML, S+M FTE | Monthly (actuals) | **Second week of the month** |
| Shopping Revenue — paced QTD goal vs warehouse actual | Weekly | **3rd day of the week** |
| Goals for all of the above | Quarterly (confirmed at roll) | Quarter roll (week 1) |

The table above is **Tier 1** (high-risk, fully automated ingest — §1–§12). §13–§15 extend this into a **complete dashboard-maintenance plan** covering every remaining (Tier 2) metric with read-only verification, in priority order (high-risk first).

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
| Operational Excellence | [Manager Dashboard](https://docs.google.com/spreadsheets/d/1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU/edit?gid=876519945) team scores | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Nikhil Khanted | Second week of the month |
| Cloud Savings | [Efficiencies tracker](https://docs.google.com/spreadsheets/d/1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY/edit?gid=915660352) (C1) | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Nikhil Khanted | Second week of the month |
| Model Velocity | [Ranking](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=477633216#gid=477633216) · [Retrieval](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=972292259#gid=972292259) · [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934#gid=90038934) launches | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Nikhil Khanted | Second week of the month |
| Experimentation Velocity | Ads experiment SQL, else [Insights QTD card](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) fallback | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Nikhil Khanted | Second week of the month |
| Ads SOTA ML | [2026 S-Scale Pillar doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) latest dated grade | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Scale team / Virgilio Pigliucci | Second week of the month |
| S+M FTE | [Rev/S+M FTE sheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) (headcount) | — (actual-only in MVP; revenue lives in the warehouse) | Nick Asaad | Second week of the month |
| Shopping Revenue (pacing) | Revenue warehouse | [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) col **AO** (paced QTD) + [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) (CQ/FY) | Vinay Sridhar / Ryan Sekulic | 3rd day of the week (after col AO update) |
| Goals (all) | — | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) (auto-pull) | Metric owners | Quarter roll |

Owner/source of record for every metric: [CATS Scorecard Data Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).

Each schedule trigger still requires the upstream source to have landed (the per-metric human check in §4). If it hasn't, the metric is held as `NEEDS VERIFICATION` rather than run on stale data.

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

### S+M FTE
- Read S+M FTE **headcount** from the Rev/S+M FTE sheet for the latest completed month.
- `value` = latest-month headcount. MoM / QoQ / YoY use the monthly headcount series.
- **Revenue is out of scope for the MVP** — it already lives in the data warehouse/dashboard, so there is no urgent need to re-ingest it. No revenue join and no Revenue/FTE ratio here; the metric is actual-only headcount (status grey until a headcount goal is approved).
- **Human check:** new FTE month landed (Nick Asaad).

### Shopping Revenue (weekly pacing)
- `value` = warehouse Shopping Revenue QTD. `QTD_goal` = pacing sheet col **AO**, current-week row (**read from the sheet, not computed**). `current_quarter_goal`/`goal_2026` = Roadmap KPIs. `pace = value / QTD_goal`; status = `shopping_pace`.
- **Week-over-week movement check:** an unchanged goal vs last week is allowed but flagged `NEEDS VERIFICATION`, since an unmoved cell can mean the sheet wasn't updated.
- **Human check:** Vinay Sridhar updated the current-week AO number; at roll, confirm the `Q{n} DPA tracker` tab and CQ/FY (Ryan Sekulic · Vinay Sridhar).

## 5. Goals, pacing, and status

### Goal & pacing contract
- Goals are explicit config records: source link, effective period, unit, direction, owner, approval status.
- `current_quarter_goal` = full-quarter target; `QTD_goal` = time-phased goal through the as-of date; `pacing_to_QTD_goal = value / QTD_goal` for positive metrics.
- Pacing rules: **Scale** = runbook linear pacing across the year; **Shopping Revenue** = `external_weekly_paced` (goal taken from col AO, not computed). **S+M FTE** is actual-only in the MVP (no pacing goal).
- **Never compute a pace** when the goal is missing, stale, unit-incompatible, or not approved → `REVIEW`.

### Status colour (business signal)
| Rule | Green | Yellow | Red | Applies to |
|---|---|---|---|---|
| `goal_binary` | ≥100% | — | <100% | Scale rows |
| `shopping_pace` | ≥85% | 70–85% | <70% | Shopping Revenue only |

Yellow is a **healthy** status, not a verification flag. Rows with no computable target are grey (S+M FTE in the MVP, plus any metric missing an approved goal).

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
10. S+M FTE uses the latest month present in the headcount sheet (no cross-source month mixing).
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
Refresh the CATS Scorecard staging output for Scale, S+M FTE, and Shopping
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
3. Implement source adapters: Scale sheets, the FTE headcount sheet, the warehouse (Shopping Revenue actual + Experimentation SQL), and shopping pacing; explicitly block Hex-only reads.
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
- S+M FTE reports the latest available headcount month; it never mixes months across sources.
- A failed source cannot overwrite the last known good result.
- Re-running the same inputs produces the same staging output (idempotent).
- Two consecutive live staging runs pass schema, freshness, uniqueness, reconciliation, and goal checks before any dashboard promotion.

## 12. Validation examples

- **Successful run** — all sources current, goals approved, totals reconcile; the sheet is written `PASS` with metric-level Green/Red (or `shopping_pace` Yellow).
- **Failed run** — the FTE sheet has no new month. S+M FTE is `BLOCKED` for the new period, the last known good result is preserved, and the audit names the missing month and owner without filling the gap.
- **Manual fallback** — Experimentation SQL is unavailable; the approved `_EXP_COUNTS` value is used only with owner, timestamp, reason, and evidence link, flagged `REVIEW` until SQL is restored and reconciled.
- **Weekly pacing** — Vinay updates col AO; the 3rd-day-of-week run stages Shopping Revenue with its `shopping_pace` colour. If col AO is unchanged from last week, the row is flagged `NEEDS VERIFICATION` and not published until confirmed.

---

# Full dashboard coverage (Tier 2)

§1–§12 are **Tier 1**: the high-risk metrics the agent fully ingests, computes, validates, and stages. Tackle those first. §13–§15 below extend the plan to **every remaining row on the dashboard** so the whole thing is managed and maintained — but at a lower priority and with a lighter touch.

## 13. Coverage tiers and operating model

- **Tier 1 — high-risk (automated ingest).** Scale ×5, S+M FTE, Shopping Revenue pacing (§1–§12). The agent reads sources read-only, computes, validates, and writes the staging sheet.
- **Tier 2 — lower-risk (verification-only).** Every other dashboard row. These are warehouse- or sheet-backed and already refresh on the 9:00 AM Chicago run, so the agent does **not** recompute them. It runs read-only **checks** and writes a per-metric check result: did the source land (freshness), did the goal roll, is the status colour computable, and does anything look anomalous. Output is a check status (`PASS` / `NEEDS VERIFICATION` / `FAIL`), not a recomputed value.

**Same guardrails for both tiers:** staging-only; read-only sources; never edit Hex or any source workbook; never guess; never turn a failed pull into a `0`; hold anything uncertain as `NEEDS VERIFICATION`.

Tier-2 behaviours the agent must **respect, not "fix"** (from the runbook):
- **Intentional blanks:** Budget Utilization (source table died 2 Jun 2026); Cloud Savings MoM/QoQ/YoY; grey rows (gROAS, Reach/Frequency/Depth, Retention, HQ Signal).
- **Display duplicates:** the Supply-tab DAUq and Ad Impressions copies are forced grey — their goals live on Company Level.
- **Manual notebook constants (human, not agent):** `IMPRESSIONS_GOALS` at quarter roll, `_EXP_COUNTS` when SQL is down, the SOTA grade. The agent flags these for a human; it never edits Hex.
- **Only 10 valid status-rule names** exist; an unknown rule fails the tab build. The agent verifies each row's rule is one of: `goal_binary`, `goal_rev_2m`, `goal_rev_5m`, `impressions_pacing`, `shopping_pace`, `ab_goal`, `yoy`, `booking_quota`, `lower_bounded_goal`, `grey`.
- **A/B label trap:** a renamed label in a goals/tracker sheet silently blanks the goal. The agent compares labels to the canonical map and flags drift (keep `Post-Install CPA A/B`, plain `CPA A/B`, and `CPI A/B` distinct).

## 14. Tier-2 metric register

Owners/verifiers are per the runbook Step 0 table and the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).

### Company Level Goals tab

| Metric | Actual source (cadence) | Goal source | Status rule | Agent check |
|---|---|---|---|---|
| Ads Realized Revenue | Warehouse (daily) | `daily_quota_profile` (warehouse) | `goal_binary` | Fresh; new-quarter quota loaded; colour computable |
| MAA (+ LCS / MM / SMB) | Warehouse (daily) | [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562) | `goal_binary` | Fresh; new-quarter daily goals rolled |
| DAUq (+ US / ROW) | Warehouse (daily) | [DAUq Master](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431) | `impressions_pacing` | Fresh; Latest Forecast on new quarter; millions→users scale sane |
| Ad Impressions (US / ROW) | Warehouse (daily) | `IMPRESSIONS_GOALS` (manual, from [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?gid=1740552033)) | `impressions_pacing` | Flag if the quarter's manual goal key is missing |
| eCPM | Warehouse (daily) | derived (impressions + revenue) | derived | Sanity vs impressions/revenue; no edit |
| Thriving | Warehouse (daily) | — | `grey` | Freshness only |
| Tier 2 A/B — CTR, kICR4, PiIR, VVR6, CPC, kCPA | [Ads Launch Review Sign-up](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) (weekly) | Roadmap KPIs | `ab_goal` | Label integrity; grey in months 1–2 is expected |
| Shopping ROAS A/B | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) (weekly) | Shopping 3H | `ab_goal` | Label integrity; new-quarter row present |

### CATS SC / KPIs tab (Tier-1 rows omitted)

| Metric | Actual source (cadence) | Goal source | Status rule | Agent check |
|---|---|---|---|---|
| Overall Measured Revenue | Warehouse (daily) | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | `goal_rev_5m` | Fresh; quarterly step rolled |
| Upper Funnel Revenue | Brand pillar feed (daily) | [Brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit) | `goal_rev_2m` | Fresh; CQ/FY confirmed at roll (Emily Glauser) |
| High Quality Signal Adoption | Warehouse/Hex (daily) | none published | `grey` | Stays grey; reference target from owners only |
| A/B lifts (incl. Post-Install CPA) | [Ads Launch Review](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) (weekly) | Roadmap KPIs | `ab_goal` | Label integrity; keep Post-Install CPA vs plain CPA vs CPI distinct |
| gROAS, Reach / Frequency / Depth, Retention | Warehouse/Hex (daily) | none | `grey` | Freshness only; stays grey |

### Ads Product & GTM tab (actuals only; goals live on KPIs)

| Metric | Actual source (cadence) | Status rule | Agent check |
|---|---|---|---|
| Shopping, Measured (GTM copies) | Warehouse (daily) | grey copy | Fresh; grey by design |
| MixShift iCR | Warehouse (daily) | `yoy` | Fresh; YoY direction sane |
| MixShift CPA | Warehouse (daily) | `yoy` (inverted — falling cost is good) | Fresh; inverted test honoured |
| New Advertisers Activated | Warehouse (daily) | `yoy` | Freshness |
| Marketplace Efficiency | Warehouse (daily) | `lower_bounded_goal` | Floor present |
| Input Demand — % Booking to Quota | Warehouse (daily) | `booking_quota` | Week-of-quarter threshold sane |
| Budget Utilization | — (source died 2 Jun 2026) | — | Intentional blank; leave it (Dana owns replace/retire) |

### Ads Supply Drivers tab (warehouse-backed)

| Metric | Actual source (cadence) | Goal | Status rule | Agent check |
|---|---|---|---|---|
| DAUq (Supply copy) | Warehouse (daily) | from Step 1 sheet | forced `grey` (duplicate) | Fresh; grey by design |
| WAUq | Warehouse (daily) | none | `grey` | Freshness only |
| Monetizable Feed | Warehouse (daily) | none | `yoy` | Fresh; direction sane |
| PDP | Warehouse (daily) | none | `yoy` | Fresh; direction sane |

## 15. Upkeep cycles — what the agent runs, when

Same triggers as Tier 1 (§2). Each cycle: **Tier 1 = ingest + compute + stage; Tier 2 = read-only verify + flag.**

### Quarter roll (week 1)
- **Goals rolled?** For every metric with a goal, confirm the new quarter's column/step exists across Roadmap KPIs, MAB Goaling, DAUq Master, Brand goals doc, Shopping 3H, and the pacing sheet. A last-quarter or blank column → `NEEDS VERIFICATION` naming the owner.
- **Manual constants:** flag `IMPRESSIONS_GOALS` (new-quarter key), the SOTA grade→rank map, and `_EXP_COUNTS` (if SQL down) for a human — the agent never edits Hex.
- **HQ Signal:** stays grey; reference target confirmed with owners (no source).
- Owners confirm goals are **final** — a populated cell is not confirmation.

### Monthly upkeep (second week of the month)
- **Tier 1:** compute + stage the Scale five and S+M FTE.
- **Tier 2:** confirm each monthly/warehouse source is fresh and its goal still present. Flag any Scale row that exactly matches last month (possible failed pull falling back to a checksum) as `NEEDS VERIFICATION`; confirm the FTE month landed (Nick Asaad).

### Weekly upkeep (3rd day of the week)
- **Tier 1:** stage Shopping Revenue pacing (col AO current-week; week-over-week movement check).
- **Tier 2:** confirm the weekly A/B trackers updated ([Ads Launch Review](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925), [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934)) and no A/B goal went blank from a renamed label. A/B rows grey in months 1–2 are expected.

### Every run (freshness gate, all tiers)
- Read the clock (`Quarter dates based on latest date`): a metric >3 days behind is dropped from the clock → `NEEDS VERIFICATION`; a `WARN systemic freshness incident` (most sources behind) holds all pacing colours and is flagged before anyone reads the numbers.
- `0` means zero; `—` means no data. Never convert a failed pull into a zero.
