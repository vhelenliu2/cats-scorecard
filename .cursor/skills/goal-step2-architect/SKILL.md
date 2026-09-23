---
name: goal-step2-architect
description: Step 2 of the Goal Creation & Pacing Workflow (Architect). Set the quarterly target value based on trends, strategic context, and scenario modeling. Output: Goal Value + Rationale.
---

# Step 2: The Architect (Context & Goal Setting)

**Purpose**: Set the target value based on trends AND strategy.

---

## Why Are We Here? (Read This to the User)

> *"Now that we understand how the metric behaves (from Topographer), we need to set a goal. We're answering:*
> 1. *What time period are we targeting?*
> 2. *What's the strategic context (launches, headwinds)?*
> 3. *What goal value balances ambition with realism?"*

---

## STOP — Check the route before deriving anything (Gate 0a)

Step 0 (Registrar) assigned this metric a **route**. This skill is written for **Route B
(derive bottom-up)**. If the route is anything else, most of what follows does not apply.

| Route | What this skill does |
|---|---|
| **A — Register (top-down committed)** | **Do §"Route A" below, then skip to Step 3.** Do NOT run the scenario framework. |
| **B — Derive (bottom-up)** | Run this skill in full. |
| **C — Dependent (derived metric)** | Skip this skill. The goal is arithmetic from parents — Step 3 §3.5. |
| **D — No goal by design** | Skip to Step 5. |
| **E — Blocked** | Skip to Step 5 (record intent). |

### Route A — validating a committed goal

For Tier 0/1 metrics the number is usually **already committed** to Finance or a plan. Your job is
to validate and record it, **not** to produce a competing number.

Do exactly this:

1. **State the committed goal and its source.**
2. **Compute implied growth** vs the prior-period actual (`baseline_value`).
3. **Run a feasibility check** — required run rate for the remainder vs recent actuals.
4. **Report the verdict** as achievable / stretch / not credible, with numbers.
5. **Do not substitute your own number.** If it isn't credible, say so and escalate to the owner.

Worked example (live, Ad Impressions Q3 2026):

> *"The committed goal is **117.70B** (US 59.8B + ROW 57.9B), from `IMPRESSIONS_GOALS` in
> `company_level_goals.py:381`. Against Q3'25 actual of 104.605B that's **+12.52% YoY**.
> Current like-for-like QTD run rate is **+16.21%**, which projects to **121.56B** — so the goal
> looks **achievable, in fact conservative by ~3.9B**.*
>
> *One caveat worth stating: YoY has decelerated every quarter for five quarters (+52.5% → +17.3%).
> A goal set off today's run rate would ignore that. **+12.52% is a defensible haircut** — but that
> should be an explicit choice, not an accident."*

Note what this example does **not** do: it doesn't tell the stakeholder their committed goal is
"between Conservative and Moderate." Framing a Finance commitment as an analyst scenario is a
category error.

**Gate 0a**: Route confirmed. Route A ⇒ validate and exit to Step 3.

---

## Direction check (Gate 0c) — before any scenario math

> **Confirm from Step 0**: *"Is higher better, or lower better, for this metric?"*

Everything below — glyphs, multipliers, the declining-segment reframe — is written for
**higher-is-better**. For a cost metric (CPC, kCPA4, CPA, CPV6 — 4 of the 9 A/B metrics) the
literal reading sets a **worse** goal the more ambitious you ask to be.

| If lower-is-better | Invert |
|---|---|
| Trend glyphs | 🟢 = YoY **below** −5%; 🔴 = YoY **above** +5% |
| Scenario multipliers | "Aggressive" = a **larger reduction**, not a larger increase |
| Sanity check | "Unprecedented" means a **record low** |
| Goal statement | Say "reduce CPA to $X", never "grow CPA by Y%" |

**Gate 0c**: Direction recorded and multipliers oriented correctly.

---

## Goal Ambition Framework (Ask Early)

### Why This Matters

Different goals serve different purposes. A "stretch goal" motivates but may demoralize if missed. A "sandbagged goal" is easy to hit but doesn't drive performance. **Ask the user what they're optimizing for.**

