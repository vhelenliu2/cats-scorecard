---
name: goal-step4-signaler
description: Step 4 of the Goal Creation & Pacing Workflow (Signaler). Confirm the Red/Yellow/Green policy for the metric by reading status_rule from the Metric Registry, validating it fits the metric's type and direction, and only then proposing a change. Output: confirmed status_rule + threshold explanation.
---

# Step 4: The Signaler (Confirm the Grading Rule)

**Purpose**: Establish how "on track" will be judged — using a policy that **actually exists in code**.

**Read this first**: [`REFERENCE_status_policies.md`](../../../docs/goaling/REFERENCE_status_policies.md)
is the authoritative list of the **23 valid `status_rule` values**.
`StatusStrategyFactory.get_strategy()` raises `ValueError` on anything else, so an invented policy
name doesn't degrade — it **crashes the dashboard**.

> Earlier versions of this skill offered 13 policy IDs (`pacing_standard`, `adoption`,
> `level_dauq`, `floor_only`, `trend_yoy`, …). **None of them exist.** They have been replaced with
> the real values below. Likewise, **narrowing bands are not implemented** — every real strategy
> uses static thresholds. Do not promise a tightening band.

---

## Step 4.1: Read the existing rule — don't ask the stakeholder to choose

In most cases this step requires **no stakeholder input at all**. `status_rule` is already recorded
per metric in the Metric Registry.

> **Read to the user**: *"The registry already grades this metric with `[status_rule]`, which means
> [plain-English thresholds]. I'll keep that unless it doesn't fit — I'll check that next."*

If the registry has no `status_rule`, select one using §4.2. **Only escalate to the stakeholder if
§4.3 finds the existing rule unsafe.**

---

## Step 4.2: Select a rule (only when none is recorded)

Inputs required from Step 0: **metric type** and **direction**.

### Cumulative volume metrics (Total — revenue, impressions, clicks)

| `status_rule` | Green | Yellow | Red | Use when |
|---|---|---|---|---|
| `goal` | ≥100% | ≥97% | <97% | General default |
| `goal_rev` | ≥99.5% | within $0.5M | else | Revenue, small absolute scale |
| `goal_rev_2m` | ≥99.5% | within $2M | else | Revenue ~$100–500M/q (Upper Funnel) |
| `goal_rev_5m` | ≥99.5% | within $5M | else | Revenue ~$500M+/q (Measured Revenue) |
| `goal_binary` | ≥100% | — | <100% | Pass/fail commitments |
| `impressions_pacing` | ≥98% | 96–98% | <96% | High-volume, low-variance (Impressions, eCPM) |
| `shopping_pace` | ≥85% | 70–85% | <70% | Lumpy, weekly-paced revenue |

Pick the $ buffer to match scale: a $0.5M buffer on a $450M quarterly goal is 0.1% — indistinguishable from `goal_binary`.

### Level / point-in-time metrics (Average, Snapshot)

| `status_rule` | Logic | Use when |
|---|---|---|
| `qtd_vs_current_q_goal` | Ramp from `previous_quarter_exit` toward the goal | Metric grows from a known starting level (MAA) |
| `goal` | ≥100% Green, ≥97% Yellow | Simple level targets |
| `qtd_goal_product_adoption` | ≥95% Green, ≥70% Yellow | Adoption / penetration — wide Yellow reflects slow ramps |

⚠️ **Do not use `dauq`.** Defect **D1**: it compares an absolute goal value against `>= 1`, so any
real DAUq goal renders **permanently Green**. Use `goal` or `qtd_vs_current_q_goal` until D1 is fixed.

### Bounded goals

| `status_rule` | Green | Yellow | Registry field |
|---|---|---|---|
| `lower_bounded_goal` | `qtd ≥ lower_bound` | — | `target_lower_bound` |
| `bounded_goal` | `qtd ≥ upper_bound` | `qtd ≥ lower_bound` | both |

Floor goals (Marketplace Efficiency ≥25x) → `lower_bounded_goal` with `target_type = Floor`.

⚠️ **Ceiling goals cannot be expressed today** (defect D3 — `bounded_goal` is direction-blind and
there is no `upper_bounded_goal`). For a "no more than X" metric, record the goal and flag the gap
rather than picking an inverted rule.

### Trend goals (no target value)

`qoq`, `yoy`, `both` (±3%), `both_1` (±1%), `both_point_1` (±0.1%).

These are the **only** rules that respect `indicator.value` (direction) natively — the right choice
for a metric where the goal is "keep improving" rather than "reach X".

### Time-varying

