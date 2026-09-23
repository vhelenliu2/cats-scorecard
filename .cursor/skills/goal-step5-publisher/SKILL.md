---
name: goal-step5-publisher
description: Step 5 of the Goal Creation & Pacing Workflow (Publisher). Write the goal to the canonical Goal Registry keyed on metric_id, append a change-log entry, and produce the stakeholder deliverable. This is the only step that creates a system of record.
---

# Step 5: The Publisher (Register & Document)

**Purpose**: Make the goal *canonical, attributable, and versioned.*

**Why this step is the point of the whole workflow**: A goal that lives in a chat transcript, a
markdown file, or a Python literal is not a goal — it is a rumour. Steps 0–4 produce analysis;
this step produces the record everything else reads from.

> **Read to the user**: *"I'm going to register this in the Goal Registry so the dashboard and the
> governance checks both read the same number, and so we can answer 'who set this and when' six
> months from now."*

---

## Step 5.0: The system of record

**Canonical store**: the **Goal Registry** tab of the CATS Scorecard Data Governance workbook
(`docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc/`).
Schema owned by [`governance/build_seed.py`](../../../governance/build_seed.py) (`GOAL_HEADERS`).

**Do not** write to `goals_log` or `goal_pacing_daily` — those tables do not exist. Earlier
versions of this skill targeted them, which is why goals never landed anywhere.

### Registry write order (dependencies matter)

| Order | Tab | Why |
|---|---|---|
| 1 | Owner Map | `target_owner_id` must exist before a goal can reference it |
| 2 | Source Registry | `approved_source_id` must exist |
| 3 | Metric Registry | Metric row must exist; confirm `goal_policy` + `status_rule` |
| 4 | **Goal Registry** | The goal itself |
| 5 | Change Log | Append-only audit entry |
| 6 | Maintenance Queue | Only if the goal is blocked or conflicting |

---

## Step 5.1: Build the Goal Registry row

All 15 columns. Never write a partial row.

| Column | Source | Rules |
|---|---|---|
| `goal_id` | generate | `GOAL-` + 12 uppercase hex. **Never reuse.** A revision gets a new `goal_id`. |
| `metric_id` | Step 0.1 | **Required.** Never a display name — see B13 / the Post-Install CPA bug. |
| `planning_period` | Step 2 | Exact form: `Q3 2026`, `FY 2026`. Not "current quarter". |
| `target_type` | below | See table |
| `target_value` | Step 2 | Absolute, unrounded, unformatted. `117700000000` not `117.7B`. |
| `target_lower_bound` | Step 2 | Floor goals only |
| `target_upper_bound` | Step 2 | Ceiling / range goals only |
| `baseline_value` | Step 1 | Prior-period actual the goal was set against — makes implied growth auditable |
| `target_owner_id` | Step 0.6 | `OWN-…` |
| `approved_source_id` | Step 0.6 | `SRC-…` |
| `approval_reference` | Step 0.6 | Doc link / meeting / planning cycle. **Free text is fine; blank is not.** |
| `approved_at` | Step 0.6 | ISO date |
| `effective_from` | — | Usually period start |
| `effective_to` | — | Blank if current; set when superseded |
| `status` | below | See table |

### `target_type` values

| Value | When | Populate |
|---|---|---|
| `Absolute` | A number to hit | `target_value` |
| `Floor` | "At least X" (e.g. Marketplace Efficiency ≥25x) | `target_lower_bound` |
| `Ceiling` | "No more than X" | `target_upper_bound` |
| `Range` | Between two bounds | both bounds |
| `Rate` | Ratio / percentage | `target_value` as a **decimal** (`0.45`, not `45`) |
| `No goal by design` | Route D | nothing |
| `Owner confirmation required` | Value proposed but unapproved | `target_value` may be set |

### `status` values

| Value | Meaning |
|---|---|
| `Approved` | Owner confirmed, `approval_reference` present. **The only status the dashboard should trust.** |
| `Owner confirmation required` | Value exists, approval doesn't |
| `Conflicting sources` | Step 0.3 found disagreeing goals — **escalated, not resolved** |
| `Blocked on parent goal` | Route C with an unset parent (e.g. eCPM today) |
| `Missing actuals pipeline` | Route E — goal real, actuals absent |
| `Pending decision` | Goal source named but not wired |
| `Superseded` | Replaced; `effective_to` set |

**Rate metrics: store decimals.** The A/B goal loader parses `%` strings to fractions
(`c_performance_goals_ab_consolidated.py`). Writing `45` where `0.45` is expected is a 100×
error that renders as plausible-looking.

---

## Step 5.2: Handle the non-simple cases explicitly

### Conflicting existing goals (Step 0.3 escalation)

Write **one row per candidate**, both `status = Conflicting sources`, each with its own
`approved_source_id` and `approval_reference` naming the file and line. Do **not** average, pick,
or invent. Open a Maintenance Queue task addressed to the metric owner.

Worked example — Ad Impressions Q3 2026:

| `target_value` | `approval_reference` | `status` |
|---|---|---|
| `117700000000` | `IMPRESSIONS_GOALS['Q3 2026'], company_level_goals.py:381` | `Conflicting sources` |
| `112330000000` | `legacy_impressions_goal_full_q, cats-scorecard.draft.yaml:13265` | `Conflicting sources` |

Include the evidence that narrows it — *"112.33B implies −1.43% QoQ against Q2'26 actual of
113.955B, on a metric that grew in 9 of the last 10 quarters"* — in the queue task. Give the owner
a recommendation; let them make the call.

### Superseding a goal (retirement / revision)

Never edit or delete a goal row.

