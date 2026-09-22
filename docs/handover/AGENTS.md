# CATS Scorecard — Ingestion & Maintenance Plan (MVP)

## 1. Outcome & guardrails

A repeatable agent that keeps the CATS Scorecard current: it **ingests** the high-risk metrics (compute → validate → stage) and **verifies** every other row, using the [Operations Runbook](OPERATIONS_RUNBOOK.md) as the source of truth.

**Guardrails (always):** staging-only; sources read-only; never edit the Hex dashboard or any source workbook; never guess a tab, header row, goal, or mapping; `0` means zero and `—` means no data (never turn a failed pull into a `0`); hold anything uncertain as `NEEDS VERIFICATION` rather than publishing it.

## 2. Operating model — tiers, cadence, flags

**Two tiers, priority-ordered (do Tier 1 first):**
- **Tier 1 — high-risk (ingest).** Scale ×5 (Operational Excellence, Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML), S+M FTE, Shopping Revenue pacing. The agent reads sources, computes, validates, and writes the staging sheet.
- **Tier 2 — lower-risk (verify).** Every other dashboard row. Already refreshed by the 9:00 AM Chicago run, so the agent does **not** recompute — it runs read-only checks (source landed? goal rolled? colour computable? anomaly?) and records a check status only.

**Cadence & triggers:**

| Scope | Cadence | Trigger |
|---|---|---|
| Scale ×5 + S+M FTE (actuals) | Monthly | **Second week of the month** |
| Shopping Revenue pacing | Weekly | **3rd day of the week** (after col AO update) |
| Goals (all metrics) | Quarterly | Quarter roll (week 1) |

A trigger still requires the upstream source to have landed; if not, hold as `NEEDS VERIFICATION` rather than run on stale data.

**Run flag (publish decision) — separate from the status colour:**
- `PASS` — all gates pass; publishable to staging.
- `NEEDS VERIFICATION` (`REVIEW`) — staged with a reason, not published; needs a human.
- `FAIL` (`BLOCKED`) — a hard gate failed; not published; last known good preserved.

**Staging columns (one row per metric):** `metric`, `value`, `MoM`, `QoQ`, `YoY`, `current_quarter_goal`, `QTD_goal`, `pacing_to_QTD_goal`, `goal_2026` — plus audit fields `unit`, `as_of`, `quarter`, `status`, `source_status`, `validation_status`, `review_reason`, `source_url`, `source_tab`, `run_id`.

## 3. Metric register

Exact tabs/header rows live in `config/metric_config.yaml` (do not rely on Hex notebook dataframe names). Owners/source-of-record per the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc). Status rules are defined in §5.

### Tier 1 — ingest (compute + stage); methodology in §4