### Present This Menu to the User

> *"Before we crunch the numbers, what kind of goal are you looking for?"*

| Ambition Level | Plain English | When to Use | Math Shortcut |
|----------------|---------------|-------------|---------------|
| **🎯 Realistic / Safe** | "A goal we'll probably hit if things go normally" | Board targets, compensation-linked, external commitments | 70-80% of recent momentum |
| **⚖️ Moderate / Balanced** | "A goal that's achievable but requires focus" | Most quarterly goals, team targets | 100% of recent momentum |
| **🚀 Stretch / Aggressive** | "A goal we'll hit if everything goes right" | Aspirational targets, internal motivation | 120-130% of recent momentum |
| **🛑 Stabilize / Hold** | "Stop the bleeding — just don't get worse" | Declining metrics, turnaround situations | Hold current level (0% change) |
| **📈 Turnaround** | "Reverse a declining trend" | Intervention-backed metrics | Flip negative momentum to positive |

---

### Scenario Table with Momentum Context (REQUIRED)

**When presenting scenarios, ALWAYS include this table format** so the user can see how ambition maps to numbers:

| Segment | Current | Momentum | Trend | Conservative | Moderate | Aggressive |
|---------|---------|----------|-------|--------------|----------|------------|
| Segment A 🟢 | 30.0% | +20.5% | ↗️📈 | 34.3% | **36.2%** | 37.4% |
| Segment B 🟢 | 50.0% | +6.0% | ↗️ | 52.0% | **52.9%** | 53.5% |
| Segment C 🟡 | 43.6% | -5.1% | ↘️ | 41.4% (decline) | **43.6% (hold)** | 45.0% (grow) |
| Segment D 🔴 | 16.8% | -25.6% | ↘️📉 | 12.5% (decline) | **16.8% (hold)** | 18.0% (grow) |

**Column Definitions:**
-   **Current**: Latest value (from Topographer)
-   **Momentum**: YoY change (positive = growing, negative = declining)
-   **Trend**: Visual indicator (see below)
-   **Conservative/Moderate/Aggressive**: Goal options based on ambition

### Trend Indicators (Visual Hints)

Use these symbols to give the user instant context:

| Symbol | Meaning | When to Use |
|--------|---------|-------------|
| 🟢 | Growing | YoY > +5% |
| 🟡 | Flat/Slight decline | YoY between -5% and +5% |
| 🔴 | Declining | YoY < -5% |
| ↗️ | Upward trend | Last 4 weeks trending up |
| ↘️ | Downward trend | Last 4 weeks trending down |
| → | Flat trend | Last 4 weeks stable |
| 📈 | Strong momentum | YoY > +15% |
| 📉 | Strong negative momentum | YoY < -15% |
| 🌊 | Has seasonality | Topographer flagged >10% seasonal swing |

**Example with full context:**
> *"Global LCS 🟢↗️📈 — This segment is **growing strongly** (+20.5% YoY), with the last 4 weeks continuing that trend. No significant seasonality."*
>
> *"Global Unmanaged 🔴↘️📉🌊 — This segment is **declining sharply** (-25.6% YoY), accelerating down, and has **strong seasonality** (16% swing). Forecasting is harder here."*

---

### Reframing for Declining Segments (CRITICAL)

**For growing segments**: Conservative/Moderate/Aggressive = slower/same/faster growth

**For declining segments**: The math inverts! "Aggressive momentum" means *more decline*, which is NOT a goal.

**Reframe declining segments like this:**

| Scenario | Growing Segment | Declining Segment |
|----------|-----------------|-------------------|
| **Conservative** | Slower growth (0.7x momentum) | Continue declining (status quo) |
| **Moderate** | Maintain growth (1.0x momentum) | **Stabilize** (hold current level) |
| **Aggressive** | Faster growth (1.2x momentum) | **Grow** (reverse the trend) |

**Always relabel the columns for declining segments** so the user doesn't accidentally set a "goal" of declining faster.

---

### Momentum Context Block (Show Before Scenarios)

**Before presenting the scenario table, show a "momentum snapshot" for each segment:**

