# Deliverable 2 — Goaling Test Set

Every case below is a **real metric with real numbers** taken from this repo, not a synthetic
example. Each case names the specific skill behaviour it probes.

Source files: [`company_level_goals.py`](../../hex_edits/modules/tabs/company_level_goals.py),
[`cats_sc_kpis.py`](../../hex_edits/modules/tabs/cats_sc_kpis.py),
[`dauq_actuals_pacing_current.py`](../../hex_edits/dauq_actuals_pacing_current.py),
[`metric_registry_seed.csv`](../../governance/seed/company_level/metric_registry_seed.csv),
[`METRICS_DATA_ARCHITECTURE.md`](../../hex_edits/METRICS_DATA_ARCHITECTURE.md).

## Tier A — Golden path (workflow should succeed cleanly)

### A1. Ads Realized Revenue (QTD), $ — `MET-AAEF7BBD83D8`
- **Goal shape:** top-down committed, warehouse-native both sides
- **Real data:** goal from `reddit-ads-prod.ads_ds_measures.daily_quota_profile`; `status_rule = goal_rev`; owner `OWN-AECE8DA3C880` (Bassem Haddad / Evie Sarkes); the only metric the architecture doc rates **"Low"** fragility
- **Tests:** Does the workflow recognise a goal that already has a system of record and *register* it rather than re-deriving a competing number? Does it preserve the `goal_rev` +$0.5M yellow buffer?
- **Correct behaviour:** skip Step 2 derivation; register the existing quota with `approved_source_id` pointing at `daily_quota_profile`; `status = Approved`.

### A2. MAA (R28D), # — `MET-B61F39994E32`
- **Goal shape:** bottom-up from history, segmented
- **Real data:** goal from *MAB Goaling 2026* sheet; `previous_quarter_exit = 18_300`; segments Global LCS / MM / SMB; `status_rule = goal` → `qtd_vs_current_q_goal`
- **Tests:** The full 5-step happy path, including segment-level ambition (Step 2 explicitly uses "Global LCS 🟢↗️📈" and "Global Unmanaged 🔴↘️📉🌊" as its worked examples) and the `previous_quarter_exit` ramp.
- **Correct behaviour:** per-segment ambition; pacing that ramps from 18,300 rather than from zero.

### A3. Overall Measured Revenue — quarterly ladder
- **Goal shape:** top-down committed, internally consistent
- **Real data:** Q1 $200M, Q2 $350M, Q3 $450M, Q4 $500M, FY $1.5B. **Sums correctly** (200+350+450+500 = 1,500).
- **Tests:** Does the workflow validate quarterly-vs-annual coherence? Does it detect that the governance tracker says **Missing** while the code holds real values (drift case §3.5 of the architecture doc)?
- **Correct behaviour:** pass the sum check; flag the tracker/code drift; register all four quarters plus FY.

## Tier B — Edge cases (where the workflow is expected to struggle)

### B1. Ad Impressions (QTD), B — `MET-83DD772E1658` ⚠️ **contradictory goals live simultaneously**
- **Real data — two different goals for the same metric and quarter in the same codebase:**

| Source | Value | Location |
|---|---|---|
| `IMPRESSIONS_GOALS['Q3 2026']` | US 59.8B + ROW 57.9B = **117.7B** | `company_level_goals.py:381` |
| `legacy_impressions_goal_full_q` | **112.33B** | `cats-scorecard.draft.yaml:13265` |

  A **5.37B (4.8%) discrepancy** between two live code paths. Governance health: `Missing`.
  Owner `OWN-06C3F25CA959` (DS: Yoni / Finance: Yona).
- **Tests:** Can the workflow *detect* that a goal already exists in more than one place and disagrees with itself? This is the fragmentation problem in its purest form.
- **Correct behaviour:** refuse to set a new goal until the conflict is escalated to the owner; record both candidates with provenance. **A workflow that silently derives a third number makes the problem worse.**
- **This is the metric chosen for the live end-to-end run.**

### B2. eCPM (QTD), $ — `MET-8D540B48605D` — derived metric, no independent goal possible
- **Real data:** eCPM = realized revenue ÷ impressions × 1000. `goal_policy = Required`, cadence Quarterly, `status_rule = impressions_pacing` (inherited from its parent — arguably wrong for a ratio). Architecture doc: *"no independent goal is possible until Impressions + Revenue goals both land."*
- **Tests:** Step 1 would run a cardinality scan and a **mandatory** sMAPE backtest on a metric with no independent series; Step 2 would derive a value that can contradict its own parents.
- **Correct behaviour:** detect the dependency, derive eCPM's goal *arithmetically* from the revenue and impressions goals, and block if either parent is unset (which it currently is — see B1).

