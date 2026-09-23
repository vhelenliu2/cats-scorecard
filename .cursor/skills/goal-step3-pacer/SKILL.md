---
name: goal-step3-pacer
description: Step 3 of the Goal Creation & Pacing Workflow (Pacer). Convert a period goal into the QTD expectation curve the dashboard will actually grade against. Handles metric-type-specific pacing, seasonal shape, mid-quarter re-forecast, and cumulative-ratio effort curves. Output: daily pacing CSV + MD + shape rationale.
---

# Step 3: The Pacer (Shape the Expectation Curve)

**Purpose**: Turn one number for a quarter into "where should we be *today*."

**Why this step matters more than its old length suggested**: the pacing shape, not the goal value,
usually decides what colour a stakeholder sees in month one. On the Ad Impressions Q3 2026 live run,
switching from linear to prior-year seasonal shape moved pacing from **99.38% to 103.28%** — a
**3.90pp** swing, *larger than the entire 2pp Yellow band*. A correct goal with the wrong shape
produces false alarms.

**Hard requirement**: your curve must match what the dashboard computes, or the stakeholder will see
a different status than you predicted. Start from the production formula, always.

---

## Step 3.1: Establish the calendar (do this first — it is assumed everywhere else)

Never assume 90 or 91 days.

| Quantity | How |
|---|---|
| `q_start` | First day of the period |
| `q_end` | `q_start + QuarterEnd(0)` |
| `days_in_quarter` | `(q_end − q_start).days + 1` |
| `days_elapsed` | `(min(latest_date, q_end) − q_start).days + 1` |

Actual quarter lengths: **Q1 = 90 (91 in leap years) · Q2 = 91 · Q3 = 92 · Q4 = 92.**
Q3 2026 = 92 days. Using 91 misstates the QTD goal by ~1.1% — half the Yellow band on
`impressions_pacing`.

Also record `latest_date` (max `dt` **with data**, not today). On the live run these differed:
today was 2026-07-30, data ran through 2026-07-29.

---

## Step 3.2: The production formula (your baseline — match it)

This is what the dashboard does
([`status_and_metric.py:534-544`](../../../hex_edits/modules/status_and_metric.py)):

```python
# With a known starting level (preferred when previous_quarter_exit exists):
qtd_goal = previous_quarter_exit + (
    (current_quarter_goal - previous_quarter_exit) * (days_elapsed / days_in_quarter)
)

# Without one — pure linear proration:
qtd_goal = current_quarter_goal * (days_elapsed / days_in_quarter)
```

**`previous_quarter_exit` is the piece the old skill never mentioned.** It matters for *level*
metrics that ramp from a known starting point — MAA uses `previous_quarter_exit = 18_300`. Omit it
and the early-quarter expectation is far too low.

**Decision rule:**

| Situation | Formula |
|---|---|
| Level metric with a known prior-quarter exit | Ramp from `previous_quarter_exit` |
| Cumulative metric (revenue, impressions) | Linear proration — *then* apply §3.4 shape |
| Level metric, no prior exit | Linear proration toward the goal |

---

## Step 3.3: Pace according to metric type

Getting this wrong is the most common structural error. The type comes from Step 0.

| Metric type | What the goal means | Pacing | Example |
|---|---|---|---|
| **Total (cumulative)** | Sum by period end | Cumulative curve summing to the goal | Revenue, Impressions |
| **Average / Level** | Typical value to maintain | **Expanding mean**, not a running sum | DAUq (QTD mean) |
| **Snapshot** | Value on a specific date | Trajectory to that date; interim days are informational | Active subscribers |
| **Rolling window** | Rolling metric's value at period end | Level curve on the rolling series | MAA (R28D) |
| **Rolling-LTM level** | Trailing-12-month level | **Not a sum of quarters** — do not sum-check | Revenue/FTE (FY $3.7M exceeds every quarterly goal) |
| **Ratio** | See §3.5 | Depends on denominator behaviour | eCPM, CTR, adoption |

🔴 **Never build a cumulative curve for an Average metric.** DAUq's goal is a *level* (131.4M).
A cumulative ramp is meaningless. Pace it as the expanding mean:
`qtd_actuals = mean(daily values from q_start to date)`.

---

## Step 3.4: Choose the shape — and measure the cost of getting it wrong

Linear is the *default*, not the *right answer*. For any seasonal or intra-quarter-trending metric,
compute both and show the difference.

### The algorithm

1. Pick a reference period — usually the **same quarter last year**.
2. Compute its cumulative share curve:
   `share[d] = cumsum(reference_daily)[d] / sum(reference_daily)`
   This normalises away growth and leaves pure shape.
3. Handle differing quarter lengths by **interpolating onto day-fraction** `d / days_in_quarter`,
   not by index. (Q3'25 and Q3'26 are both 92 days; Q1'26 vs Q1'25 are not.)
4. Apply: `qtd_goal[d] = current_quarter_goal * share[d]`
5. Optionally blend: `share = w·seasonal + (1−w)·linear`, `w` stated explicitly.

### Always report the divergence