```
📊 MOMENTUM SNAPSHOT

Global LCS 🟢↗️📈
  • YoY: +20.5% (strong growth)
  • Last 4 weeks: ↗️ continuing upward
  • Seasonality: None detected
  • TL;DR: "Ride the wave — stretch goals are justified"

Global Unmanaged 🔴↘️📉🌊
  • YoY: -25.6% (sharp decline)
  • Last 4 weeks: ↘️ accelerating down
  • Seasonality: Strong (16% swing)
  • TL;DR: "Stabilization is the goal — turnaround requires intervention"
```

This gives the user **instant intuition** before they see the numbers.

---

### Follow-Up Questions Based on Choice

**If Realistic/Safe:**
> *"Got it — we'll build in a buffer. Are there any known risks that could blow us off course?"*

**If Moderate:**
> *"This assumes things continue as they have been. Any strategic bets that could accelerate or decelerate?"*

**If Stretch/Aggressive:**
> *"What's the upside scenario? Any launches, investments, or tailwinds that justify the stretch?"*

**If Stabilize:**
> *"What's causing the decline? Do we have interventions planned, or is this about holding ground?"*

**If Turnaround:**
> *"Reversing a trend is hard. What's the intervention? (New product, campaign, resource shift?)"*

---

### For Segmented Goals

When setting goals for multiple segments, **ask per segment** — different segments may need different ambition levels:

> *"For your 5 segments, do they all get the same ambition level, or should some be stretch and others stabilize?"*
>
> *Example:*
> - *Global LCS 🟢📈: Aggressive (riding momentum)*
> - *Global Unmanaged 🔴📉: Stabilize (managing decline)*

### Record the User's Choice

| Segment | Trend | Ambition Level | User Rationale |
|---------|-------|----------------|----------------|
| [Segment A] 🟢 | ↗️ | Stretch | "Riding momentum" |
| [Segment B] 🔴 | ↘️ | Stabilize | "No intervention planned" |

**Gate 0b**: Record ambition level before calculating scenarios.

---

## Step 2.0a: Confirm Goal Period (Do This First)

**Ask the user:**
> *"What period are we setting a goal for?"*
> - Q2'26? Q3'26? Full Year 2026?
> - Is this a **new goal** or **revising an existing goal**?

**If revising**: Ask what the current goal is and why it needs to change.

**Gate 1**: Do not proceed until goal period is confirmed.

---

## Step 2.0b: Confirm Goal Structure (Total vs Segment)

**Use the Topographer's Segmentation Advisor output to recommend a goal structure that balances accuracy and complexity.**

### Reference Topographer Artifact

**Load the Segmentation Advisor output** from Topographer (Step 1.1c — *not* 1.6; earlier versions
of this skill cited a section number that never existed):
-   **File**: `data/[metric]_segmentation_advisor.csv`
-   **Insight Card**: Check the "Segmentation Advisor" section

The output should look like:

| Option | # Series to Manage | Forecast Error (sMAPE) | Complexity |
|--------|-------------------|------------------------|------------|
| No segmentation (total) | 1 | 18.7% | Low |
| Consolidated: US vs Non-US | 2 | 18.6% | Low |
| 1-way: sales_channel_top_level | 5 | 17.2% | Low |
| 1-way: sales_channel_as_is | 12 | 16.8% | Medium |
| Full cross: channel × region | 24 | 16.5% | High |

### Generate a TL;DR Recommendation

Based on the accuracy vs complexity tradeoff, provide a clear recommendation:

**If segmentation helps significantly (>2pp improvement)**:
> *"**TL;DR: Segment by [X]** — reduces forecast error by ~[Y]pp with only [Z] series to manage (Complexity: Low)."*

**If segmentation doesn't help much (<1pp improvement)**:
> *"**TL;DR: Keep it simple (no segmentation)** — the best segmentation only improves accuracy by ~[Y]pp, not worth the added complexity."*

**If there's a "sweet spot" consolidation**:
> *"**TL;DR: Use consolidated segmentation** — [Dimension] has [N] values, but grouping to [X vs Y] gives you [benefit] with only [Z] series."*