### B3. DAUq (QTD), M — `MET-419D6C123B19` — stale, MNPI, average-type, goal in one path but not another
- **Real data:** health `Stale`; Company Level tab renders `grey` with `qtd_goal = None`; but `dauq_actuals_pacing_current.py:94` holds `{'Total': 131_400_000, 'US': 56_500_000, 'ROW': 74_900_000}` for Q2 2026. Tier 0 MNPI connection. Metric is a **QTD mean**, not a sum.
- **Tests:** (a) average-type pacing — a linear cumulative ramp is wrong; (b) a goal that exists in one code path and is absent in another; (c) MNPI data handling; (d) `implied_roq_avg` reconciliation between the SQL and Python paths, which use *different* formulas.
- **Correct behaviour:** classify as Average/Level, pace as a level not an accumulation, and surface the two conflicting pacing formulas.

### B4. Cost-direction A/B metrics — CPC, kCPA4, CPA, CPV6 ⚠️ **lower is better**
- **Real data:** 4 of the 9 A/B metrics are cost metrics (`theme = Cost Metrics`). `status_rule = ab_goal`, though production forces `grey`.
- **Tests:** The **entire Step 2 ambition framework assumes higher = better.** Its trend glyphs (🟢 YoY > +5%, 🔴 YoY < −5%), its scenario multipliers (Aggressive = momentum × 1.2), and its declining-segment reframe are all inverted for cost metrics. Following Step 2 literally sets a *worse* goal for CPA the more aggressive you ask to be.
- **Correct behaviour:** require a `direction` (higher-is-better / lower-is-better) before any scenario math, and invert the glyphs, multipliers, and band logic accordingly.

### B5. Marketplace Efficiency — `>= 25x` — bounded goal, not a target value
- **Real data:** goal is `>= 25x` (`cats_sc_kpis.py:734`). No actuals pipeline exists.
- **Tests:** The Goal Registry distinguishes `target_value` from `target_lower_bound` / `target_upper_bound`. A floor goal must populate the **bound**, not the value. Step 4 offers `floor_only` — which doesn't exist; the real strategy is `lower_bounded_goal`.
- **Correct behaviour:** write `target_lower_bound = 25`, leave `target_value` null, select `lower_bounded_goal`.

### B6. Ads Tier0 Availability — SA 99.90% / SRR 99.20% / NHR 98.0% — near-ceiling metric
- **Real data:** three sub-targets in the 98–99.9% range. No actuals pipeline.
- **Tests:** Step 4's bands are all **relative percentages of goal** (Green ≥98% of goal, Yellow 96–98%). At a 99.90% target, "98% of goal" = 97.9% availability — a catastrophic outage that the policy would grade **Green**. Relative bands are actively dangerous for near-ceiling metrics.
- **Correct behaviour:** use absolute error budget (e.g. Green ≥99.90%, Red <99.85%), not relative-to-goal bands.

### B7. Revenue / Sales + Marketing FTE — goal-only, FY is an LTM *level* not a sum
- **Real data:** actuals are the literal string `'TBD'` (no pipeline). Goals: Q1 $3.07M, Q2 $3.2M, Q3 $3.4M, **Q4 unset**, FY $3.7M.
- **Tests:** (a) Step 1 requires history that does not exist; (b) FY $3.7M **exceeds every quarterly goal** because it's an LTM level, not a sum — the Step 1 metric-type menu ("Total: how much by end of quarter?" vs "Average: typical daily value?") has no category for *LTM level*, and a sum check would false-positive here; (c) an incomplete goal set (Q4 blank) mid-year.
- **Correct behaviour:** classify as Rolling Window / LTM level; skip sum validation; record Q4 as `Pending decision` rather than silently omitting it.

### B8. Shopping Revenue — quarterly and annual goals are inconsistent
- **Real data:** CQ (Q3) $22M, FY $70M, hardcoded paced QTD $5,614,458 ("weekly paced", not linear).
- **Tests:** (a) If Q3 alone is $22M, the remaining three quarters must average $16M — plausible but **unverifiable because the quarterly ladder isn't stored anywhere**; (b) the pacing shape is bespoke and undocumented, so Step 3's linear-or-seasonal choice can't reproduce it.
- **Correct behaviour:** flag that only one quarter of a four-quarter ladder is recorded; require the full ladder or an explicit FY-only declaration; document the weekly pacing shape as a named shape source.

