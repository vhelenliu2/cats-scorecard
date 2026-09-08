# How the CATS Scorecard Calculates

**For:** manager review and whoever owns the published app after handover

**Dashboard:** [CATS Scorecard](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest)

**As of:** 8 September 2026

This document is the **rulebook**. It explains how any live row is turned into a Value, comparisons, goals, and a color.

The companion [Metric Playbook](03_METRIC_PLAYBOOK.md) is the **catalog**. It walks each live metric from the warehouse table, through the Hex intermediate frame, to the number on the tab.

Read this first. Use the playbook when you need a specific row.

---

## 1. What you are looking at

Every live row is one metric object. The table shows:

| Column | Meaning |
|---|---|
| Value | The number for the current window (often labeled QTD even when it is not a quarter-to-date sum) |
| MoM / QoQ / YoY | Change versus a prior window |
| CQ / QTD / FY goals | Optional targets |
| Status | Color: on track or not |

The published app rebuilds daily at **09:00 CT**. A successful run does not prove every source moved. Check the **Data clock** line (section 3) and the as-of date on the row.

---

## 2. How a number is built

Almost every live metric follows the same three steps.

**1. Raw source.** A warehouse table, a planning Google Sheet, or a Hex pin / component.

**2. Intermediate frame.** A Hex SQL or Python cell that filters, joins, and aggregates to one row per day (or one snapshot). These frames have names like `dauq_counts_df` and `rfd_cats_df`.

**3. Scorecard math.** Python takes that series, picks a window (QTD sum, rolling-28 stock, QTD mean, …), computes comparisons, looks up a goal, and paints a color.

A few metrics skip step 2 and read a pin or a Hex component directly (Scale, Rev/FTE, Measured Revenue). The playbook says so.

**Most live rows do not go through `combined_df`.** They read their own intermediate frame (`dauq_counts_df`, `shopping_rev_df`, `rfd_cats_df`, `hq_signal_df`, and so on) so a calendar join cannot move their as-of. The KPI tab does not use `combined_df` at all.

`combined_df` is still in the notebook as a **narrow leftover join** (`combined_df_2` cast to `combined_df`). Only these live rows still call it:

| Tab | Rows still read from `combined_df` |
|---|---|
| Company Level | Ads Realized Revenue, MAA (+ LCS / MM / SMB) |
| GTM | Credit line setups, lower-funnel AT+DPA, new advertisers, % Booking to Quota |
| Supply | WAUq, monetizable Feed / PDP |

CAPI, Shopping, DAUq, Thriving, Impressions, eCPM, MixShift, RFD, Retention, HQ Signal, Brand, Measured Revenue, Scale, and Rev/FTE use their own frames or pins.

---

## 3. Which clock a row uses

The **Data clock** is the latest date **every daily metric can support**. It is not “today” and it is not the last ads-revenue day by itself.

```
latest_date = min(each daily source’s latest ready date)
```

If DAUq, Thriving, WAUq, shopping, or any other daily source is behind, the clock moves back for **everyone**. Daily rows then cap to that shared date. A row must not sit on its own series max after the clock is set — that max is an **input** to the MIN, not a second clock.

The published table prints this as **Data clock**. If a source is behind, it also says the clock was pulled back and names the lagging table.

### How the freshness guard sets `latest_date`

Three SQL cells collect ready dates (Ads DS cannot read the DAUq or WAUq tables, so those stay on their own connectors). A Python cell takes the earliest:

```
latest_date = min(ads-safe date, DAUq-safe date, WAUq-safe date)
```

Ads-safe is already a MIN of the ads-side daily sources below. Together with DAUq and WAUq, that is the full daily set.

**1. Requested date.** Max `dt` on ads realized revenue in the last 5 days, capped at calendar today. That is the date the dashboard *wants*.

**2. Ads-safe date** (`latest_date_df`). For each ads-side source, take the max ready day. Compact sources must have a non-zero metric. Large facts use partition metadata only (latest date partition with rows). Then:

```
ads-safe date = min(those max ready dates, requested date)
```