### Present Options to User

| Option | # Goals | Accuracy | Complexity | When to Use |
|--------|---------|----------|------------|-------------|
| **A: Total Only** | 1 | Baseline | Low | Segments behave similarly; simplicity preferred |
| **B: Consolidated** | 2-3 | +1-2pp | Low | Want some segment signal without explosion |
| **C: Full Segment** | 5+ | +2-3pp | Medium | Segments diverge significantly; teams own segments |

### Recommendation Format (ELI5)

> *"Based on the Topographer analysis:*
> - *Segmenting by **sales_channel_top_level** (5 series) improves forecast accuracy by ~1.5pp vs no segmentation.*
> - *Going more granular (12 channels) only adds ~0.4pp more accuracy but doubles complexity.*
>
> *I recommend **Option B: 5 segment-level goals** — best balance of accuracy and manageability.*
>
> *Do you want to:*
> 1. *Set 5 separate goals (one per channel)?*
> 2. *Set 1 total goal + segment "guardrails"?*
> 3. *Keep it simple with 1 total goal?*"

**Gate 2**: Record the goal structure choice.

---

## Step 2.1: Strategic Context Injection (Critical)

**Before setting the number, ask:**
> *"Beyond the historical trends, is there any strategic context for [Period]?"*
>
> 1. **Product/Feature launches?** (e.g., new ad formats, API improvements)
> 2. **Go-to-market pushes?** (e.g., sales incentives, marketing campaigns)
> 3. **Headwinds?** (e.g., budget cuts, competitive pressure, deprecations)
> 4. **Segment-specific initiatives?** (e.g., "We're investing heavily in LCS")

### Capture in Structured Format

| Initiative | Segment Affected | Expected Impact | Timing |
|------------|------------------|-----------------|--------|
| Conversion API v2 | Global LCS | +5pp adoption | May 1 |
| Sales incentive | Global SMB | +10% lift | All Q2 |
| (None) | Global Unmanaged | No intervention planned | — |

**Gate 3**: Record strategic context before proceeding.

---

## Step 2.2: Scenario Framing (Anchored on Momentum)

### Step 2.2a: Calculate Baseline ("Status Quo")

**For each segment (or total), calculate:**
- **Recent Momentum**: Average YoY change over last 2-4 quarters
- **Status Quo Projection**: Apply recent momentum to current value

**Example**:
> *"Global LCS is at 31.5% with +21% YoY momentum. If that continues:*
> - *Status Quo Q2'26 = 31.5% × 1.21 = **38.1%***"

### Step 2.2b: Define Scenarios with Explicit Math

| Scenario | Formula | Description |
|----------|---------|-------------|
| **Conservative** | Recent YoY × 0.7 | Assumes 30% haircut (headwinds, execution risk) |
| **Moderate** | Recent YoY × 1.0 | Maintains recent momentum |
| **Aggressive** | Recent YoY × 1.2 | Assumes 20% acceleration (successful initiatives) |

### ⚠️ These multipliers are conversation-starters, not defaults

The 0.7 / 1.0 / 1.2 factors are arbitrary. **Present them as a starting frame and say so.** Two
failure modes to guard against:

**1. Decelerating growth makes "Moderate" the aggressive option.** If YoY is trending *down*,
"maintain recent momentum" bakes in a trend that is visibly ending.

Check first: *is the YoY sequence itself trending?* Live example — Ad Impressions YoY went
+52.5% → +49.2% → +41.3% → +32.2% → +17.3% over five quarters. Extrapolating the *level* of the
last YoY (+17.3%) ignores a ~−8pp/quarter slide in the growth rate. The committed goal's +12.52%
is arguably the honest "Moderate."

> *"YoY has fallen from +52% to +17% over five quarters — about −8pp per quarter. If that continues,
> next quarter's YoY is nearer +10-12% than +17%. So 'maintain momentum' is optimistic here, not
> neutral. I'd anchor Moderate on the **trend in the growth rate**, not its last value."*