> *"Q3'25 delivered **30.33%** of its quarter in the first 29 days; linear assumes **31.52%** —
> so the quarter is mildly back-loaded. On the 117.70B goal that's a QTD goal of **35.70B**
> (seasonal) vs **37.10B** (linear). Against actual 36.87B: **103.3% Green** vs **99.4% Green** —
> a **3.90pp** difference, larger than the 2pp Yellow band. Linear leaves us 1.4pp from Yellow
> while we're genuinely ahead of plan."*

**Escalate the shape choice when** the two shapes differ by more than the Yellow band's width, or
when they land in different colours. That's a stakeholder decision, not an analyst default —
and it is currently open decision #3 for this metric set.

### Event layering

Ask about known date-specific effects (holidays, Prime Day, launches, pricing changes) and layer
them explicitly. Record each as a named adjustment, never a silent tweak.

---

## Step 3.5: Ratio metrics — point-in-time vs cumulative

| Ratio type | Denominator | Pacing |
|---|---|---|
| **Point-in-time** | Recomputed each day over a rolling window | Goal = value on the **last day**. Linear % trajectory is fine. |
| **Cumulative** | Sum over the period | Denominator grows and dilutes new performance. **Needs an effort curve.** |

> *"Is the denominator a rolling snapshot (like MAA adoption) or a running sum (like CTR or eCPM)?"*

### Cumulative-ratio effort curve

```
required_marginal = (Goal × Total_denom − Locked_num) / Remaining_denom
```

Early results are locked in, so later days must outperform the target ratio. Report the required
marginal performance by month and **flag if it exceeds 1.5× current**.

**Derived ratios (Route C) don't get an independent curve.** eCPM's pacing *is* the revenue curve
divided by the impressions curve. Build it from the parents; if a parent goal is unset or
conflicting, block — eCPM today is blocked on the Ad Impressions conflict.

---

## Step 3.6: Mid-quarter re-forecast

If `days_elapsed > 0`, you are re-forecasting, not planning. Say so.

1. **Lock actuals.** Past dates are actuals, never re-paced.
2. **Compute the required run rate for the remainder:**
   `required_daily = (goal − actual_to_date) / days_remaining`
3. **Compare with recent actuals** and state the ratio plainly.
4. **Reality-check.** If `required_daily > 1.5 ×` trailing 28-day average, say the goal is unlikely
   and quantify by how much.

Worked example from the live run:
> *"29 of 92 days done. 36.87B booked against a 117.70B goal, leaving 80.83B over 63 days =
> **1.283B/day**. Trailing rate is ~1.27B/day, so this needs a **1.0×** continuation — no
> acceleration required. The goal is comfortably achievable at current run rate; projection is
> **121.56B**, about **3.9B above** goal."*

---

## Step 3.7: Sanity checks

- [ ] Curve's final value equals the goal (within rounding) — for cumulative metrics
- [ ] Curve is monotonically non-decreasing — for cumulative metrics
- [ ] No negative daily expectations
- [ ] `days_in_quarter` matches the real calendar
- [ ] Segment curves sum to the total curve
- [ ] Predicted status at `latest_date` **matches what the dashboard shows today** — if not, your
      formula and production's disagree; fix yours before publishing

That last check is the one that would have caught the old skill's divergence from production.

---

## Output

| Artifact | Format | Contents |
|---|---|---|
| Daily pacing (machine) | `data/[metric_id]_[period]_pacing.csv` | `dt, metric_id, segment, expected_value, expected_cumulative, days_elapsed, pct_of_period` |
| Daily pacing (human) | `data/[metric_id]_[period]_pacing.md` | Weekly checkpoints + month-end rows |
| Trajectory chart | `figures/…png` | Actuals + pacing curve + prior-year overlay |
| Effort curve | `.md` + `.png` | Cumulative ratio metrics only |

### Methodology block (required in the `.md`)

```markdown
- Metric type: [Total / Average / Snapshot / Rolling / Rolling-LTM / Ratio]
- Pacing formula: [previous_quarter_exit ramp / linear proration / expanding mean]
- previous_quarter_exit: [value or n/a]
- days_in_quarter: [n]  ·  days_elapsed: [n]  ·  latest_date: [date]
- Shape source: [linear / QX'YY seasonal / blended w=…]
- Linear vs seasonal divergence: [X]pp  →  [same colour / DIFFERENT COLOUR]
- Event adjustments: [list or none]
- Re-forecast: [yes/no]; required run rate [X]/day vs trailing [Y]/day
- Cross-check vs production dashboard status: [match / mismatch + explanation]
```

---

## Checklist

- [ ] Calendar established from the real quarter length (3.1)
- [ ] Production formula used as the baseline, `previous_quarter_exit` considered (3.2)
- [ ] Pacing matches metric **type** — no cumulative curve on an Average metric (3.3)
- [ ] Shape chosen deliberately; linear-vs-seasonal divergence computed and reported (3.4)
- [ ] Divergence escalated if it exceeds the Yellow band or changes colour (3.4)
- [ ] Ratio type resolved; effort curve built for cumulative ratios (3.5)
- [ ] Derived metrics paced from parents, blocked if a parent is unset (3.5)
- [ ] Re-forecast mode: actuals locked, required run rate stated (3.6)
- [ ] All sanity checks pass, including the production cross-check (3.7)
- [ ] CSV + MD + charts saved; methodology block complete

**Next step**: Step 4 — the Signaler.
