# Deliverable 4 — Improvements

Every change below is traceable to a specific evaluation finding. Baseline skills were installed
unmodified first, so `git diff` shows exactly what changed and why.

## What changed at a glance

| Skill | Before | After | Driver |
|---|---:|---:|---|
| **goal-step0-registrar** | *(did not exist)* | **282** | Live run would have invented a 3rd conflicting goal |
| goal-workflow-orchestrator | 159 | 198 | Fictional state; no batch mode; no routing |
| goal-step1-topographer | 945 | 1,093 | Mandatory sMAPE; duplicate sections; no shape measurement |
| goal-step2-architect | 402 | 535 | No top-down route; direction-blind; unjustified multipliers |
| goal-step3-pacer | 146 | 219 | Measurably wrong default shape; ignored production formula |
| goal-step4-signaler | 203 | 196 | **Every policy ID was fictional** |
| goal-step5-publisher | 57 | 237 | Wrote to storage that doesn't exist |

Plus three new supporting assets:

| Asset | Purpose |
|---|---|
| [`REFERENCE_status_policies.md`](REFERENCE_status_policies.md) | The 23 real `status_rule` values, with thresholds and 5 documented defects |
| [`governance/validate_goal_row.py`](../../governance/validate_goal_row.py) | Executable schema contract — catches bad rows before they reach the registry |
| [`eval/goal_rows_testcases.csv`](../../eval/goal_rows_testcases.csv) | 10 rows exercising each failure mode; 6 fail by design |

The instruction budget shifted from 49% on analysis / 3% on persistence to a shape that matches
where the problems actually are.

---

## 1. New: Step 0 — Registrar

**Fixes:** the live run's worst failure, plus 12 of 17 test-case failures.

The baseline had no step that asked *"does a goal already exist?"* Following it literally on Ad
Impressions would have produced a **third** number alongside the two conflicting ones already in
code — worsening the exact problem the project exists to fix.

Step 0 does five things before any analysis:

1. **Resolves `metric_id`** from the registry, never a display name — fixes the label-drift bug
   class (Post-Install CPA blank goals, retired CVR/IIR/CPI A/B names).
2. **Reads what the registry already knows** — `goal_policy`, `status_rule`, `cadence`, owner,
   `goal_source_id`. This alone removes ~6 stakeholder questions.
3. **Searches all four goal locations** (registry, Python literals, sheets, warehouse) and
   **escalates conflicts instead of resolving them**. The Ad Impressions conflict is the worked
   example, with the instruction: *"Do not derive a new goal to break a tie."*
4. **Establishes direction** (higher/lower is better) before any scenario math.
5. **Captures the approver up front** — `target_owner_id`, `approved_source_id`,
   `approval_reference`, `approved_at`. *"An unattributed goal is not a goal."*

Then routes to one of five paths (A Register / B Derive / C Dependent / D No-goal / E Blocked),
which is what makes the other four goal shapes supportable at all.

## 2. Step 5 — Publisher rewritten as registry-native

**Fixes:** G1, G4, G5, B11 — the dead end that left goals as Python literals.

- **Correct destination.** The Goal Registry (15 columns, `governance/build_seed.py`), with an
  explicit *"do not write to `goals_log` / `goal_pacing_daily` — those tables do not exist."*
- **Write order** that respects dependencies (Owner Map → Source Registry → Metric Registry →
  Goal Registry → Change Log → Queue).
- **Enumerated `target_type` and `status` values**, including `Conflicting sources` and
  `Blocked on parent goal` so escalations are recordable states rather than gaps.
- **Conflict handling**: one row per candidate with provenance, plus a queue task — never averaged.
- **Supersede, never delete**: `effective_to` + new `goal_id` + change-log entry, which finally
  supports goal retirement (B11).
- **Mandatory change log** with baseline and implied growth in `reason`, so the number is
  reconstructable without rerunning the analysis.
- **Backfill instruction** for hardcoded literals encountered along the way.
- **Read-back verification** before reporting success.

## 3. Step 4 — Signaler grounded in real code

**Fixes:** G2, plus B4/B5/B6.

All 13 fictional policy IDs replaced with the **23 real `status_rule` values**, and the claim that
bands narrow removed (nothing implements it). Added four safety checks, each tied to a real defect:

| Check | Catches |
|---|---|
| **Direction** | Cost metrics (CPC/kCPA4/CPA/CPV6) given a pacing rule that grades beating the goal as Red |
| **Near-ceiling** | 98% of a 99.90% availability goal = 97.9% graded Green (defect D4) |
| **Null safety** | `goal` has no None guard → `TypeError` when the goal is unset (defect D2) |
| **First meaningful signal** | `ab_goal` is ⚪ by design in months 1–2 — silence isn't breakage |

Also: `dauq` is now explicitly **discouraged** (defect D1 — renders permanently Green), and
thresholds must be converted into metric units, because "98% of goal" means nothing to a
stakeholder.

Most importantly, the step now **reads `status_rule` from the registry first** rather than asking
the stakeholder to choose. In most cases it needs no stakeholder input at all.

## 4. Step 3 — Pacer expanded (highest measured leverage)

**Fixes:** G12, B3, B8 — and the live run's 3.90pp finding.

- **Calendar first**: real quarter lengths (Q3 = 92, not 90), and `latest_date` = max `dt` *with
  data*, which differed from today on the live run.
- **The production formula** including `previous_quarter_exit`, which the baseline never mentioned.
- **A shape algorithm** that actually exists: normalise the prior-year cumulative share curve,
  interpolate on day-fraction to handle unequal quarter lengths, optionally blend with a stated
  weight.
