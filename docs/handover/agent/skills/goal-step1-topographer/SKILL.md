---
name: goal-step1-topographer
description: Step 1 of the Goal Creation & Pacing Workflow (Topographer). Analyze metric behavior, data health, and seasonality. Output: Insight Card + Cleaned Data + Segmentation Recommendation.
---

# Step 1: The Topographer (Analyze, Clean & Recommend)

**Purpose**: Understand how this metric behaves before setting a goal number.

---

## Preconditions (read before starting)

**Run [Step 0 — Registrar](../goal-step0-registrar/SKILL.md) first.** It supplies the `metric_id`,
metric type, direction, and — critically — the **route**. This skill is only fully required for
**Route B (derive bottom-up)**.

| Route | What this skill does |
|---|---|
| **A — Register (top-down committed)** | **Abbreviated run only**: data health, quarterly context table, like-for-like QTD, within-quarter shape (§1.3b). Skip cardinality scan, skip sMAPE — you are validating a number, not deriving one. |
| **B — Derive (bottom-up)** | Full run. |
| **C — Dependent (derived metric)** | **Skip this skill entirely.** A derived metric has no independent series to analyse. |
| **D / E — No goal by design / Blocked** | Skip. Go to Step 5 to record. |

**Establish the calendar before any analysis** (everything downstream depends on it):

| Quantity | Note |
|---|---|
| `latest_date` | Max `dt` **with data** — not today. These differ in practice. |
| `days_in_quarter` | **Q1 = 90/91 · Q2 = 91 · Q3 = 92 · Q4 = 92.** Never assume 90. |
| `days_elapsed` | `(min(latest_date, q_end) − q_start).days + 1` |

### Query cost warning

Some source tables are large and the connections are slot-constrained. A 3.5-year *daily* pull from
`direct_ads_revenue_by_sales_channel` on the Ads DS Nonprod connection **failed to complete in
17 minutes** during testing.

**Push aggregation into SQL.** Return quarterly/weekly aggregates, not daily rows, using a
`params` CTE for the elapsed-day window:

```sql
WITH params AS (
  SELECT MAX(dt) AS max_dt,
         DATE_DIFF(MAX(dt), DATE_TRUNC(MAX(dt), QUARTER), DAY) + 1 AS elapsed_days
  FROM `<table>` WHERE <filters>
)
-- then CROSS JOIN params and filter
-- WHERE DATE_DIFF(dt, quarter_start, DAY) < elapsed_days   -- like-for-like QTD
```

One aggregating statement returned the full topography in ~3 minutes where the daily pull timed out.

---

## Why Are We Here? (Read This to the User)

> *"Before we set a goal, we need to understand how this metric behaves. We're answering three questions:*
> 1. *Is the data clean and trustworthy?*
> 2. *Is the metric growing, flat, or shrinking?*
> 3. *Are there patterns (weekly spikes, seasonal dips) we need to account for?"*
>
> *Once we understand the metric, I'll give you a recommendation on how to slice it (or keep it as one number).*

---

## Agent Transparency Rules (MANDATORY — Read Before Any Analysis)

### 1. No Hidden Assumptions

**Before making ANY selection or recommendation, you MUST:**

1. **Cite the source** of your reasoning. If you're using:
   - Examples from this skill file → Say: *"The skill's examples suggest X, but let me show you all options first."*
   - Patterns from other documents in context → Say: *"I found references to X in [document name], but this may not apply to your use case."*
   - General industry patterns → Say: *"X is common in ads data, but I don't know if that's how your team operates."*

2. **Never pre-filter options** without showing the full list first. Even if the skill has examples, those are illustrative — not prescriptive for every metric.

### 2. Show Your Work

When presenting any analysis, include a **"Context Sources"** section:

```
### Context Sources (Transparency)
- Table schema: Pulled from INFORMATION_SCHEMA
- Segment options: [How I selected them — full scan vs pre-filtered]
- Assumptions made: [List any assumptions and their source]
- Skill examples used: [Yes/No — if yes, which ones influenced this output]
```

### 3. Anti-Pattern: Silent Pre-Selection

❌ **WRONG**: Running sMAPE on 3-4 dimensions you picked without showing all options first.

✅ **RIGHT**: 
1. Run full cardinality scan (ALL columns)
2. Present complete menu to user
3. Ask user which dimensions to test
4. Only then run sMAPE on user's selections

### 4. When in Doubt, Ask

If you have context from:
- Prior conversations
- Other documents found in search
- Skill file examples
- Common industry patterns

**Tell the user**: *"I have some context that might be relevant: [X]. Should I use this, or would you prefer to start fresh?"*

### Why This Matters

Users trust AI outputs. If the agent silently injects assumptions from skill examples or prior context, users may:
- Accept recommendations that don't fit their use case
- Miss better segmentation options
- Not understand why certain choices were made

Transparency builds trust. Always show the full picture first.

---

## Universal Output Rules (MANDATORY — Apply to ALL Outputs)

### 1. All Artifacts MUST Be Clickable Links

**Every file path, chart, or artifact you reference MUST be a clickable hyperlink.** Users should never have to copy-paste a path.

#### Format for Artifacts

```markdown
| Artifact | Path |
|----------|------|
| Time series chart | [click_obj_timeseries.png](figures/click_obj_timeseries.png) |
| Daily data | [click_obj_daily_total.csv](data/click_obj_daily_total.csv) |
| Quarterly summary | [click_obj_quarterly.csv](data/click_obj_quarterly.csv) |
```

#### Anti-Patterns (NEVER DO THIS)

❌ **WRONG** — Plain text paths (not clickable):
```markdown
Saved: figures/click_obj_timeseries.png
Data: data/click_obj_daily_total.csv
```

❌ **WRONG** — Backtick paths (not clickable):
```markdown
Chart saved to `figures/click_obj_timeseries.png`
```

✅ **RIGHT** — Clickable markdown links:
```markdown
Chart saved to [click_obj_timeseries.png](figures/click_obj_timeseries.png)
```

#### Apply This To:
- **All charts** saved to `figures/`
- **All data files** saved to `data/`
- **All SQL files** saved to `sql/`
- **All deliverable docs** saved to `docs/`
- **Any artifact mentioned in tables, summaries, or prose**