| Source | How readiness is judged |
|---|---|
| `direct_ads_revenue_by_sales_channel` | Max `dt` with non-zero realized revenue |
| `brand_pillar_daily_comprehensive_summary` | Max `dt` with non-zero brand revenue |
| `thriving_communities_v2` | Max `pt` with thriving > 0 |
| `ad_supply_key_metrics` | Max `dt` with monetizable feed views > 0 |
| `product_adoption_revenue` | Max `dt` with delivered revenue ≠ 0 |
| `aggregated_shopping_impressions` | Latest date partition with rows |
| `msmt_foundation_rolling_revenue` | Latest date partition with rows |
| `conversion_signals_quality_score` | Latest date partition with rows |
| `t_pillar_rfd_daily_v2` | Latest date partition with rows |
| `e2e_performance` | Latest date partition with rows |

**3. DAUq-safe date** (`dauq_date_freshness_df`). Max `DATE(pt)` on `baseline_canonical_cube` in the last 2 weeks with `is_dauq` and `n_users` > 0.

**4. WAUq-safe date** (`wauq_date_freshness_df`). Max `DATE(pt)` on `tier0_wauq_reporting` in the last 2 weeks with `wauq` > 0.

If the guarded date is behind the requested date, `data_delayed` is true and `scorecard_missing_detail` lists which source stopped where. Quarter start / end and “days elapsed” are computed from the **guarded** `latest_date`, not from today.

If a freshness SQL cell is empty, Hex warns and falls back rather than blocking the whole notebook. Treat that as a clock failure, not a metric change.

### After the shared clock

Some rows apply a **tighter window** on top of `latest_date` (last complete month, or a 28 / 91-day bake). That is a grain, not a second freshness clock. Those grains are not inputs to the MIN.

| After the clock | What it is | Who uses it |
|---|---|---|
| Shared safe date | `latest_date` from the MIN above | All daily rows (ads, DAUq, Thriving, WAUq, KPI, GTM, Supply) |
| Baked window | Guarded as-of minus 28 or 91 days | Retention |
| Month-end / last FTE month | Last complete planning month | Scale, Rev/FTE |
| Last complete month | MixShift 7-day bake | MixShift |

---

## 4. How percentage change is calculated

**Standard** (revenue, impressions, MAA, DAUq, Thriving, WAUq, most sums and means):

```
change = (current window − prior window) / prior window
```

Skip the cell if either side is **missing** or the prior window is zero. Do not write `0` for a skipped cell. Hex stores `0.12` and displays `12%`.

**A/B lifts are not standard.** They are percentage-point deltas:

```
change = current lift − prior lift
```

A lift moving from −31% to 0 is **+31 pp**, not −100%. If a stored lift looks like a whole number (`abs(x) > 1.5`), Hex divides by 100 first so −31 and −0.31 are the same lift.

The same A/B row on **KPI and Company Level must match**: same source, same current-month Value, same MoM / QoQ / YoY. Today both tabs leave those comps blank. If comps are turned on, both tabs use the same percentage-point helper. A tab mismatch is a bug.

---

## 5. Three standard families

Most of Company Level, and the KPI / Supply rows that copy it, use one of these.

### Family A — QTD sum (a flow)

**Used for:** Ads Realized Revenue, Ad Impressions (and US/ROW), Overall Measured Revenue. Shopping Revenue uses this for the **actual**; its QTD **goal** does not (section 7).

| Field | Window |
|---|---|
| Value | Sum from quarter start through as-of |
| MoM | Last 28 days vs the 28 days immediately before that (not calendar month-to-date) |
| QoQ / YoY | Same number of days into the prior quarter / prior year |

**Standard QTD goal:**

```
QTD goal = current-quarter goal × (days elapsed / days in quarter)
```

**Pacing:** Value ÷ QTD goal.

### Family B — Rolling-28 stock (a level)

**Used for:** MAA and MAA LCS / MM / SMB.

| Field | Window |
|---|---|
| Value | Rolling-28 stock on as-of |
| MoM | As-of vs as-of minus 28 days |
| QoQ | As-of minus 91 days |
| YoY | As-of minus 365 days |