- **Mandatory divergence reporting**: compute linear *and* seasonal, and escalate when they differ
  by more than the Yellow band or land in different colours. On Ad Impressions that's
  99.38% vs 103.28% — Green either way, but linear leaves only 1.38pp of headroom while the metric
  is genuinely ahead.
- **Type-specific pacing**, with an explicit prohibition on cumulative curves for Average metrics
  (DAUq) and on sum-checking Rolling-LTM metrics (Revenue/FTE).
- **A production cross-check**: predicted status must match what the dashboard shows today.

## 5. Step 2 — Architect: routes and direction

**Fixes:** the route mismatch that made Step 2 frame a Finance commitment as an analyst scenario.

- **Route gate up front** with a full **Route A** procedure: state the committed goal, compute
  implied growth, run a feasibility check, report a verdict, *don't substitute your own number*.
- **Direction gate** with an inversion table for cost metrics.
- **Multipliers demoted to conversation-starters**, with two documented failure modes:
  deceleration makes "Moderate" the aggressive option (live: YoY fell +52.5% → +17.3%, so the
  committed +12.52% is arguably the honest neutral), and multiplying a *rate* means very different
  ambition at different growth levels.
- **QoQ implausibility check** — the check that identifies the stale 112.33B goal
  (−1.43% QoQ on a metric that grew 9 of 10 quarters), which a YoY-only comparison misses entirely.
- **Multi-period coherence** with the Rolling-LTM exemption.
- **Step 5 handoff fields** captured here: `target_value` absolute, `target_type`, `baseline_value`.
- Fixed the broken "Step 1.6" cross-reference (the artifact is produced at §1.1c).

## 6. Step 1 — Topographer: conditional, calibrated, trimmed

**Fixes:** G10, G11, plus the infeasibility discovered live.

- **Route-aware preconditions** — abbreviated for Route A, skipped entirely for C/D/E.
- **sMAPE is no longer mandatory.** A gate lists seven conditions under which to skip it, and
  offers a cheaper first check: **like-for-like YoY divergence**. On Ad Impressions, US +8.97% vs
  ROW +24.69% (15.7pp) settles the segmentation question in one line. This matters practically —
  the daily pull sMAPE needs **failed to complete in 17 minutes** on this metric's connection.
- **New §1.3b: within-quarter shape**, the measurement Step 3 depends on and nothing produced.
- **§1.2 collapsed** from a duplicate of §1.1b into a single confirmation, with an explicit
  "do not re-ask."
- **Rolling-LTM added** to the metric-type menu, with the Revenue/FTE trap called out.
- **Seasonality example recalibrated** — the baseline's "20% Monday-vs-Friday" is 2.2× the measured
  8.97%, and was anchoring the agent toward over-reading weekly seasonality.
- **Growth-rate trend** now reported alongside growth rate.
- **Query-cost guidance** with the `params` CTE pattern that worked (~3 min) where the daily pull
  timed out.

## 7. Orchestrator: routing, real state, batch mode

**Fixes:** G6, G7, G8, B14.

- **Step 0 is mandatory and first.**
- **Routing table** showing which steps each route runs — Route A is flagged as the most common for
  Tier 0/1 and *not* the flow the workflow was written for.
- **State on disk** at `docs/goals/_state/[period].md` with a per-metric table, replacing
  "keep track of where you are."
- **Batch mode** for the quarterly lock: run Step 0 across all required metrics *first*, then report
  the batch picture. This reframes "15 goals to set" as **"2 goals to derive and 13 records to
  file"** — which is the honest shape of the work.
- **Burden reduction**: a table of what never to ask (it's in the registry) vs the 6 questions worth
  a stakeholder's time. Explicit rule: never ask a stakeholder about sMAPE tradeoffs or band widths.
- **Definition of done**: *"'I produced an analysis' is not done. 'It's in the registry with an
  owner' is done."*

## 8. Executable contract

Instructions decay; a validator doesn't.
[`validate_goal_row.py`](../../governance/validate_goal_row.py) enforces the schema, ID patterns,
period format, `target_type`/field agreement, decimal rates, the approval trail, supersede rules,
and — critically — that `status_rule` is one of the 23 implemented strategies.

Against the test fixture it correctly fails 6 of 10 rows:

```
ERROR row 6  target_type='Floor' requires target_lower_bound to be set
ERROR row 7  target_type='Rate' expects a decimal (0.45 for 45%); got 45.0 — a 100x error
ERROR row 8  target_value='117.7B' looks formatted; store an absolute number
ERROR row 9  status='Approved' requires approval_reference / approved_at / owner / source
ERROR row 10 target_type='No goal by design' must leave target_value empty
ERROR row 11 status_rule='pacing_standard' is not one of the 23 implemented strategies
WARN  row 5  status_rule='dauq' has a known defect (D1) — renders permanently Green
```

Row 11 is the important one: `pacing_standard` is a policy the **old Step 4 skill actively
recommended**. The validator now blocks it.

---

## Not fixed — deliberately

These need decisions from [Deliverable 3, Part 4](03_EVALUATION.md#part-4--decisions-only-yoni-can-make):

| Item | Why left open |
|---|---|
| Which impressions goal is canonical | Business decision (Finance). Skills escalate rather than choose. |
| Linear vs seasonal pacing as the standard | 3.90pp swing; a policy choice affecting all cumulative metrics. |
| Defects D1–D5 in `status_strategies.py` | Code changes to a live dashboard, out of scope for a skill update. Documented and worked around. |
| Ceiling-goal support | Requires a new `upper_bounded_goal` strategy. |
| Absolute error budgets for near-ceiling metrics | Requires a new strategy; Step 4 currently flags and refuses. |
| Whether the registry is a Sheet or a warehouse table | Architecture doc open question §8.1; determines automation ceiling. |