### B9. gROAS\*, Reach / Frequency / Depth, Retention 28D (SMB) — `No goal by design`
- **Real data:** `goal_policy = No goal by design` is a valid registry enum. All three still display as **Missing**. Retention 28D goals were *deliberately cleared*.
- **Tests:** There is no path in any of the 5 steps to record "we decided not to goal this." Consequently a legitimate decision is indistinguishable from an overdue task — the exact ambiguity `DASHBOARD_WARNING_CONTRACT.md` says must not exist.
- **Correct behaviour:** a short-circuit path that writes `goal_policy = No goal by design` with an owner, a date, and a rationale, then exits without running Steps 1–4.

### B10. Thriving Communities, # — `MET-A89FB651EAE1` — named source that isn't wired up
- **Real data:** health `Missing`. Tracker cites *"2026 Community Growth Plan"* as the goal source; the architecture doc confirms the *"sheet [is] not wired into any cell today."*
- **Tests:** A goal source that is *named but inaccessible*. The Fast Path expects a table that exists; the Full Path expects discoverable data. Neither handles "the source is a document nobody has connected."
- **Correct behaviour:** register the goal source as `Pending decision` with the named artifact in `approval_reference`, and open a maintenance-queue task instead of fabricating a goal from actuals.

### B11. Retention 28D (SMB) — goal *retirement*
- **Real data:** goals were cleared intentionally.
- **Tests:** All 5 steps only ever *create* goals. The registry has `effective_from` / `effective_to` for versioning, and the architecture doc's `goals_history` expects `old_value → new_value` transitions. Nothing supports retiring or superseding a goal.
- **Correct behaviour:** set `effective_to` on the prior row and append a change-log entry with a reason; never delete.

### B12. % top-200 brand advertisers with 3+ best practices — metric doesn't exist yet
- **Real data:** *"Metric exists in governance tracker but has no calculation cell yet."* Goal source: *June'26 CATS Roadmap Planning* sheet.
- **Tests:** A goal requested for a metric with **no actuals implementation at all**. Step 1 cannot begin.
- **Correct behaviour:** register the goal against the `metric_id` with `status = Missing actuals pipeline`; do not run Steps 1–4; queue the actuals build.

### B13. A/B goal label drift — the recurring historical bug
- **Real data:** sheet row `Price: Post-Install CPA` was never added to `metric_rename`, so Post-Install CPA A/B rendered **blank goals for months**. The same bug class recurred ≥3 times (`"CPA"` vs `"CPA A/B"` vs `"Price: CPA"` vs `"Price:CPA"`). The tracker still lists retired names *CVR A/B*, *IIR A/B*, *CPI A/B*.
- **Tests:** Does the workflow key goals on a stable `metric_id`, or on a display name that drifts? This is the failure mode `DASHBOARD_WARNING_CONTRACT.md` was written to prevent.
- **Correct behaviour:** resolve to `metric_id` via the alias map at entry; fail loudly on an unmapped label; never write a goal keyed on display name.

### B14. Batch quarterly lock — 15 metrics, 9 owners, one deadline
- **Real data:** 15 company-level Goal Registry rows, **all** empty stubs (`target_type = "Owner confirmation required"`); 9 distinct `target_owner_id` values; `MAINTENANCE_RUNBOOK.md` defines a quarterly goal-lock ritual.
- **Tests:** The workflow is single-metric and single-session. The actual job is coordinating 15 metrics across 9 owners — which is where the manual effort really goes, and where "stakeholders shouldn't have to do much" is won or lost.
- **Correct behaviour:** a batch mode that reports per-metric goal status, routes each gap to its owner, and tracks completion against the lock date.

## Coverage matrix

| Skill behaviour under test | Cases |
|---|---|
| Metric-type classification | A2, B2, B3, B7 |
| Top-down vs bottom-up goal origin | A1, A3, B1 |
| Conflicting / duplicate existing goals | **B1**, B3 |
| Derived-metric dependency | B2 |
| Direction (lower-is-better) | **B4** |
| Bounded / floor goals | B5 |
| Near-ceiling band safety | **B6** |
| Quarterly ↔ annual coherence | A3, B7, B8 |
| Pacing shape fidelity to production | A2, B3, B8 |
| `No goal by design` path | **B9** |
| Missing source / missing actuals | B10, B12 |
| Goal retirement & versioning | B11 |
| `metric_id` stability | **B13**, all |
| Approval & audit capture | all |
| Batch coordination | **B14** |

Bolded cases are the ones the current skills fail hardest — they are the priority for
[Deliverable 4](04_IMPROVEMENTS.md).