Goals are **looked up** on the MAB Daily Goals Allocation sheet (EOQ / as-of / 31 Dec). They are not prorated by days elapsed.

**Pacing:** Value ÷ that QTD sheet row. Green at ≥100%, red below. No yellow.

### Family C — QTD mean

**Used for:** DAUq (and breakouts), Thriving Communities (and breakouts), WAUq (and US/ROW).

| Field | Window |
|---|---|
| Value | Mean of the daily series from quarter start through as-of |
| MoM | R28 mean vs the prior R28 mean |
| QoQ / YoY | Same-elapsed QTD mean |

**DAUq QTD goal = the current-quarter goal.** A mean is not paced down by days elapsed.

eCPM is a **ratio of two family-A sums**:

```
eCPM = realized revenue / impressions × 1,000
```

The CQ eCPM goal (total only) uses the prior-quarter delivered/realized ratio. The QTD eCPM goal is blank. Status is grey: there is no official eCPM pacing.

---

## 6. Status colors

```
pacing = Value / QTD goal
```

If the QTD goal is missing, pacing is empty and status is grey. It must not become green or `0%`.

| Rule | Green | Yellow | Red / grey | Used on |
|---|---|---|---|---|
| `goal_binary` | ≥100% of QTD goal | — | <100% | Ads Realized Revenue, MAA, Rev/FTE, Scale |
| `impressions_pacing` | ≥98% | 96–98% | <96% | Ad Impressions, DAUq |
| `goal_rev_2m` | ≥99.5% | Value + $2M covers the QTD goal | else | Upper Funnel Revenue |
| `goal_rev_5m` | ≥99.5% | Value + $5M covers the QTD goal | else | Overall Measured Revenue |
| `shopping_pace` | ≥85% of the weekly paced target | 70–85% | <70% | Shopping Revenue |
| `ab_goal` | CQ already hit; or last 15 days of the quarter and ≥95% | last 15 days, 70–95% | last 15 days, <70%. Otherwise **grey — too early** | A/B lifts |
| `grey` | — | — | always grey | No official target, or rule not confirmed |
| `yoy` | YoY × direction ≥ 0 (0.5% buffer) | — | else | MixShift; monetizable-feed headline |
| `booking_quota` | Week of quarter ≥55% / ≥80% / ≥95% | 50 / 75 / 90 | else | % Booking to Quota |
| `lower_bounded_goal` | Value ≥ lower bound | — | else | DPA ROAS* when a bound exists |

CPC, kCPA, Post-Install CPA, and MixShift CPA are **lower-is-better**. Everything else is higher-is-better unless the playbook says otherwise.

Do not assign the leftover rule named `dauq`. It treats a user target (~130 million) as if it were a ratio. Live DAUq uses `impressions_pacing`.

---

## 7. Definitions that do not match the rest of the dashboard

These rows are live and intentional. They will not match family A/B/C. This is the usual source of “why doesn’t this MoM match the others?”

| Row | What is different |
|---|---|
| **Scale Our Foundations** (all five) | Each row is its own definition. OE is a month-end **level**; Cloud is **YTD**; Model / Experimentation are **QTD counts**; SOTA is a **grade**. OE “QoQ” is month-end vs prior-quarter-end month, not same-elapsed QTD. Actuals come from Hex pins. |
| **Revenue / Sales + Marketing FTE** | Last-twelve-months **level** (ads revenue ÷ average LTM billable FTE), pinned to the last month that has FTE. Comparisons are vs the window ending 1 / 3 / 12 months earlier. FY $3.7M is a level, not a sum of quarters. |
| **Shopping Revenue QTD goal** | The actual follows family A. The QTD goal is a **hardcoded weekly paced target** (not day-elapsed CQ). Status uses 85% / 70%. YoY is YTD vs prior-year same calendar day. |
| **A/B lifts** | Value = current **calendar month** lift vs control. QTD goal blank. Status vs the **CQ** goal; grey until the last 15 days unless CQ is already hit. KPI and Company Level MoM / QoQ / YoY must match (today both blank). Post-Install CPA actuals key ≠ goals key (`CPA A/B`). |
| **Reach / Frequency / Depth** | QTD **snapshot** on as-of. MoM blank. QoQ / YoY = same day-of-quarter. |
| **Retention** | Share still active after a 28- or 91-day **bake**. Comparisons are percentage points on the baked as-of. |
| **MixShift** | The Value **is** the QoQ MixShift (last complete month, 7-day bake, advertisers in both periods). YoY is the YoY MixShift. |
| **HQ Signal Adoption** | Latest HQ revenue rate. CQ 45% / FY 50% are reference only. QTD blank. Status grey (rule pending). Comps are percentage points. |
| **Budget Utilization** | Intentionally **blank**. The lean flight-budget table stopped on 2026-06-02. Restoring it would print ~100% utilization. |
| **gROAS* (KPI)** | Latest geometric R28. No official target. Comparisons not wired. GTM **DPA ROAS*** uses the same series but can show a lower-bound status. |