#### Why This Matters
Users are in an IDE. Clicking a link opens the file instantly. Copy-pasting paths is friction that kills the workflow. **Every artifact = one click away.**

### 2. Charts Must Be Viewable

When showing charts in your response:
- Use markdown image syntax: `![Description](figures/filename.png)`
- This embeds the chart directly in the response
- User sees the visualization immediately without clicking

---

## Fast Path: Skip Discovery When User Knows What They Want

**Check this FIRST before starting the full workflow.**

Many users already know their metric, table, and how they want to segment. Don't make them sit through discovery steps they don't need.

### Detect Fast Path Signals

If the user's request includes **ALL THREE** of the following, use Fast Path:

| Signal | Example |
|--------|---------|
| **Table name** | "using `direct_ads_revenue_by_sales_channel`" |
| **Metric** | "click objective revenue" or "delivered_revenue where objective_type = 'CLICKS'" |
| **Segmentation** | "by sales channel" or "split by sales_channel_top_level" |

**Examples that qualify for Fast Path:**
- *"Set Q2 goal for click objective revenue from direct_ads_revenue_by_sales_channel, by sales channel"*
- *"I need Q2 and Q3 goals for impressions by sales_channel_top_level using the ads_engagement_cube"*
- *"Goal for SMB revenue from the revenue table, segmented by region (US vs ROW)"*

**Examples that need Full Path:**
- *"Help me set a goal for our ads business"* (no table, no metric specified)
- *"What should our Q2 target be?"* (needs discovery)
- *"I want to set a revenue goal but not sure how to slice it"* (needs segment discovery)

### Fast Path Flow (2-3 minutes)

When Fast Path is detected:

```
1. CONFIRM (30 sec)
   - Echo back: metric, table, filter, segmentation
   - Ask: "Is this correct? Any filters I should apply?"

2. PULL DATA (60 sec)
   - Query historical data (last 2-3 years)
   - Include the user's specified segmentation
   - No cardinality scan needed

3. ANALYZE (60 sec)
   - Quarterly context table (last 6-8 quarters with YoY/QoQ)
   - Segment breakdown
   - Seasonality summary
   - Generate charts (with partial period handling)

4. PRESENT INSIGHT CARD
   - Same format as full workflow
   - Ready for Step 2 (target setting)
```

### What Gets Skipped in Fast Path

| Step | Full Path | Fast Path |
|------|-----------|-----------|
| Step 1.0a: Metric type identification | ✅ Ask user | ⏭️ Infer from request |
| Step 1.0b: Data health check | ✅ Ask user | ⚡ Quick null/gap check, auto-flag issues |
| Step 1.1: Full cardinality scan | ✅ All 45+ columns | ⏭️ Skip entirely |
| Step 1.1b: Business context questions | ✅ Ask about goals/drivers | ⏭️ Skip — user already specified |
| Step 1.1c: sMAPE validation | ✅ Run backtest | ⏭️ Skip — user chose their segments |
| Step 1.2: Segment selection menu | ✅ Present options | ⏭️ Skip — user specified |
| Step 1.3: Trend/seasonality | ✅ Full analysis | ✅ Full analysis |
| Step 1.4: Quarterly context | ✅ Full analysis | ✅ Full analysis |
| Step 1.5: Charts | ✅ Generate | ✅ Generate |

### Fast Path Confirmation Template

When Fast Path is detected, confirm with the user:

> *"Got it — you want to set **[Q2/Q3] goals** for **[metric]**, segmented by **[dimension]**.*
>
> *I'll pull the data from `[table]` with filter `[filter]` and show you:*
> - *Last 6-8 quarters with YoY/QoQ*
> - *Breakdown by [segment]*
> - *Seasonality patterns*
>
> *Does that look right? (If you want to explore other segmentation options, just say so and I'll run the full discovery.)"*

### When to Fall Back to Full Path

Even if Fast Path signals are present, fall back to Full Path if:
- User says "I'm not sure" or "help me explore"
- The specified table doesn't exist or has issues
- The specified segmentation column doesn't exist
- User asks "what other options do I have?"

**The goal is speed for users who know what they want, not to force everyone into a shortcut.**

---

## Step 1.0a: Identify Metric Type (Critical — Do This First)

**Why This Matters**: Different metric types behave differently. A "total" (like Revenue) accumulates over time. An "average" (like DAU) is a level you maintain. A "ratio" (like CTR) depends on two numbers. The type affects how we set goals, how we pace, and how we interpret "on track."

### Ask the User

> *"What type of metric is this? Here are the common types — pick the one that fits, or just tell me the metric name and I'll help you figure it out."*

---

### Metric Type Menu (Present to User)

#### Group A: Volume Metrics (Things You Add Up)

| Type | Plain English | Examples | Goal Sounds Like... |
|------|---------------|----------|---------------------|
| **Total (Cumulative)** | "How much total by the end of the quarter?" | Revenue, Impressions, Signups, Clicks | "We want $10M by end of Q2" |
| **Average / Level** | "What's the typical daily value?" | DAU, Daily Active Advertisers, Avg Spend | "We want to average 5M DAU this quarter" |
| **Snapshot (Point-in-Time)** | "What's the count as of a specific date?" | Active Subscribers (as of today), Credit Balance | "We want 100K active subs by June 30" |
| **Rolling Window** | "What's the total/average over the last X days?" | MAU (Monthly Active Users), WAU, Revenue L28D | "We want MAU to hit 50M by end of Q2" |
| **Rolling-LTM Level** | "What's the trailing-twelve-month level?" | Revenue / Sales+Marketing FTE | "We want LTM revenue per FTE to reach $3.7M" |

⚠️ **Rolling-LTM is the type people misclassify most.** Its annual goal is a **level, not a sum of
quarters** — Revenue/FTE has quarterly goals of $3.07M/$3.2M/$3.4M and an FY goal of **$3.7M**,
which is higher than all of them. If you classify it as Total, every coherence check will
false-positive. Never sum-check a Rolling-LTM metric.

#### Group B: Derived Metrics (Calculated from Other Numbers)

| Type | Plain English | Examples | Goal Sounds Like... |
|------|---------------|----------|---------------------|
| **Ratio / Percentage** | "What's the rate?" (Numerator ÷ Denominator) | CTR, eCPM, Budget Utilization %, Conversion Rate | "We want CTR to reach 1.5%" |
| **Progress to Ceiling** | "How close are we to 100%?" | % of Target List Covered, Adoption % | "We want 80% adoption by Q2" |

---

### If the User Just Says the Metric Name

If the user says *"It's Impressions"* or *"It's CTR"*, help them by narrowing:

**Example 1: "The metric is Impressions"**
> *"Got it — Impressions is typically a **Total (Cumulative)** metric. You add up daily impressions to get a quarterly total. Does that sound right?"*

**Example 2: "The metric is DAU"**
> *"DAU is usually an **Average / Level** metric. You're tracking the daily number and want to maintain or grow that level. Does that sound right?"*

**Example 3: "The metric is CTR"**
> *"CTR is a **Ratio** metric — it's Clicks ÷ Impressions. I'll need to understand both the numerator and denominator. What are they?"*

**Example 4: "The metric is MAU"**
> *"MAU is a **Rolling Window** metric — it's the count of distinct users over the last 28 (or 30) days. It's not a simple sum, so we pace it differently. Confirmed?"*

---

### Record the Metric Type

Once confirmed, record:
-   **Metric Name**: [e.g., "Impressions"]
-   **Metric Type**: [e.g., "Total (Cumulative)"]
-   **If Ratio**: Numerator = [X], Denominator = [Y]

**Gate 1**: Do not proceed until metric type is confirmed.

---

## Step 1.0b: Data Health Check

**Purpose**: Make sure the data is clean before we analyze it.

### What to Check

| Issue | How to Detect | What to Ask User |
|-------|---------------|------------------|
| **Missing Days** | Gaps in the date sequence | "I see data is missing for [dates]. Is this expected (e.g., no data on weekends) or a problem?" |
| **Unexpected Zeros** | Zero values on days that should have data | "I see zeros on [dates]. Is this real (e.g., holiday shutdown) or bad data?" |
| **Extreme Spikes** | Single day >3x the typical value | "I see a spike on [date] that's 5x normal. Is this a real event (e.g., Prime Day) or bad data?" |
| **Extreme Drops** | Single day <0.3x the typical value | "I see a drop on [date] that's 70% below normal. Is this real or an outage?" |

### How to Handle Issues

> *"I found some potential data quality issues:*
> - *[Date]: Value is 0 (expected median: 1.2M)*
> - *[Date]: Value is 15M (expected median: 1.2M)*
>
> *How should I handle these?*
> 1. **Keep them** — they're real events.
> 2. **Exclude them** — remove from analysis.
> 3. **Interpolate** — replace with estimated values."

**Gate 2**: Get user confirmation on how to handle issues before proceeding.

---

## Step 1.1: Segment Discovery (What Can We Slice By?)

**Purpose**: Show the user what dimensions exist in the data so they can decide how to segment.

### What to Do

1.  **Scan all columns** in the data.
2.  **Filter to useful candidates**: Categorical columns with 2–50 distinct values.
3.  **Exclude noise**: IDs, timestamps, ETL fields, high-cardinality (>100 values).

### Query Optimization & Data Source Guidance

#### Time Window for Cardinality Scans

| Scan Type | Recommended Window | Why |
|-----------|-------------------|-----|
| **Cardinality scan** | **30 days** (recent data) | Fast; reflects current/active values; sufficient for segment discovery |
| **sMAPE backtest** | **2-3 years** | Needs history for seasonality detection |
| **Trend/YoY analysis** | **2-3 years** | Needs prior year for YoY comparisons |

**Use judgment**: If queries are slow or the dataset is very large, reduce the cardinality scan window to 7-14 days. The goal is to understand what dimensions exist — not to scan every historical record.

#### Large Dataset Handling

If the dataset is very large (queries timing out, >1 minute for simple aggregations):

1. **Ask about the data source**:
   > *"This dataset is quite large and queries are slow. A few questions:*
   > - *Is this the right source table, or is there a summarized/aggregated version?*
   > - *Is there a daily/weekly rollup table that might be faster?*
   > - *Should we filter to a subset (e.g., specific sales channels, regions)?"*

2. **Offer alternatives**:
   - Use a smaller time window for exploration
   - Sample the data for cardinality scans
   - Switch to an aggregated table if available

3. **Be transparent about tradeoffs**:
   > *"I'm using 14 days of data for the cardinality scan to keep queries fast. This captures current segment values but might miss rare/seasonal values."*

### Required Artifact: Full Cardinality List

**You MUST save the full cardinality scan to a file** so the user can reference it later:
-   **Location**: `data/[metric_name]_cardinality.csv` or `docs/[metric_name]_full_cardinality.md`
-   **Contents**: ALL columns with distinct counts and sample values (not just the filtered top 20)
-   **Why**: Users may want to explore other dimensions later; the artifact preserves the full menu

**Example artifact** (`data/lower_funnel_cardinality.csv`):
```
column_name,distinct_count,sample_values,category
sales_channel_top_level,5,"LCS, MM, SMB...",segment_candidate
region,2,"US, ROW",segment_candidate
ads_account_id,15000,"a2_xxx...",high_cardinality
dt,800,"2023-01-01...",date_field
```

### Present to User (Example Format)

> *"Here are the dimensions you can segment by:*
>
> | Column | Distinct Values | Samples |
> |--------|-----------------|---------|
> | region | 2 | US, ROW |
> | sales_channel | 5 | Direct, Partner, SMB, Enterprise, Other |
> | placement_type | 4 | Feed, Comments, Search, Profile |
> | platform | 3 | iOS, Android, Web |
>
> *I've saved the full cardinality list to `data/[metric]_cardinality.csv` — this includes all columns if you want to explore other dimensions later.*
>
> *I've hidden high-cardinality columns (like user_id, campaign_id). Let me know if you need to see them."*

### Proactively Suggest Consolidated Options

For high-cardinality columns (>50 values), **always suggest consolidation patterns**. Don't just list them as "excluded" — show how they could be useful with grouping.

#### Common Consolidation Patterns (Suggest These)

| High-Cardinality Column | Consolidation Options | Why It Helps |
|-------------------------|----------------------|--------------|
| **location_country** (100+ values) | → **US vs ROW** (2 groups) | Most common; maps to team structure |
| | → **US / EMEA / APAC / LATAM** (4 groups) | Regional teams |
| | → **Top 5 countries + Other** (6 groups) | Focus on biggest markets |
| **placement_type** (many feed types) | → **Feed vs Non-Feed** (2 groups) | Group HOME_FEED, COMMUNITY_FEED, MIXED_FEED, etc. together |
| | → **Feed / Comments / Other** (3 groups) | Separate comments engagement |
| **sales_channel_as_is** (12 values) | → **sales_channel_top_level** (5 values) | Use existing rollup column if available |
| | → **LCS / MM / SMB / Other** (4 groups) | Custom grouping |
| **sfdc_industry** (80+ values) | → **Top 10 industries + Other** | Focus on biggest verticals |
| | → **Custom vertical groups** | e.g., Tech / Retail / Finance / Other |
| **agency_holding_co_name** (100+ values) | → **Top 5 holdcos + Independent + Other** | Focus on biggest agency relationships |

#### How to Present Consolidated Options

> *"I also noticed some high-cardinality columns that could be useful with grouping:*
>
> | Column | Raw Values | Suggested Consolidation |
> |--------|------------|------------------------|
> | location_country | 228 | **US vs ROW** (2 groups) — common for team alignment |
> | placement_type | 18 | **Feed types vs Other** — group the various feed placements |
> | sfdc_industry | 81 | **Top 10 + Other** — focus on biggest verticals |
>
> *Would any of these consolidated options be useful to test?"*

#### Rules for Consolidation

1. **Always offer at least one consolidation** for columns with >50 values
2. **Check if a rollup column already exists** (e.g., `sales_channel_top_level_as_is` is a rollup of `sales_channel_as_is`)
3. **Ask the user** if they have standard groupings they already use (e.g., "Do you have a standard regional split?")
4. **US vs ROW is almost always useful** — suggest it for any country/geo column

---

## Step 1.1b: Segment Selection (Business-First Approach)

**Purpose**: Help the user pick segments that align with how they **think about** and **manage** this metric. Technical accuracy analysis comes AFTER the user identifies what matters to them.

### Step 1: Understand the Business Context (Ask First)

**Before showing any technical analysis, understand what drives this goal.**

> *"Before we pick segments, I want to understand how you think about this metric:*
>
> 1. *What's driving this goal? Is it a GTM initiative, product launch, operational efficiency, or general growth?*
> 2. *How will success be measured? By team, by region, by product, by customer type?*
> 3. *Who owns this metric? Is it split across teams (e.g., LCS vs SMB)?*
> 4. *Are there specific segments you already report on or care about?"*

### Step 2: Match Segments to Business Context

**Based on the user's answers, suggest relevant dimensions.**

| If the goal is about... | Relevant segments might be... | Why |
|-------------------------|------------------------------|-----|
| **GTM / Sales motion** | sales_channel, sales_channel_top_level | Different channels have different strategies |
| **Product adoption** (e.g., new feature rollout) | sales_channel (to measure where adoption is happening), product_type | Track which teams/customers are adopting |
| **Regional expansion** | Region (US vs ROW), location_country | Different markets grow differently |
| **Customer type** | ads_account_type (Managed vs Self-Serve), sfdc_account_type | Enterprise vs SMB behave differently |
| **Platform/Placement** | placement_type_agg, placement_platform | Track where ads are being served |
| **Vertical focus** | business_industry, lcs_sector_flag_sfdc | Industry-specific performance |

#### Example: Feature Adoption Goal

> *"You mentioned this goal is tied to automated targeting adoption. In that case, **sales_channel** is important because:*
> - *LCS and MM teams have different adoption motions (high-touch vs scaled)*
> - *SMB/Unmanaged may adopt faster (self-serve) or slower (less support)*
> - *You'll want to see which channels are driving adoption vs lagging*
>
> *Does that framing make sense? Should we segment by sales_channel_top_level (5 segments) or the more granular sales_channel_as_is (12 segments)?"*

### Step 3: User Picks Segments Based on Business Logic

**Let the user decide what matters to them. Allow multi-select for exploration.**

> *"Based on our discussion, which segments do you want to explore?*
> - *Option A: Total-level goal (simplest)*
> - *Option B: Segment by [X] — [N] goals*
> - *Option C: Segment by [Y] — [M] goals*
> - *Option D: Cross-segment [X × Y] — [N×M] goals*
>
> *You can select **more than one option** to explore. I'll run trend/seasonality analysis on each so you can compare before deciding.*
>
> *Remember: More segments = more granular accountability, but also more complexity."*

#### Multi-Select Exploration Flow

If the user selects multiple options (e.g., "A and C" or "let me see both"):

1. **Run analysis on ALL selected options** in parallel
2. **Present comparison table** showing trend/seasonality for each
3. **Let user pick final segmentation** after seeing the data

> *"You selected [A, B, C]. Let me analyze each:*
>
> | Option | # Goals | Recent YoY | Seasonality Pattern | Forecast Error |
> |--------|---------|------------|---------------------|----------------|
> | A: Total | 1 | +25% | Strong Q4 peak | 18% |
> | B: By channel | 5 | Varies (12-40%) | Similar pattern | 16% |
> | C: By geo | 2 | US +30%, ROW +15% | US stronger Q4 | 17% |
>
> *Which would you like to proceed with for goal-setting?"*

**Record the user's final choice before proceeding.**

---

## Step 1.1c: Validate with Forecast Accuracy (Conditional — check the gate first)

**Purpose**: AFTER the user picks segments based on business logic, validate whether those segments actually behave differently. This helps confirm the choice makes sense from a data perspective.

### Gate: skip sMAPE unless it will change a decision

Earlier versions of this skill marked the sMAPE backtest **MANDATORY**. That was wrong. It is an
expensive second pass over history that is meaningless or infeasible for most metrics in this set.

**Skip sMAPE when any of these is true:**

| Condition | Why | Example |
|---|---|---|
| Route is A, C, D, or E | You're not choosing segmentation from data | Ad Impressions (committed), eCPM (derived) |
| Metric is derived from other metrics | No independent series exists | eCPM = revenue ÷ impressions |
| <1 year of history | Cannot backtest a seasonal-naive forecast | New metrics |
| No actuals pipeline | Nothing to backtest | Scale Our Foundations, Revenue/FTE |
| Segmentation is dictated by org structure | Accuracy is irrelevant — teams own the segments | US/ROW where regional teams are accountable |
| **The YoY split already answers the question** | Cheaper and clearer — see below | Ad Impressions US/ROW |
| Queries are slot-constrained | The backtest may simply not finish | `direct_ads_revenue_by_sales_channel` |

### Cheaper first check: like-for-like YoY divergence

Before reaching for sMAPE, compute each candidate segment's **like-for-like QTD YoY growth**. If
segments diverge materially, segmentation is justified — no backtest needed.

Live example (Ad Impressions Q3 2026):

| Segment | LFL QTD YoY |
|---|---|
| US | **+8.97%** |
| ROW | **+24.69%** |
| **Divergence** | **15.7pp** |

> *"US is growing at +9% and ROW at +25% — a 15.7pp gap. Segmenting is clearly warranted; a blended
> +16% goal would be too easy for ROW and too hard for the US. I don't need a backtest to establish
> that."*

**Rule of thumb**: divergence >5pp ⇒ segment. <2pp ⇒ probably don't. Between the two, or when the
stakeholder wants more rigour, *then* run sMAPE.

**When you do skip it, say so and why** — don't silently omit a step the stakeholder may expect.

### Introduce the Concept (Plain English)

> *"Now that you've picked [segments], let me check whether these segments actually behave differently historically. If they do, segmenting makes sense — you'll get more accurate tracking. If they all move together, you might be adding complexity without benefit."*
>
> *"I'll run a quick backtest: I'll pretend it's 3 months ago and try to predict what happened. If the segments I'm tracking help me predict better, that's a good sign."*

### What We're Measuring (Explain Simply)

**Forecast accuracy** = "How well can we predict this metric?"

- **Lower error** = segments behave predictably, easier to set and track goals
- **Higher error** = more volatility, harder to know if you're on/off track

We measure this using a metric called **sMAPE** (Symmetric Mean Absolute Percentage Error):
- It's just a fancy way of saying "on average, how far off were our predictions?"
- **10% error** = predictions were typically 10% off (pretty good)
- **30% error** = predictions were typically 30% off (harder to track)

### Method (Technical Details — For Reference)

For each candidate segmentation:
1.  **Hold out** the last N periods (e.g., last quarter)
2.  **Train** a simple forecast (repeat the same period from last year)
3.  **Measure** forecast error (sMAPE)
4.  **Compare** accuracy vs complexity (# of series to manage)

### Handling Limited Data History

**Before running analysis, check available history and be transparent about limitations.**

| Data Available | What You CAN Do | What You CANNOT Do |
|----------------|-----------------|-------------------|
| **< 6 months** | Basic trend direction, cardinality scan | sMAPE backtest, YoY comparison, seasonality detection |
| **6-12 months** | QoQ comparison, weekly patterns | Full YoY comparison, annual seasonality |
| **1-2 years** | YoY comparison, basic seasonality | Multi-year trend analysis, confident sMAPE |
| **2-3+ years** | Full analysis | — |

**If data history is limited, tell the user:**

> *"This dataset has [X] months of history (starting [date]). Here's what I can and cannot do:*
> - ✅ **Can do**: [list what's possible]
> - ❌ **Cannot do**: [list what's not possible]
> - ⚠️ **Limited confidence**: [list what's possible but unreliable]
>
> *Should I proceed with the available data, or is there a longer-history source?"*

**Adjust methodology based on data:**
- **< 1 year history**: Use QoQ instead of YoY; skip seasonal-naive forecast; use simpler trend extrapolation
- **No prior year for same quarter**: Compare to most recent quarter instead; flag as "limited baseline"
- **Sparse segments**: Some segments may not have enough data for reliable sMAPE — note which ones are unreliable

### Key Functions

```python
def smape(y_true, y_pred):
    """Symmetric Mean Absolute Percentage Error (lower = better)"""
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    return float(np.mean(np.abs(y_pred - y_true) / denom)) * 100  # as percentage

def seasonal_naive_forecast(train, horizon, season_len):
    """Forecast by repeating the last seasonal cycle (e.g., same week last year)"""
    last_season = train.iloc[-season_len:].to_numpy()
    return np.tile(last_season, int(np.ceil(horizon / season_len)))[:horizon]
```

### REQUIRED: Show This Table to the User

**You MUST compute and display this table before the user selects segments.**

| Segmentation Option | # of Goals | Forecast Error (sMAPE) | Complexity | Notes |
|---------------------|------------|------------------------|------------|-------|
| No segmentation (total) | 1 | 18.7% | ✅ Low | Simplest option |
| By region (US vs ROW) | 2 | 17.9% | ✅ Low | -0.8pp vs total |
| By sales_channel (5 values) | 5 | 15.2% | ✅ Low | **-3.5pp vs total** |
| By ads_account_type (2 values) | 2 | 16.8% | ✅ Low | -1.9pp vs total |
| By country (50 values) | 50 | 14.1% | ❌ High | -4.6pp but too many |

### How to Interpret (Read to User)

> *"Lower sMAPE = more accurate forecasts. Here's how to read this:*
> - *If a segmentation **reduces sMAPE by >2 percentage points** vs total, that dimension captures meaningful signal — worth segmenting.*
> - *If a segmentation **barely changes sMAPE** (<1pp), the segments behave similarly — you might keep it simple.*
> - *If a segmentation has **many values** (>10) with only moderate accuracy gain, consider **consolidating** (e.g., group 12 channels into 3)."*

### TL;DR Recommendation

After showing the table, provide a plain-English recommendation:

**If segmentation helps significantly (>2pp improvement)**:
> *"**Accuracy Recommendation**: Segment by **[X]** — reduces forecast error by ~[Y]pp with only [Z] goals to manage."*

**If segmentation doesn't help much (<1pp improvement)**:
> *"**Accuracy Recommendation**: Keep it simple (total-level) — segmenting only improves accuracy by ~[X]pp, not worth the added complexity."*

**If organizational alignment overrides**:
> *"**Accuracy Recommendation**: From a pure accuracy standpoint, [X] is best. But you may choose [Y] for organizational reasons (e.g., teams own those segments)."*

### Required Artifact

Save the Segmentation Advisor output to:
-   `data/[metric]_segmentation_advisor.csv` — Full table with all options tested

---

## Step 1.2: Confirm the Segmentation (single confirmation — do NOT re-ask)

> ⚠️ **Do not repeat Step 1.1b's questions here.** Earlier versions of this skill asked the
> stakeholder to pick segments in §1.1b and then again in §1.2 with near-identical prompts. That is
> one decision, not two. This section is a **confirmation and record**, nothing more.

**Purpose**: State the segmentation back, note whether accuracy and org-fit agreed, and record it.

### Confirm in one message

> *"So we're going with **[dimension]** — [Segment A], [Segment B]. Rationale: [accuracy-driven /
> organizational alignment / both]. That's **[N] goals** to manage. Confirming before I move on."*

If accuracy and organisational fit point different ways, say so plainly and let the stakeholder
choose — org alignment usually wins, and that's a legitimate answer:

> *"Purely on forecast accuracy, [X] is best. But [Y] maps to how teams are actually accountable.
> I'd suggest [Y] — the goal has to be ownable. Your call."*

### Recommendation Format (ELI5)

When recommending, always use this format:

> *"I recommend segmenting by **[Dimension]** because:*
> - *[Segment A] is [growing/flat/declining] at [X]% YoY.*
> - *[Segment B] is [growing/flat/declining] at [Y]% YoY.*
> - *If we combine them, the blended number ([Z]%) hides [insight]."*

**Example**:
> *"I recommend segmenting by **Region (US vs ROW)** because:*
> - *US is growing at +50% YoY.*
> - *ROW is growing at +10% YoY.*
> - *If we combine them, the blended +30% hides that US is carrying the growth. Setting one goal might be unfair to the ROW team."*

### Rules

-   **Max 5 segments**: More than 5 becomes unmanageable.
-   **Ask about groupings**: "Should we use all 12 sales channels, or group them (e.g., Direct vs Partner vs Other)?"

**Gate 3**: Record the user's segment choices before proceeding.

---

## Step 1.3: Trend & Seasonality Analysis

**Purpose**: Understand if the metric is growing, flat, or declining — and if there are patterns.

### What to Analyze

| Analysis | Question It Answers | How to Compute |
|----------|---------------------|----------------|
| **YoY Growth** | "Is it growing compared to last year?" | Compare last 90 days vs same 90 days last year |
| **QoQ Growth** | "Is it accelerating or decelerating?" | Compare last quarter vs prior quarter |
| **Day-of-Week Pattern** | "Is Monday different from Friday?" | Average by day of week; compute range |
| **Month-of-Year Pattern** | "Is December different from June?" | Average by month; compute range |
| **Trend Direction** | "Is the line going up, down, or flat?" | Simple linear regression slope |

### Interpretation Guide (For the User)

| YoY Growth | What It Means |
|------------|---------------|
| > +20% | **Strong growth** — metric is accelerating |
| +5% to +20% | **Moderate growth** — steady trajectory |
| -5% to +5% | **Flat** — no significant change |
| < -5% | **Decline** — investigate why |

| Seasonality Strength | What It Means |
|----------------------|---------------|
| **Strong** (>15% swing) | "December is 30% higher than June — we need to account for this in pacing" |
| **Moderate** (5–15% swing) | "Some monthly variation, but not dramatic" |
| **Weak** (<5% swing) | "Pretty consistent month-to-month" |

### Output (Plain English Summary)

> *"Here's what I found:*
> - **Trend**: The metric is **growing** — up +25% YoY.
> - **Seasonality**: **Strong weekly pattern** — Mondays are 20% lower than Fridays.
> - **Month-of-Year**: **Moderate** — Q4 is typically 15% higher than Q2.
> - **Recent Momentum**: Q1'26 is tracking at +30% YoY, up from +20% in Q4'25."*

⚠️ **Calibration note**: the "20% Monday-vs-Friday" figure above is an *illustration*, not a typical
value. Measured day-of-week swing on Ad Impressions is **8.97%** (Monday highest, Saturday lowest) —
"Moderate" by the table above. Report what you measure; don't inherit the example's magnitude.

### Also report the growth-rate trend, not just the growth rate

A single YoY number hides whether growth is accelerating or decelerating — and that changes what a
"neutral" goal is (Step 2 depends on this).

Live example: Ad Impressions YoY by quarter — **+52.5% → +49.2% → +41.3% → +32.2% → +17.3%**.
Growth is decelerating by roughly **−8pp per quarter**.

> *"YoY is +17.3% most recently, but it's fallen every quarter for five quarters, about −8pp per
> quarter. So 'maintain momentum' isn't a neutral goal here — it's optimistic."*

---

## Step 1.3b: Within-Quarter Shape (required — Step 3 depends on this)

**Purpose**: Measure whether the metric is front-loaded, linear, or back-loaded **within** a quarter.
This is what determines the pacing curve, and it is usually more consequential than day-of-week
seasonality.

### How to compute

For the same quarter last year:

```
shape_share = (sum of first `days_elapsed` days) / (full-quarter sum)
linear_share = days_elapsed / days_in_quarter
```

- `shape_share` **<** `linear_share` ⇒ **back-loaded** (linear pacing will understate early progress)
- `shape_share` **>** `linear_share` ⇒ **front-loaded** (linear pacing will flatter early progress)

### Report it with its consequence

Live example (Ad Impressions, day 29 of 92):

| | Share of quarter |
|---|---|
| Q3'25 actual at day 29 | **30.33%** |
| Linear | **31.52%** |
| | **mildly back-loaded** |

> *"Q3 is mildly back-loaded — last year 30.3% of the quarter landed in the first 29 days, versus
> 31.5% under linear. That's a **3.90pp** difference in pacing, which is **larger than the 2pp Yellow
> band**. Under linear pacing this metric shows 99.4% (Green, but only 1.4pp above Yellow); under
> last year's actual shape it shows 103.3%. Worth deciding which shape we grade against before we
> publish."*

**Flag for Step 3 whenever the two shapes would produce different colours, or differ by more than
the Yellow band's width.** That's a stakeholder decision, not an analyst default.

---

## Step 1.4: Contextualize Latest Performance

**Purpose**: Ground the analysis in the most recent data so the user knows where they stand.

### Always Show Quarterly Context Table

**REQUIRED**: Show the last 6-8 quarters with YoY and QoQ changes. This gives the user context on trajectory, not just the latest number.

| Quarter | Revenue | YoY Δ | QoQ Δ | Notes |
|---------|---------|-------|-------|-------|
| Q2'24 | $84.9M | +49% | +17% | |
| Q3'24 | $105.5M | +54% | +24% | |
| Q4'24 | $137.5M | +49% | +30% | Q4 peak |
| Q1'25 | $108.2M | +49% | -21% | Seasonal dip |
| Q2'25 | $146.7M | +73% | +36% | |
| Q3'25 | $171.3M | +62% | +17% | |
| Q4'25 | $226.8M | +65% | +32% | Q4 peak |
| **Q1'26*** | **$137.5M** | **+27% (full) / +63% QTD** | -39% | *Partial quarter |

**Key interpretation points to highlight:**
- What's the typical YoY range? (e.g., "consistently +49-73% YoY")
- Is growth accelerating or decelerating?
- What's the typical Q4→Q1 drop? (seasonality baseline)

### Handle Partial Quarters (QTD Comparisons)

**If the current quarter is incomplete, ALWAYS use QTD (quarter-to-date) like-for-like comparisons.**

#### When to Use QTD

| Progress Through Quarter | Use QTD? | Confidence |
|--------------------------|----------|------------|
| < 25% (early in quarter) | ⚠️ Optional | Low — too early for reliable comparison |
| 25-50% | ✅ Yes | Moderate — directional signal |
| 50-75% | ✅ Yes | Good — solid comparison |
| > 75% | ✅ Yes | High — reliable like-for-like |

#### How to Compute QTD YoY

1. **Identify the latest date** in the current quarter (e.g., Mar 17 for Q1'26)
2. **Pull same-day range from prior year** (Jan 1 - Mar 17 of prior year)
3. **Compare like-for-like**: Q1'26 QTD vs Q1'25 same days

```sql
-- Example: QTD like-for-like comparison
WITH current_qtd AS (
  SELECT SUM(revenue) as rev FROM table WHERE dt BETWEEN '2026-01-01' AND '2026-03-17'
),
prior_year_same_days AS (
  SELECT SUM(revenue) as rev FROM table WHERE dt BETWEEN '2025-01-01' AND '2025-03-17'
)
SELECT 
  (current_qtd.rev / prior_year_same_days.rev - 1) * 100 as like_for_like_yoy
FROM current_qtd, prior_year_same_days
```

#### How to Present (Read to User)

> *"Q1'26 is partial (through Mar 17 — 85% of the quarter). Here's the like-for-like comparison:*
>
> | Period | Value | Notes |
> |--------|-------|-------|
> | Q1'26 QTD | $137.5M | Through Mar 17 |
> | Q1'25 same days | $82.8M | Jan 1 - Mar 17, 2025 |
> | **Like-for-like YoY** | **+66%** | Apples-to-apples comparison |
>
> *At this pace, Q1'26 would finish at ~$162M (vs Q1'25 full quarter of $108M)."*

#### Anti-Patterns (Avoid These)

❌ **WRONG**: "Q1'26 is $137M vs Q1'25 of $108M = +27% YoY" (comparing partial to full)

✅ **RIGHT**: "Q1'26 QTD is $137M vs Q1'25 same period of $83M = +66% YoY (like-for-like)"

**Key rule**: If you're showing a partial quarter, the YoY comparison MUST be like-for-like (same days), not partial vs full.

---

## Step 1.5: Generate Required Charts

### Minimum Required Charts

1.  **Time Series**: Metric over time (daily or weekly), last 12+ months.
2.  **YoY Comparison**: Current period vs same period last year (overlay or side-by-side).
3.  **Segment Breakdown**: Bar chart showing each segment's contribution.

### Optional Charts (Offer to User)

-   **Day-of-Week Heatmap**: If weekly seasonality is strong.
-   **Month-of-Year Overlay**: If annual seasonality is strong.
-   **Growth Rate Over Time**: If user cares about acceleration/deceleration.

### Chart Delivery

-   Save charts to `figures/` with descriptive names.
-   Embed in the deliverable `.md` using `![alt](figures/...)`.
-   Show in the agent response so the user sees them immediately.

### MANDATORY: Handling Partial Periods in Charts

#### Rule 1: Truncate Partial Weeks/Months in Time Series

**Problem**: The last data point in a time series often "plummets" because the week/month is incomplete. This is misleading.

**Solution**: Cut off partial periods to avoid false "decline" signals.

```python
# Example: Truncate partial week from weekly time series
weekly = df.set_index('dt')['revenue'].resample('W').sum()
max_date = df['dt'].max()

# If last week is partial (less than 7 days), drop it
if max_date.weekday() != 6:  # Not a Sunday (week-end)
    weekly = weekly.iloc[:-1]  # Drop the incomplete week
```

**Apply this to:**
- Weekly time series → Drop last week if < 7 days
- Monthly time series → Drop last month if < 28 days
- Quarterly charts → Mark partial quarters (see Rule 2)

#### Rule 2: Annotate Partial Quarters with Asterisk

**Problem**: Bar charts showing quarterly revenue display partial quarters at full height, making YoY look artificially low.

**Solution**: 
1. Add asterisk (*) to partial quarter labels
2. Show QTD YoY in annotations (not full-quarter comparison)
3. Add footnote explaining the partial period

```python
# Example: Annotate partial quarter
max_date = df['dt'].max()
current_q = f"Q{max_date.quarter}'{max_date.year % 100}"

# Check if partial
q_start = pd.Timestamp(f"{max_date.year}-{((max_date.quarter-1)*3)+1:02d}-01")
days_in_q = (max_date - q_start).days + 1
is_partial = days_in_q < 85  # Less than ~full quarter

if is_partial:
    label = f"{current_q}*"  # Add asterisk
    # Use QTD YoY for annotation, NOT full-quarter comparison
    annotation = f"+{qtd_yoy:.0f}% QTD"
```

**Visual requirements:**
- Partial quarter bars should have asterisk: `Q1'26*`
- YoY annotation should say "QTD" if partial: `+63% QTD` not `+27%`
- Add footnote below chart: `*Q1'26 is partial (through Mar 17). YoY shown is QTD like-for-like.`

#### Anti-Patterns to Avoid

❌ **WRONG**: Weekly chart with final week plummeting to near-zero (incomplete data)

✅ **RIGHT**: Truncate the incomplete week; note "Data through [date]" in title or subtitle

❌ **WRONG**: Quarterly bar chart showing "+27% YoY" for Q1'26 (comparing partial to full)

✅ **RIGHT**: Show "+63% QTD YoY*" with asterisk and footnote explaining it's partial

❌ **WRONG**: No indication that current period is incomplete

✅ **RIGHT**: Clear visual markers (asterisk, different color, footnote) for partial periods

---

## Output: The Insight Card (Required Deliverable)

### Template

```
## Insight Card: [Metric Name]

**Metric Type**: [Total / Average / Ratio / etc.]

**Data Health**: [Clean / Issues handled: X excluded]

---

### Quarterly Performance (Context Table)

| Quarter | Revenue | YoY Δ | QoQ Δ | Notes |
|---------|---------|-------|-------|-------|
| Q2'24 | $XXM | +XX% | +XX% | |
| Q3'24 | $XXM | +XX% | +XX% | |
| Q4'24 | $XXM | +XX% | +XX% | Q4 peak |
| Q1'25 | $XXM | +XX% | -XX% | Seasonal dip |
| Q2'25 | $XXM | +XX% | +XX% | |
| Q3'25 | $XXM | +XX% | +XX% | |
| Q4'25 | $XXM | +XX% | +XX% | Q4 peak |
| **Q1'26*** | **$XXM** | **+XX% QTD** | -XX% | *Partial (through [date]) |

*Partial quarter — YoY shown is QTD like-for-like comparison

**Key Takeaways**:
- Average YoY growth (last 4 full quarters): +XX%
- Typical Q4→Q1 seasonal drop: -XX%
- Trend direction: [Accelerating / Steady / Decelerating]

---

**Trend & Seasonality**:
- **Trend**: [Growing / Flat / Declining] — [X]% YoY
- **Weekly Pattern**: [Strong / Moderate / None]
- **Annual Seasonality**: [Strong / Moderate / None]

---

### Segmentation Accuracy Analysis (sMAPE Backtest)

| Segmentation Option | # of Goals | Forecast Error (sMAPE) | vs Total | Complexity |
|---------------------|------------|------------------------|----------|------------|
| Total (no segmentation) | 1 | [X]% | — | ✅ Low |
| [Dimension A] | [N] | [Y]% | [+/-Z]pp | [✅/⚠️/❌] |
| [Dimension B] | [N] | [Y]% | [+/-Z]pp | [✅/⚠️/❌] |
| ... | ... | ... | ... | ... |

**Accuracy Recommendation**: [Plain English summary of best option from accuracy standpoint]

---

**Segmentation Decision**:
- **User's Choice**: [Dimension] — [Segment A], [Segment B], etc.
- **Rationale**: [Accuracy-driven / Organizational alignment / Both]
- **# of Goals**: [N] (+ derived total if applicable)

**Artifacts Saved**:
- `data/[metric]_cardinality.csv`
- `data/[metric]_topography.csv`
- `data/[metric]_segmentation_advisor.csv`
```

---

## Decision Gates (When to Pause)

| Gate | When | What to Confirm |
|------|------|-----------------|
| **Gate 1** | After Step 1.0a | Metric type confirmed |
| **Gate 2** | After Step 1.0b | Data issues handled |
| **Gate 2b** | After Step 1.1b | sMAPE table shown; user understands accuracy vs complexity tradeoff |
| **Gate 3** | After Step 1.2 | Segments selected (informed by accuracy analysis + org fit) |
| **Gate 4** | After Insight Card | "Does this look right before we move to goal-setting?" |

---

## Checklist for the Agent

- [ ] **Step 0 run; `metric_id`, metric type, direction and route known**
- [ ] **Route checked** — abbreviated run for Route A; skip entirely for Routes C/D/E
- [ ] **Calendar established** — real `days_in_quarter` (92 for Q3, not 90), `latest_date` = max dt *with data*
- [ ] Metric type identified and confirmed, including Rolling-LTM where applicable (Gate 1)
- [ ] Data health checked; issues surfaced and resolved (Gate 2)
- [ ] Segment candidates presented (full cardinality artifact saved) — *Route B only*
- [ ] **Like-for-like YoY divergence computed** as the first segmentation check (§1.1c)
- [ ] sMAPE run **only if the gate says it will change a decision**; skip stated and justified otherwise
- [ ] Segmentation confirmed **once** (§1.2 is a confirmation, not a repeat of §1.1b) (Gate 3)
- [ ] Trend analyzed, **plus the growth-rate trend** (is YoY itself rising or falling?)
- [ ] Seasonality reported from measurement, not from the example's magnitudes
- [ ] **Within-quarter shape measured (§1.3b)** and divergence from linear reported in pp
- [ ] Shape divergence flagged for Step 3 if it exceeds the Yellow band or changes colour
- [ ] Latest performance contextualized with **like-for-like** QTD YoY (never partial vs full)
- [ ] Required charts generated and shown, partial periods truncated/annotated
- [ ] Insight Card produced
- [ ] User confirmed Insight Card before proceeding (Gate 4)

**Next Step**: Once confirmed, proceed to **Step 2: The Architect**.