**2. Multiplying a rate isn't the same as multiplying a level.** `YoY × 1.2` on +50% growth means
+60% — a huge level change. On +5% growth it means +6% — trivial. The same multiplier means very
different ambition at different growth rates. **Always show the resulting absolute values**, and let
the stakeholder react to those rather than to the multiplier.

**Alternative anchors** worth offering when momentum is unstable: prior-year same-quarter level ×
a chosen growth rate; trailing-4-quarter average growth; or an explicit run-rate projection with a
named haircut.

**Example for Global LCS (current: 31.5%, YoY: +21%)**:
| Scenario | YoY Applied | Q2'26 Goal |
|----------|-------------|------------|
| Conservative | +14.7% (0.7 × 21%) | 36.1% |
| Moderate | +21.0% | 38.1% |
| Aggressive | +25.2% (1.2 × 21%) | 39.5% |

### Step 2.2c: Adjust for Strategic Context

> *"You mentioned Conversion API v2 launches May 1 with expected +5pp lift in LCS. Should I add that to the Aggressive scenario?"*

---

## Step 2.3: Ratio Metric Decomposition (For Ratio Metrics Only)

**If the metric is a ratio (like Lower Funnel Adoption = LF MAA ÷ Total MAA):**

> *"Your goal is [X]% adoption. Let me validate the numerator and denominator:*
>
> | Component | Current | Projected Q2'26 | Required for Goal |
> |-----------|---------|-----------------|-------------------|
> | Total MAA | 21,478 | ~39,000 (+84% YoY) | — |
> | Lower Funnel MAA | 6,355 | ? | ~13,650 for 35% goal |
> | Implied LF MAA Growth | — | — | **+115% YoY** |
>
> *Is +115% YoY growth in Lower Funnel MAA realistic?"*

**Why this matters**: A ratio can hit goal by:
1. Numerator growing faster than expected (good)
2. Denominator growing slower than expected (may hide a problem)

---

## Step 2.4: Sanity Check

**Before finalizing, check for red flags:**

| Check | What to Look For | Action |
|-------|------------------|--------|
| **Unprecedented?** | Is this goal higher than any historical value? | Flag: "This would be a record. Intentional?" |
| **Reversal?** | Is the goal opposite to recent trend? (e.g., declining metric, but goal is +20%) | Flag: "Recent trend is -25% YoY. Goal of +10% requires a reversal. What's driving that?" |
| **Denominator risk?** | For ratios, is denominator assumption realistic? | Validate MAA growth assumption |
| **QoQ implausibility?** | Does the goal imply a *decline* on a consistently growing metric (or vice versa)? Compare against the **prior quarter's actual**, not only prior-year. | See worked example below |
| **Quarterly ↔ annual coherence?** | Do quarterly goals sum to the annual goal? | See "Multi-period coherence" below |
| **Growth-rate trend?** | Is YoY *itself* trending across recent quarters? | If so, say which direction anchoring on the last YoY biases the goal |

### Worked example — the QoQ check catches a stale goal

This is the check that identifies a goal which has silently gone out of date:

> *"The legacy impressions goal of **112.33B** for Q3'26 is **below the Q2'26 actual of 113.955B** —
> it implies a **−1.43% QoQ decline** on a metric that has grown in 9 of the last 10 quarters. That
> goal is almost certainly stale and should be retired rather than reconciled."*

A prior-year-only comparison misses this entirely: 112.33B is +7.39% YoY, which looks unremarkable.

### Multi-period coherence

If both quarterly and annual goals exist, check them — and know when **not** to:

| Metric type | Check | Real example |
|---|---|---|
| **Total / cumulative** | Quarterly goals **must sum** to the annual goal | Measured Revenue: 200+350+450+500 = 1,500 = $1.5B ✅ |
| **Total, incomplete ladder** | Report what's missing; don't infer the rest | Shopping: only Q3 ($22M) recorded against $70M FY — **unverifiable** |
| **Rolling-LTM level** | **Do NOT sum-check — it will false-positive** | Revenue/FTE: FY $3.7M exceeds every quarterly goal because it's a *level*, not a sum |
| **Average / Level** | Confirm whether the annual goal is the exit level or the mean | DAUq |

State which check you applied and why.