1. Set `effective_to` on the old row and `status = Superseded`.
2. Insert a new row with a **new `goal_id`**.
3. Append a Change Log entry with `old_value` → `new_value` and a reason.

This covers goal *removal* too (e.g. Retention 28D cleared): supersede with a row whose
`target_type = No goal by design`.

### Segmented goals

One row per segment, plus one for the total. Each segment gets its own `metric_id` — child metrics
are separate registry records (as MAA's LCS/MM/SMB children already are). **Check that segment
rows sum to the total row** and report if they don't.

### Multi-period goals

One row per `planning_period`. If both quarterly and FY goals exist, **verify coherence and report
the result**:

- Overall Measured Revenue: 200 + 350 + 450 + 500 = 1,500 → $1.5B FY ✅
- Shopping Revenue: only Q3 ($22M) of a four-quarter ladder is recorded against $70M FY —
  **cannot verify**. Record what's known; flag the missing quarters as `Pending decision`.
- Revenue/FTE: FY $3.7M **exceeds every quarterly goal** because it is an **LTM level, not a sum**.
  Do not run the sum check on Rolling-LTM metrics — it will false-positive.

---

## Step 5.3: Append the Change Log entry (non-negotiable)

Every registry write gets one. This is the audit trail whose absence is the core failure named in
[`METRICS_DATA_ARCHITECTURE.md`](../../../hex_edits/METRICS_DATA_ARCHITECTURE.md) §3.3.

| Field | Example |
|---|---|
| `metric_id` | `MET-83DD772E1658` |
| `goal_id` | `GOAL-…` |
| `planning_period` | `Q3 2026` |
| `field_changed` | `target_value` |
| `old_value` | `(null)` |
| `new_value` | `117700000000` |
| `changed_by` | user / agent identity |
| `changed_at` | ISO timestamp |
| `reason` | "Q3 FY26 Finance commitment; +12.52% YoY vs Q3'25 actual 104.605B" |

`reason` should state the **implied growth and the baseline**, so a reader can reconstruct the
logic without rerunning the analysis.

---

## Step 5.4: Backfill hardcoded goals as you encounter them

Any hardcoded literal you touch is a real commitment with no system of record. Register it —
attributed to its code location — even if you weren't asked to.

Known set (from the architecture doc §3.3): Upper Funnel Revenue, Shopping Revenue, Overall
Measured Revenue, HQ Signal Adoption, Revenue/FTE, all four Scale Our Foundations metrics,
`IMPRESSIONS_GOALS`, MAA `previous_quarter_exit = 18_300`, DAUq EOQ overrides.

Use `approval_reference = "backfilled from <file>:<line>"` and
`status = Owner confirmation required` — honest about provenance, and it surfaces in the owner's
queue for confirmation.

---

## Step 5.5: Stakeholder deliverable

Write `docs/goals/[metric_id]_[period]_goal.md`:

| Section | Audience | Content |
|---|---|---|
| **Decision** | Exec | Goal value, implied growth vs baseline, one-sentence rationale, owner, approval reference. ≤5 bullets. |
| **Registry record** | Governance | The 15 columns as written, plus `goal_id` |
| **How it will be graded** | Operator | `status_rule`, its exact thresholds, and the *first date the signal is meaningful* |
| **Pacing** | Operator | Shape source, QTD checkpoints, link to pacing CSV |
| **Assumptions & risks** | Analyst | Baseline, growth assumption, what would invalidate it |
| **Appendix** | Analyst | Topography, charts, SQL |

State the **grading rule in plain language**, e.g.: *"Graded by `impressions_pacing`: Green at ≥98%
of the day-weighted QTD goal, Yellow 96–98%, Red below 96%."* For `ab_goal`, say explicitly that
months 1–2 show ⚪ by design.

Artifacts as clickable links, never bare paths. Pair every CSV with a `.md` twin for human review.

---

## Step 5.6: Verify the write

Do not report success until:

1. **Read back** the Goal Registry row and diff against intent.
2. `metric_id` resolves to a live Metric Registry row.
3. `status_rule` on that row is one of the 23 real values
   ([`REFERENCE_status_policies.md`](../../../docs/goaling/REFERENCE_status_policies.md)) —
   an invalid value raises `ValueError` and crashes the dashboard.
4. `target_owner_id` and `approved_source_id` resolve.
5. Change Log entry exists.
6. If `status = Approved`, `approval_reference` and `approved_at` are both non-empty.

> **Report**: *"Registered `[goal_id]` for `[metric_id]` / `[period]`: `[value]`, status
> `[status]`, owner `[owner]`. Change Log appended. The dashboard will grade this with
> `[status_rule]`."*

---

## Checklist

- [ ] Goal Registry row complete — all 15 columns, keyed on `metric_id`
- [ ] `target_value` absolute and unformatted; rates as decimals
- [ ] `baseline_value` recorded so implied growth is auditable
- [ ] Correct `target_type` (Floor → bound, not value)
- [ ] `status` reflects reality — `Approved` only with an approval reference
- [ ] Conflicts written as multiple rows + queue task, **not** resolved unilaterally
- [ ] Superseded goals given `effective_to`, never deleted
- [ ] Segment rows sum-checked against total
- [ ] Multi-period coherence checked (skipped for Rolling-LTM)
- [ ] Change Log appended with baseline + implied growth in `reason`
- [ ] Hardcoded literals encountered along the way backfilled
- [ ] Deliverable written with the grading rule in plain language
- [ ] Write verified by read-back (5.6)

**Workflow complete.** If this was one metric in a quarterly lock, return to the orchestrator's
batch tracker.