| `status_rule` | Logic |
|---|---|
| `booking_quota` | Wk 1–4 ≥55% · Wk 5–8 ≥80% · Wk 9+ ≥95% |
| `ab_goal` | ⚪ in months 1–2; month 3 ≥60% Green; last 15 days ≥95% Green / 70–95% Yellow |

`ab_goal` is the closest thing to a time-varying band that exists. If a stakeholder asks for
narrowing bands, offer `booking_quota`'s stepped thresholds as the implementable alternative.

### Deliberate no-signal

`grey` — always ⚪. Correct for metrics under methodology review or with intentionally suppressed
status (all Tier 2 A/B metrics today).

---

## Step 4.3: Safety checks — where this step earns its place

Run all four. Each has produced a real defect in this metric set.

### Check 1 — Direction. Is the metric lower-is-better?

Every pacing rule above assumes **higher is better** (`pacing = qtd / qtd_goal`, Green when high).
For CPC, kCPA4, CPA, CPV6 that is inverted — beating a cost goal means coming in *under* it, which
these rules grade **Red**.

**If lower-is-better**: use a trend rule (`yoy`/`both`) or `bounded_goal` with the target as a
ceiling. Do **not** use a pacing rule. Flag that 4 of the 9 A/B metrics are affected.

### Check 2 — Near-ceiling. Is the goal close to a natural maximum?

**Relative bands are dangerous near a ceiling.** For Ads Tier0 Availability at 99.90%,
`impressions_pacing`'s "Green at ≥98% of goal" means **97.9% availability grades Green** — a major
outage. (Defect D4.)

**If the goal is >95% of a natural maximum**: use an absolute error budget, not a relative band.
No existing strategy provides this — record the goal, select `grey`, and flag that a new strategy
is needed. Do **not** accept a relative band here.

### Check 3 — Null safety. Could the goal be missing at render time?

`goal` — the registry's most common rule — has **no None guard** (defect D2): `get_pacing()` returns
`None` when `qtd_goal` is unset, and `None >= 1.0` raises `TypeError`. `goal_binary`,
`goal_rev_2m`, `goal_rev_5m`, `shopping_pace` and `ab_goal` all guard correctly.

**If the goal may be absent or late** (Route E, `Pending decision`, or a sheet-sourced goal that
can go blank): prefer a null-safe rule, or ensure the goal is written before the rule is activated.

### Check 4 — Does the first meaningful signal date make sense?

Some rules are deliberately silent early. `ab_goal` returns ⚪ through months 1–2;
`booking_quota` uses 55% in weeks 1–4. Confirm the stakeholder knows **when** they'll first get a
real signal, so silence isn't read as breakage.

---

## Step 4.4: Explain the thresholds in the metric's own units

Percentages of goal are abstract. Convert them.

> *"`impressions_pacing` on a 117.70B Q3 goal, at day 29 of 92:*
> - *QTD goal: **37.10B***
> - *🟢 Green at ≥98% → **36.36B or more***
> - *🟡 Yellow 96–98% → **35.62B – 36.36B***
> - *🔴 Red below 96% → **under 35.62B***
>
> *Actual is 36.87B → **Green at 99.4%**. Note that's only 1.4pp above Yellow — see the pacing-shape
> caveat from Step 3."*

Where the band is uncomfortably tight, **say so**. That sentence is worth more than the chart.

---

## Step 4.5: Visualisation

One chart: expected pace (black line), green/yellow/red shaded zones from the **real static
thresholds**, goal as a horizontal marker, actuals to date overlaid.

Do not draw narrowing bands — nothing implements them.

---

## Output

```markdown
## Grading Rule

**status_rule**: `[one of the 23 real values]`
**Source**: [registry / newly selected]
**Thresholds**: Green [X] · Yellow [Y] · Red [Z]
**In metric units at [date]**: Green ≥[value] · Yellow [range] · Red <[value]
**First meaningful signal**: [date or "immediately"]
**Safety checks**: direction [pass/flag] · near-ceiling [pass/flag] · null-safety [pass/flag] · signal-date [pass/flag]
**One-sentence definition**: [plain English]
```

---

## Checklist

- [ ] `status_rule` read from the registry before asking the stakeholder anything
- [ ] Value is one of the **23 real** rules (verified against the reference)
- [ ] No narrowing bands promised
- [ ] Check 1 — direction, cost metrics not given a pacing rule
- [ ] Check 2 — near-ceiling metrics not given a relative band
- [ ] Check 3 — null safety considered where the goal may be absent
- [ ] Check 4 — first meaningful signal date stated
- [ ] `dauq` avoided (defect D1)
- [ ] Thresholds converted into metric units
- [ ] Tight bands called out explicitly

**Next step**: Step 5 — the Publisher.