---

## Step 2.5: Preview Loop (Optional but Recommended)

**Before finalizing the goal, offer a quick preview:**
> *"To hit [Goal], here's what the trajectory looks like:*
> - *Current: [X]%*
> - *Goal: [Y]%*
> - *Required monthly change: +[Z]pp per month*
>
> *Does that feel achievable? If not, we can adjust before locking in."*

---

## Step 2.6: Confirm Goal

**Present the final recommendation:**

```
## Goal Summary: [Metric] - [Period]

**Segment**: [Segment name or "Total"]
**Current Value**: [X]%
**Goal Value**: [Y]%
**Scenario**: [Conservative / Moderate / Aggressive]
**Implied Change**: [+Z% YoY] or [+W pp]

**Rationale**: [One sentence: e.g., "Maintains recent +21% YoY momentum"]

**Key Assumptions**:
- [e.g., "Conversion API v2 launches May 1"]
- [e.g., "MAA growth continues at +84% YoY"]

**Risks**:
- [e.g., "If MAA growth accelerates beyond forecast, adoption % may decline even with LF MAA growth"]
```

### Handoff fields for Step 5 (capture these now)

Step 5 writes a 15-column Goal Registry row. Three of its fields are decided *here* — record them
explicitly so the Publisher doesn't have to guess:

| Field | From this step |
|---|---|
| `target_value` | The confirmed goal, **absolute and unformatted** (`117700000000`, not `117.7B`). Rates as decimals (`0.45`, not `45`). |
| `target_type` | `Absolute` / `Floor` / `Ceiling` / `Range` / `Rate` — a floor goal like `>=25x` populates `target_lower_bound`, **not** `target_value` |
| `baseline_value` | The prior-period actual the goal was set against — this is what makes implied growth auditable later |

**Gate 4**: User confirms goal value before proceeding to Pacer.

---

## Required Charts

### Chart 1: Scenario Comparison

**Show historical actuals + scenarios:**
- **Solid line**: Historical actuals (last 2 years)
- **Dotted lines**: Conservative / Moderate / Aggressive projections
- **Vertical line**: Goal period start

### Chart 2: Goal vs History (For Each Segment)

**If segment-level goals:**
- Small multiples or faceted chart showing each segment's trajectory + goal

---

## Decision Gates (When to Pause)

| Gate | When | What to Confirm |
|------|------|-----------------|
| **Gate 0b** | After Ambition Framework | Ambition level confirmed (per segment if applicable) |
| **Gate 1** | After Step 2.0a | Goal period confirmed |
| **Gate 2** | After Step 2.0b | Goal structure (total vs segment) confirmed |
| **Gate 3** | After Step 2.1 | Strategic context captured |
| **Gate 4** | After Step 2.6 | Goal value confirmed |

---

## Checklist for the Agent

- [ ] **Route confirmed** (Gate 0a) — Route A validates a committed goal and exits to Step 3; only Route B runs this skill in full
- [ ] **Direction confirmed** (Gate 0c) — multipliers and glyphs inverted for lower-is-better metrics
- [ ] **Ambition level confirmed** (Realistic / Moderate / Stretch / Stabilize / Turnaround)
- [ ] Goal period confirmed (Q2'26? Full year?)
- [ ] Goal structure decided (total vs segment-level)
- [ ] Strategic context captured (initiatives, headwinds)
- [ ] Scenarios calculated with explicit math, **presented as absolute values** not multipliers
- [ ] Growth-rate trend checked — flagged if anchoring on the last YoY biases the goal
- [ ] For ratio metrics: numerator/denominator decomposition done
- [ ] Sanity check performed — including **QoQ implausibility** vs prior-quarter actual
- [ ] Multi-period coherence checked (or correctly skipped for Rolling-LTM)
- [ ] Preview loop offered
- [ ] Goal Summary produced
- [ ] **Step 5 handoff fields recorded**: `target_value` (absolute), `target_type`, `baseline_value`
- [ ] Charts generated
- [ ] User confirmed goal before proceeding

**Next Step**: Once confirmed, proceed to **Step 3: The Pacer**.