| Metric | Actuals source (cadence) | Goal source | Rule | Owner / verifier |
|---|---|---|---|---|
| Operational Excellence | [Manager Dashboard](https://docs.google.com/spreadsheets/d/1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU/edit?gid=876519945) team scores (monthly) | [Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | `goal_binary` | Scale / Nikhil Khanted |
| Cloud Savings | [Efficiencies tracker](https://docs.google.com/spreadsheets/d/1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY/edit?gid=915660352) C1 (monthly) | Roadmap KPIs | `goal_binary` | Scale / Nikhil Khanted |
| Model Velocity | [Ranking](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=477633216#gid=477633216) · [Retrieval](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=972292259#gid=972292259) · [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934#gid=90038934) launches (monthly) | Roadmap KPIs | `goal_binary` | Scale / Nikhil Khanted |
| Experimentation Velocity | Ads experiment SQL, else [Insights QTD card](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) (monthly) | Roadmap KPIs | `goal_binary` | Scale / Nikhil Khanted |
| Ads SOTA ML | [2026 S-Scale Pillar doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) grade (monthly) | Roadmap KPIs | `goal_binary` | Scale / Virgilio Pigliucci |
| S+M FTE | [Rev/S+M FTE sheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) headcount (monthly) | — (actual-only) | `grey` | Nick Asaad |
| Shopping Revenue (pacing) | Revenue warehouse (weekly) | [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) col **AO** + Roadmap KPIs (CQ/FY) | `shopping_pace` | Vinay Sridhar / Ryan Sekulic |

### Tier 2 — verify (read-only checks), grouped by tab

Every Tier-2 check confirms freshness + goal present/rolled + colour computable; the **Note** column adds the metric-specific catch.

**Company Level Goals**

| Metric | Source (cadence) | Goal | Rule | Note |
|---|---|---|---|---|
| Ads Realized Revenue | Warehouse (daily) | `daily_quota_profile` | `goal_binary` | new-quarter quota loaded |
| MAA (+ LCS / MM / SMB) | Warehouse (daily) | [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562) | `goal_binary` | new-quarter daily goals rolled |
| DAUq (+ US / ROW) | Warehouse (daily) | [DAUq Master](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431) | `impressions_pacing` | Latest Forecast on new quarter; millions→users scale |
| Ad Impressions (US / ROW) | Warehouse (daily) | `IMPRESSIONS_GOALS` manual, from [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?gid=1740552033) | `impressions_pacing` | flag if the quarter's manual key is missing |
| eCPM | Warehouse (daily) | derived (impressions + revenue) | derived | sanity vs impressions/revenue |
| Thriving | Warehouse (daily) | — | `grey` | freshness only |
| Tier 2 A/B — CTR, kICR4, PiIR, VVR6, CPC, kCPA | [Ads Launch Review](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) (weekly) | Roadmap KPIs | `ab_goal` | label integrity; grey in months 1–2 is expected |
| Shopping ROAS A/B | [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) (weekly) | Shopping 3H | `ab_goal` | label integrity; new-quarter row present |

**CATS SC / KPIs** (Tier-1 rows are in §3 above)

| Metric | Source (cadence) | Goal | Rule | Note |
|---|---|---|---|---|
| Overall Measured Revenue | Warehouse (daily) | Roadmap KPIs | `goal_rev_5m` | quarterly step rolled |
| Upper Funnel Revenue | Brand pillar feed (daily) | [Brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit) | `goal_rev_2m` | CQ/FY confirmed at roll (Emily Glauser) |
| High Quality Signal Adoption | Warehouse/Hex (daily) | none published | `grey` | stays grey; reference target from owners only |
| A/B lifts (incl. Post-Install CPA) | [Ads Launch Review](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) (weekly) | Roadmap KPIs | `ab_goal` | keep Post-Install CPA vs plain CPA vs CPI distinct |
| gROAS · Reach/Frequency/Depth · Retention | Warehouse/Hex (daily) | none | `grey` | freshness only |

**Ads Product & GTM** (actuals only; goals live on KPIs)

| Metric | Source (cadence) | Rule | Note |
|---|---|---|---|
| Shopping · Measured (GTM copies) | Warehouse (daily) | grey copy | grey by design |
| MixShift iCR | Warehouse (daily) | `yoy` | YoY direction sane |
| MixShift CPA | Warehouse (daily) | `yoy` (inverted) | falling cost is good |
| New Advertisers Activated | Warehouse (daily) | `yoy` | — |
| Marketplace Efficiency | Warehouse (daily) | `lower_bounded_goal` | floor present |
| Input Demand — % Booking to Quota | Warehouse (daily) | `booking_quota` | week-of-quarter threshold |
| Budget Utilization | — (source died 2 Jun 2026) | — | intentional blank; leave it (Dana owns replace/retire) |

**Ads Supply Drivers** (warehouse-backed)

| Metric | Source (cadence) | Goal | Rule | Note |
|---|---|---|---|---|
| DAUq (Supply copy) | Warehouse (daily) | from Step 1 sheet | forced `grey` | display duplicate |
| WAUq | Warehouse (daily) | none | `grey` | freshness only |
| Monetizable Feed | Warehouse (daily) | none | `yoy` | direction sane |
| PDP | Warehouse (daily) | none | `yoy` | direction sane |

## 4. Tier-1 methodology

Computed after normalization, before staging; the as-of date is supplied by the run, never hard-coded. The automatic path for every Tier-1 metric is **read → normalize → validate → compute → stage + audit**; the human check always = confirm the source actually landed (a populated cell is not confirmation).

- **Operational Excellence** — latest completed month-end; sum team scores (skip summary rows); MoM vs prior month, QoQ vs prior quarter-end, YoY vs Dec 2025. *Human:* new month landed (Nikhil Khanted).
- **Cloud Savings** — YTD from Efficiencies C1; **MoM/QoQ/YoY intentionally blank** (no reliable as-of date to phase against); preserve zero vs missing. *Human:* C1 moved (Nikhil Khanted).
- **Model Velocity** — QTD qualifying launches across Ranking + Retrieval + Shopping; exclude bug fixes, backtests, deprecations, zero-impact, undated; comparisons per runbook periods. *Human:* new launches on the 2026 tabs (Nikhil Khanted).
- **Experimentation Velocity** — QTD distinct Ads experiments with `unique_objects > 1000` via approved SQL (read QTD, not YTD). **`_EXP_COUNTS` fallback:** a manual QTD count keyed by `(year, quarter)` read off the Insights QTD card when SQL is down — accepted only with value/owner/timestamp/reason/evidence, flagged `REVIEW`, replaced by SQL once restored. *Human:* owner confirms the fallback (Nikhil Khanted).
- **Ads SOTA ML** — most recent dated grade from the pillar doc; MoM/QoQ/YoY blank unless comparable grades exist; **no pace** until the approved grade→rank map is configured (missing map → `REVIEW`, never a guessed pace). *Human:* readout posted; Virgilio Pigliucci approves the map.
- **S+M FTE** — latest-month S+M headcount from the sheet; comparisons on the monthly headcount series. **No revenue join / ratio** — revenue already lives in the warehouse, so it is out of scope; actual-only, status grey until a headcount goal is approved. *Human:* new FTE month landed (Nick Asaad).
- **Shopping Revenue (pacing)** — `value` = warehouse Shopping Revenue QTD; `QTD_goal` = pacing sheet col **AO** current-week row (read from the sheet, not computed); CQ/FY from Roadmap KPIs; `pace = value / QTD_goal`. **Week-over-week check:** an unchanged AO vs last week → `NEEDS VERIFICATION`. *Human:* Vinay updated the current-week AO; at roll confirm the `Q{n} DPA tracker` tab + CQ/FY (Ryan Sekulic · Vinay Sridhar).

## 5. Goals, pacing & status rules

**Goal & pacing contract:** goals are explicit config records (source link, effective period, unit, direction, owner, approval status). `current_quarter_goal` = full-quarter target; `QTD_goal` = time-phased to the as-of date; `pacing_to_QTD_goal = value / QTD_goal`. Pacing: **Scale** = runbook linear pacing across the year; **Shopping Revenue** = `external_weekly_paced` (goal taken from col AO); **S+M FTE** = actual-only. **Never compute a pace** when the goal is missing, stale, unit-incompatible, or unapproved → `REVIEW`.

**Status colour catalog** — 10 valid rules; an unknown rule name fails the tab build. Yellow is a **healthy** status, not a verification flag.

| Rule | Green / Yellow / Red | Applies to |
|---|---|---|
| `goal_binary` | ≥100% / — / <100% | Scale rows, MAA family, Ads Realized Revenue |
| `goal_rev_2m` | ≥99.5% / within $2M / else | Upper Funnel Revenue |
| `goal_rev_5m` | ≥99.5% / within $5M / else | Overall Measured Revenue |
| `impressions_pacing` | ≥98% / 96–98% / <96% | Ad Impressions, DAUq (total/US/ROW) |
| `shopping_pace` | ≥85% / 70–85% / <70% | Shopping Revenue (KPIs tab) |
| `ab_goal` | met or ≥95% last mo / 70–95% / <70% | every A/B row (grey months 1–2) |
| `yoy` | moving right way / — / else | MixShift iCR, New Advertisers, Monetizable Feed, PDP (MixShift CPA inverted) |
| `booking_quota` | week-of-quarter thresholds | Input Demand — % Booking to Quota |
| `lower_bounded_goal` | at/above floor / — / below | GTM Marketplace Efficiency |
| `grey` | always grey | gROAS, Reach/Frequency/Depth, Retention, HQ Signal, S+M FTE |

## 6. Pipeline, validation & safe failure

**Pipeline:** identify source → extract raw rows → normalize schema/units → validate → compute → reconcile to source totals/cards → write staging → write audit/provenance → report. Every adapter returns one envelope: `source_id, source_url, source_tab_or_query, pulled_at, source_as_of, raw_rows, source_status`. Hex-only sources use a separate adapter that is **explicitly blocked** — a Google service account reads shared Sheets, not Hex.

**Validation gates — PASS only when all applicable pass:**
1. Required columns and data types exist.
2. Dates parse; periods fall in the expected window.
3. Metric-period keys are unique.
4. Required keys are not missing.
5. Source freshness within the metric SLA.
6. Row-count change vs the last good run within tolerance.
7. Zero is distinguished from null/missing.
8. Derived totals reconcile to the source total/card within tolerance.
9. Manual overrides carry value + reason + owner + timestamp + evidence.
10. S+M FTE uses the latest headcount month (no cross-source month mixing).
11. Units are compatible before ratios/comparisons.
12. Weekly: DPA tracker tab exists and col AO has a non-blank current-week row (unchanged → `NEEDS VERIFICATION`).

A failure blocks only the affected metric and is visible in `Run Audit`; it never silently produces a complete-looking row.

**Respect, don't "fix" (Tier-2 special cases):** intentional blanks (Budget Utilization — source died 2 Jun 2026; Cloud MoM/QoQ/YoY; grey rows); display duplicates (Supply DAUq / Ad Impressions forced grey); manual notebook constants (`IMPRESSIONS_GOALS`, `_EXP_COUNTS`, SOTA grade → flag for a human, never edit); the A/B renamed-label trap (a renamed label silently blanks a goal — keep Post-Install CPA vs plain CPA vs CPI distinct).

**Safe failure & credentials:** reference credentials by name (`GOOGLE_SHEETS_CONNECTION`, `WAREHOUSE_CONNECTION`), never log or write them; read-only least-privilege; bounded-backoff retries; staging writes idempotent by `run_id, metric, as_of`; a failed run preserves the last known good result and is marked failed; alert after the configured repeated-failure threshold.

## 7. Upkeep cycles

**Every run — freshness gate:** read the clock (`Quarter dates based on latest date`); a metric >3 days behind is dropped → `NEEDS VERIFICATION`; a `WARN systemic freshness incident` (most sources behind) holds all pacing colours and is flagged before anyone reads the numbers.

- **Quarter roll (week 1):** confirm every goal's new-quarter column/step rolled (Roadmap KPIs, MAB Goaling, DAUq Master, Brand goals doc, Shopping 3H, pacing sheet); flag manual constants (`IMPRESSIONS_GOALS`, SOTA grade→rank map, `_EXP_COUNTS` if SQL down) for a human; owners confirm goals are **final** (a populated cell is not confirmation).
- **Monthly (second week):** Tier 1 → compute + stage Scale ×5 and S+M FTE (flag any Scale row identical to last month as a possible failed pull → checksum); Tier 2 → verify monthly/warehouse freshness + goals present; confirm the FTE month landed (Nick Asaad).
- **Weekly (3rd day):** Tier 1 → stage Shopping Revenue pacing (col AO + week-over-week check); Tier 2 → confirm the weekly A/B trackers updated ([Ads Launch Review](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925), [Shopping 3H](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934)) and that no A/B goal blanked from a renamed label (A/B grey in months 1–2 is expected).

## 8. Interface, agent prompt & acceptance

**Inputs:** `as_of_date` (default: latest completed reporting date) · `environment` (`staging`) · `write_mode` (`dry_run` | `write_staging`) · source + approved-goal config · runtime credential reference.

**Agent prompt:**

```text
Refresh the CATS Scorecard staging output for Scale, S+M FTE, and Shopping Revenue
pacing (Tier 1), and verify all other dashboard rows (Tier 2), using the Operations
Runbook as the source of truth. Read sources read-only for the configured as-of date;
normalize, then validate schema, freshness, keys, row counts, zero-vs-missing, and
reconciliation. For Tier 1 compute value, MoM, QoQ, YoY, current-quarter goal, QTD
goal, pace, and 2026 goal; for Tier 2 record a check status only. Do not guess goals,
mappings, or periods. Write only to staging, idempotently. On any failed check,
preserve the last known good result, mark the metric REVIEW or BLOCKED with a reason,
and never fill gaps. Never expose credentials or touch the dashboard/sources. Return a
run report: status, as-of, source status, each row, findings, overrides, and evidence.
```

**Acceptance criteria:**
- Every Tier-1 row has the eight metric fields or an explicit null + reason, each non-null value carrying source + as-of provenance; no stale source is shown as current.
- S+M FTE reports the latest headcount month and never mixes months across sources.
- A failed source never overwrites the last known good result; re-running identical inputs is idempotent.
- Tier-2 rows carry a check status; intentional blanks, greys, and duplicates are preserved, not "fixed."
- Two consecutive live staging cycles pass schema, freshness, uniqueness, reconciliation, and goal checks before any dashboard promotion.