Full Scale / Rev-FTE formulas are in the playbook cards.

---

## 8. What makes the dashboard look stale or wrong

### A source went quiet

| What failed | What you see |
|---|---|
| Any freshness-guard source lags | `latest_date` is pulled back to that day. Most QTD sums and paced goals sit on the shared safe date. The 09:00 run can still succeed; the Data clock line names the lagging table. |
| Ads warehouse `dt` stops | Requested date and ads-safe date freeze. Same effect as above. |
| DAUq cube or WAUq reporting lags | The shared clock is pulled back (those dates are in the MIN). Daily rows, including DAUq / Thriving / WAUq, cap to that date. |
| Google Sheets connection missing | MAA, DAUq, A/B, and some Scale goals go grey or keep the last successful parse. |
| Planning tab or column renamed | Lookup misses. A/B is the highest recurrence (`Price: Post-Install CPA` must stay in the rename map). |
| MAB / DAUq sheet not rolled for the new quarter | Hex keeps last-on-or-before. The number looks current and is last quarter’s target. |
| Hardcoded quarter goals not rolled | Impressions `IMPRESSIONS_GOALS`, Shopping weekly QTD, Measured CQ step, Scale checksums, Rev/FTE Q4. |
| Brand pillar, Measured component, or a Scale pin fails | That row empties or falls back to a checksum without looking broken. |

### Zero vs missing

These must not be mixed.

| In the cell | Meaning |
|---|---|
| `0` / `0%` / `$0` | The metric is a real zero for that window |
| Blank / `-` / not available | The source or prior window is missing. Skip the cell. |

Never coerce a failed pull, an empty frame, or a skipped comparison to `0`. Pacing with a missing QTD goal stays blank — it must not become `0%` (section 6). A/B formatting already follows this: `None` prints `-`; a true 0% lift prints `0.0% A/B`.

If a connector failed and the table shows `0`, that is a bug.

### A comparison that is not a bug

These look wrong in review and are usually **two different rules**, not a stale refresh.

**Scale “QoQ” does not match revenue QoQ.**  
Revenue QoQ is same-elapsed quarter-to-date (family A). Operational Excellence “QoQ” is this month-end versus the last month of the prior quarter (July vs June). Different window, different meaning.

**A/B is grey in month 1 or 2 of the quarter.**  
`ab_goal` stays grey until the last 15 days unless the current-quarter goal is already hit. Grey here means “too early to call,” not “goal missing.”

**Retention or MixShift looks earlier than the Data clock.**  
They consume the guarded clock, then apply a bake or last-complete-month grain. That is the window, not a second freshness date.

---

## 9. How to review a number

1. Find the row in the playbook. Confirm it is a **copy** (change once) or a **recompute** (change on both tabs).
2. Which **family** is it — A, B, C, or an exception in section 7?
3. Walk **raw source → intermediate frame → Hex window**.
4. Daily as-of should be the freshness-guard `latest_date`. If the row looks earlier, is it a bake / month-end grain, or did a cell ignore the clock?
5. Is the goal day-elapsed, CQ-as-QTD, a sheet lookup, or hardcoded?
6. If MoM looks wrong, are you comparing two different comparison rules — or the same metric on two tabs that must match?

The playbook has the end-to-end path for every live metric.
