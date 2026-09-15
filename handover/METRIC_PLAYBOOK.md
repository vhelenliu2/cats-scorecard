# Metric playbook

**As of:** 10 September 2026

Search the [list](#list-of-metrics). Open the card.

Refresh or “is this a bug?” → [How the scorecard works](HOW_THE_SCORECARD_WORKS.md).

**Tabs:** [Company Level](#company-level-goals) · [KPIs](#cats-sc--kpis) · [GTM](#ads-product--gtm) · [Supply](#ads-supply-drivers) · [RFD names](#appendix--gtm-rfd-child-names)

Every card uses the same fields: **Owner · Tabs · Value · Color · Actuals · Goals**. **Watch** only when something breaks easily.

---

## Rows that need extra care

| Row | Card |
|---|---|
| Scale | [Scale](#scale-our-foundations) |
| Rev/FTE | [Rev/FTE](#revenue--sales--marketing-fte-ltm-as-of-month-) |
| A/B | [Company Level](#c-performance-ab-company-level) · [KPI names](#performance-ab-kpi) |
| Goals in code | [Impressions](#ad-impressions-qtd--and-us--row) · [Shopping](#shopping-revenue-qtd-) · [Measured](#overall-measured-revenue-qtd-) · [Upper Funnel](#upper-funnel-revenue-qtd-) |
| Budget | [Budget](#budget-utilization--and-bid-types) |

How to pull a monthly or quarter number → [refresh](HOW_THE_SCORECARD_WORKS.md#how-to-refresh-the-numbers).

---

## List of metrics

| Metric | Tabs | Value |
|---|---|---|
| [Ads Realized Revenue (QTD), $](#ads-realized-revenue-qtd-) | Company Level | quarter sum |
| [MAA (R28D), #](#maa-r28d--and-lcs--mm--smb) + LCS / MM / SMB | Company Level; KPI | 28-day level |
| [DAUq (QTD), #](#dauq-qtd--and-us--row) + US / ROW | Company Level; Supply | quarter average |
| [Thriving Communities, #](#thriving-communities--and-us--row--gold--silver--bronze) | Company Level | quarter average |
| [Ad Impressions (QTD), #](#ad-impressions-qtd--and-us--row) + US / ROW | Company Level; Supply | quarter sum |
| [eCPM (QTD), $](#ecpm-qtd--and-us--row) | Company Level | quarter ratio |
| [C-performance A/B](#c-performance-ab-company-level) | Company Level; KPI | this month’s lift |
| [Shopping ROAS A/B](#shopping-roas-ab) | Company Level; KPI | this quarter’s lift |
| [Upper Funnel Revenue (QTD), $](#upper-funnel-revenue-qtd-) | KPI | Brand feed |
| [Post-Install CPA A/B](#performance-ab-kpi) | KPI | this month’s lift |
| [Shopping Revenue (QTD), $](#shopping-revenue-qtd-) | KPI; GTM | quarter sum |
| [gROAS* (R28D)](#groas-r28d) | KPI | latest R28 |
| [Overall Measured Revenue (QTD), $](#overall-measured-revenue-qtd-) | KPI; GTM | quarter sum |
| [High Quality Signal Adoption, %](#high-quality-signal-adoption-) | KPI; GTM | latest rate |
| [Revenue / Sales + Marketing FTE](#revenue--sales--marketing-fte-ltm-as-of-month-) | KPI | LTM level |
| [Reach / Frequency / Depth](#reach--frequency--depth-kpi-headlines) | KPI; GTM | day-D snapshot |
| [Retention (R28D) - SMB, %](#retention-r28d---smb-) | KPI | baked 28d |
| [Scale](#scale-our-foundations) | KPI | each its own |
| [MixShift Key3 CPA / iCR](#same-store-mixshift-key3-cpa--icr-qoq-) | GTM | MixShift |
| [DPA ROAS* (R28D)](#dpa-roas-r28d) | GTM | latest R28 |
| [CAPI adoption](#revenue-weighted-capi-adoption---lcs--mm-) | GTM | latest rate |
| [Credit line setups](#-credit-line-setups---global-lcs--global-mm-qtd) | GTM | QTD count |
| [Lower-funnel AT+DPA](#-of-lower-funnel-revenue-using-automated-targeting--dpa-r7d) | GTM | R7 share |
| [New Advertisers Activated](#new-advertisers-activated-qtd--and-channels) | GTM | quarter sum |
| [Retention R91 / R28](#retention-r91d-and-retention-r28d) | GTM | baked |
| [Budget Utilization](#budget-utilization--and-bid-types) | GTM | **blank** |
| [% Booking to Quota](#-booking-to-quota) | GTM | as-of % |
| [WAUq (QTD), #](#wauq-qtd--and-us--row) | Supply | quarter average |
| [DAUq App / Web](#dauq-qtd--total--us--row--app--web--geo--surface) | Supply | quarter average |
| [Monetizable Feed / PDP (R7D)](#monetizable-feed-post-views-r7d-and-monetizable-pdp-screen-views-r7d) | Supply | R7 average |

---

## Company Level Goals

### Ads Realized Revenue (QTD), $

- **Owner:** Bassem Haddad, Evie Sarkes
- **Tabs:** Company Level
- **Value:** quarter sum
- **Color:** hit or miss (≥100% of QTD quota)
- **Actuals:** `reddit-ads-prod.ads_ds_measures.direct_ads_revenue_by_sales_channel` (exclude House Ads / internal in the ranked-category step)
- **Goals:** `daily_quota_profile` (latest snapshot in the last 30 days) → CQ and QTD quota. FY blank
- **Watch:** Hex frame is `revenue_base_df`. Do not route this through a calendar join.

---

### MAA (R28D), # — and LCS / MM / SMB

- **Owner:** DS Ye Liu / Pengfei Qiao; RSO Paola Madueno. KPI also lists Yoni Sauerbrun
- **Tabs:** Company Level; KPI
- **Value:** rolling 28-day level
- **Color:** hit or miss
- **Actuals:** one business per day — spine `rddt-ds-data1-prod.ad__attributes.businesses_comprehensive` ∩ `reddit-marketing.facts.lifecycle_28d_ads_account_business_id` (not dormant); spend from `direct_ads_revenue_by_sales_channel` (at least one qualifying delivered-revenue day in `[dt−27, dt]`; no House Ads / internal)
- **Goals:** [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc) → Daily Goals Allocation (`Overall`, `Global LCS`, `Global MM`, `Global SMB`). EOQ / as-of / 31 Dec lookups — **not** prorated
- **Watch:** children do not have their own registry ids.

---

### DAUq (QTD), # — and US / ROW

- **Owner:** Logan Wilson
- **Tabs:** Company Level; Supply (Total / US / ROW). [App / Web](#dauq-qtd--total--us--row--app--web--geo--surface) is Supply only
- **Value:** quarter average
- **Color:** Impressions / DAUq rule (98 / 96). Grey if the goal is missing
- **Actuals:** `rddt-tier0-metrics1-prod.dauq.baseline_canonical_cube`, `is_dauq`, `SUM(n_users)` — same as [Daily DAUq Report v2](https://app.hex.tech/reddit/app/Daily-DAUq-Report-v2-033JmYVBjqTdtm70mD94CP/latest)
- **Goals:** [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ) → Latest Forecast. Sheet is **millions**; Hex stores **users**. **QTD goal = CQ**
- **Watch:** Registry name is `DAUq (QTD), M`. Hex display is `DAUq (QTD), #`. Join on `metric_id` **`MET-419D6C123B19`**.

Breakouts: `dauq`, `dauq_us` (geo US), `dauq_row` (everyone else, including unknown geo).

---

### Thriving Communities, # — and US / ROW / Gold / Silver / Bronze

- **Owner:** Ben Feinberg, Victor Ronda
- **Tabs:** Company Level
- **Value:** quarter average, rounded to an integer
- **Color:** grey (region children: status off)
- **Actuals:** `rddt-ds-data1-prod.subreddit__daily.thriving_communities_v2` by region and Gold / Silver / Bronze
- **Goals:** none
- **Watch:** as-of is the Data clock (thriving’s ready date is an input to that MIN).

---

### Ad Impressions (QTD), # — and US / ROW

- **Owner:** DS Yoni Sauerbrun; Finance Yona Kuritzky
- **Tabs:** Company Level; Supply
- **Value:** quarter sum
- **Color:** Impressions / DAUq rule
- **Actuals:** `direct_ads_revenue_by_sales_channel` (`impressions`, `location_country`). Internal accounts excluded
- **Goals:** `IMPRESSIONS_GOALS` in the Company Level Metrics cell. Q3 2026: US 59.8B + ROW 57.9B. QTD = CQ × day-elapsed
- **Watch:** edit the cell when the quarter rolls.

---

### eCPM (QTD), $ — and US / ROW

- **Owner:** same as Impressions
- **Tabs:** Company Level
- **Value:** revenue ÷ impressions × 1,000
- **Color:** grey
- **Actuals:** same ads revenue table (realized revenue + impressions)
- **Goals:** CQ (total only) = revenue CQ × prior-Q delivered/realized ÷ impressions CQ × 1,000. QTD blank. US/ROW blank

---

### C-performance A/B (Company Level)

- **Owner:** Christa Benton
- **Tabs:** Company Level; KPI (labels may differ)
- **Value:** this calendar month’s lift vs control
- **Color:** green if CQ is already hit; last month of the quarter 95 / 70; otherwise grey
- **Actuals:** C-performance launch-tracker / A/B actuals sheet
- **Goals:** C-performance A/B goals sheet, through the Hex rename map. Status uses the **quarter** goal. No QTD goal
- **Watch:** a missed rename leaves the goal blank. KPI-only: [Post-Install CPA](#performance-ab-kpi). Not on this tab: CPV6 A/B.

| Display | Sheet key | Direction |
|---|---|---|
| CTR A/B | CTR A/B | Higher better |
| kICR4 A/B | kICR4 A/B | Higher better |
| PiIR A/B | PiIR A/B | Higher better |
| VVR6 A/B | VVR6 A/B | Higher better |
| CPC A/B | CPC A/B | Lower better |
| kCPA A/B | kCPA4 A/B (display drops the 4) | Lower better |

---

### Shopping ROAS A/B

- **Owner:** Ryan Sekulic, Lillian Kravitz
- **Tabs:** Company Level; KPI
- **Value:** this quarter’s lift
- **Color:** same A/B rule as above
- **Actuals:** Shopping A/B sheet (`Shopping ROAS A/B`)
- **Goals:** `Shopping ROAS A/B Goal`. FY defaults to **0.60** if the sheet is quiet

---

## CATS SC / KPIs

### Upper Funnel Revenue (QTD), $

- **Owner:** Emily Glauser
- **Tabs:** KPI
- **Value:** Brand feed QTD / YTD (not summed here)
- **Color:** Upper Funnel rule ($2M yellow)
- **Actuals:** `reddit-ads-prod.ads_ds_metrics.brand_pillar_daily_comprehensive_summary`.`brand_revenue`, GLOBAL — same as the [Brand Pillar](https://app.hex.tech/reddit/app/Brand-Pillar-Business-Overview-Dashboard-6mNDevMXkAFJjOGjuervnI/latest?tab=revenue_summary) revenue tab
- **Goals:** CQ / FY from [brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit?tab=t.0#bookmark=id.sw1mjrnh4i0a) (Progress to Revenue Goal 2026). QTD = CQ × CATS day-elapsed
- **Watch:** `% of top 200 brand advertisers who adopt 3+ best practices` is not on this tab.

---

### Performance A/B (KPI)

Same as [C-performance A/B](#c-performance-ab-company-level). Names on this tab:

| Display | Actuals col | Goals key | Direction |
|---|---|---|---|
| CTR A/B | CTR A/B | CTR A/B | Higher better |
| kiCR4 A/B | kICR4 A/B | kICR4 A/B | Higher better |
| PilR A/B | PiIR A/B | PiIR A/B | Higher better |
| CPC A/B | CPC A/B | CPC A/B | Lower better |
| kCPA A/B | kCPA4 A/B | kCPA4 A/B | Lower better |
| Post-Install CPA A/B | Post-Install CPA A/B | **CPA A/B** | Lower better |
| VVR6 A/B | VVR6 A/B | VVR6 A/B | Higher better (under Brand) |

**Post-Install CPA** is on this tab only. Goals key `CPA A/B` is the rename that breaks most often.

---

### Shopping Revenue (QTD), $

- **Owner:** Ryan Sekulic, Vinay Sridhar
- **Tabs:** KPI; GTM
- **Value:** quarter sum. MoM = trailing 28 days vs the 28 days before that. QoQ = same-elapsed QTD. **YoY** = YTD vs prior-year same calendar day
- **Color:** Shopping rule (85 / 70)
- **Actuals:** `reddit-ads-prod.ads_ds_measures.aggregated_shopping_impressions` (Catalog Sales / DPA + custom product ads). Exclude listed internal ad accounts and `business_name = Reddit`
- **Goals:** CQ / FY $22M / $70M. QTD goal = weekly target in the metrics cell ($5,614,458 as of this writing) — not CQ × days elapsed
- **Watch:** edit the weekly number when the quarter rolls.

---

### gROAS* (R28D)

- **Owner:** Ryan Sekulic
- **Tabs:** KPI. GTM [DPA ROAS*](#dpa-roas-r28d) uses the same series
- **Value:** latest geometric R28 on or before ads as-of
- **Color:** grey. Comps not wired
- **Actuals:** `aggregated_shopping_impressions` (pixel-enabled purchase value / ad views)
- **Goals:** none

---

### Overall Measured Revenue (QTD), $

- **Owner:** Anirudha Sundaresan
- **Tabs:** KPI; GTM
- **Value:** quarter sum through the Data clock
- **Color:** Measured rule ($5M yellow)
- **Actuals:** Hex component `measured_revenue_daily`, column `measured_revenue`
- **Goals:** CQ 2026 $200 / $350 / $450 / $500M. FY $1.5B. QTD = CQ × day-elapsed

---

### High Quality Signal Adoption, %

- **Owner:** Aayush Shah, Emre Enes Yavuz
- **Tabs:** KPI; GTM
- **Value:** latest `hq_revenue_rate` = HQ 90d revenue ÷ eligible 90d revenue
- **Color:** grey (rule pending)
- **Actuals:** `reddit-ads-prod.ads_ds_measures.msmt_foundation_rolling_revenue` (28d / 90d conversion + catalog sales, web-active MAAs, exclude CLICKS / UNKNOWN) + `rddt-ads-measurement1-prod.conversion_signals.conversion_signals_quality_score` (pixel overall, integration ALL)
- **Goals:** CQ / FY 45% / 50% — reference only. QTD blank
- **Watch:** HQ only if **every** active optimization-goal event meets the threshold (0.6 for PageVisit / ViewContent, else 0.7) on a 28-day average score.

---

### Revenue / Sales + Marketing FTE (LTM as of {month}), $

- **Owner:** Aaron Nelson
- **Tabs:** KPI
- **Value:** LTM ads revenue ÷ average LTM billable FTE (completed months only)
- **Color:** hit or miss
- **Actuals:** revenue from `direct_ads_revenue_by_sales_channel` (monthly). FTE from the planning-sheet pin (billable Sales + Marketing)
- **Goals:** Q1–Q3 waypoints $3.07 / $3.2 / $3.4M. Q4 unset. FY $3.7M is a **level**. QTD goal = linear path from the prior waypoint
- **Watch:** as-of = last month that has FTE. Do not pair a later partial revenue month with held-forward FTE. Comps = that level vs 1 / 3 / 12 months earlier.

---

### Reach / Frequency / Depth (KPI headlines)

- **Owner:** Ye Liu, Dana Avgil
- **Tabs:** KPI headlines; GTM [diagnostics](#reach--frequency--depth-diagnostics-gtm)
- **Value:** snapshot on as-of. MoM blank. QoQ / YoY = same day-of-quarter
- **Color:** grey
- **Actuals:** `rddt-ds-data1-prod.sandbox.t_pillar_rfd_daily_v2` — Demand Health QTD, `revenue_basis = delivered`, `basis_used = as_was`, baked, Business ID. Channels LCS, Mid-Market, SMB, Unmanaged, Partnerships (exclude Unknown / Other)
- **Goals:** none

| Display | Column | Calc |
|---|---|---|
| Reach (QTD Advertisers), # | `rfd_reach` | `SUM(advertisers)` |
| Frequency (QTD Active Days / Advertiser), # | `rfd_frequency` | `SUM(active_days) / SUM(advertisers)` |
| Depth (QTD Revenue / Active Day), $ | `rfd_depth` | `SUM(window_revenue) / SUM(active_days)` |

---

### Retention (R28D) - SMB, %

- **Owner:** Ye Liu
- **Tabs:** KPI. GTM [channels](#retention-r91d-and-retention-r28d) match “Global SMB (Managed + Unmanaged)”
- **Value:** share of businesses active in the trailing 28d baseline that return with spend in the next 28d. Headline = SMB Managed + Unmanaged
- **Color:** grey. Comps are percentage points
- **Actuals:** `direct_ads_revenue_by_sales_channel`, qualifying delivered spend, grain `ads_account_business_id`
- **Goals:** none
- **Watch:** as-of is **28 days behind** ads `latest_date`.

---

### Scale Our Foundations

- **Owner:** Virgilio Pigliucci
- **Tabs:** KPI
- **Value:** each row its own (level, YTD, count, or grade)
- **Color:** hit or miss (`goal_binary`) — each row’s bar is its own pacing rule
- **Actuals:** pillar Google Sheets, pinned monthly (~1 month lag: September still shows July)
- **Goals:** see table
- **Watch:** a failed pin can sit on a checksum and still look healthy. Do not reuse retired names Marketplace Efficiency or Ads Tier0 Availability.

| Display | Pin | Goal / pacing |
|---|---|---|
| Operational Excellence (as of {month}), sum | Unweighted **sum** of Manager Dashboard team scores at month-end | CQ +5%, FY +40%. QTD rate = +5% × completed months / 3. **Pacing = QoQ ÷ that rate** |
| Cloud Savings (YTD as of {month}), $ | Tracker C1 **YTD** COR savings; else pillar Q3 YTD $9.2M | FY $10M. QTD bar = FY × completed months / 12. CQ blank. QoQ uses Q1 $0.34M / Q2 $5.7M |
| Model Velocity (QTD as of {month}), # | QTD Ranking + Retrieval + Shopping launches with KPI movement (exclude bugs / deprecations / backtests / 0). Q2 checksum 23 | FY +25% YoY. QTD = last-year same-elapsed × 1.25 |
| Experimentation Velocity (QTD as of {month}), # | QTD distinct qualifying Ads experiments. Insights app unread; pillar checksums until SQL is granted. [Ads Experimentation Insights](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) | FY +33% YoY. QTD = last-year same-elapsed × 1.33 |
| Ads SOTA ML (as of {month}) | Subjective grade from the Scale pillar table | Path C- (Jan) → C (Q2) → B- (Q3) → B (Dec) |

---

## Ads Product & GTM

### Same-Store MixShift Key3 CPA / iCR (QoQ), %

- **Owner:** Emre Enes Yavuz
- **Tabs:** GTM
- **Value:** the QoQ MixShift (last finished month). MoM not defined. YoY = YoY MixShift
- **Color:** year-over-year sign. CPA lower-is-better; iCR higher-is-better
- **Actuals:** `reddit-ads-prod.ads_ds_metrics.e2e_performance`. Key3 = `objective_type = CONVERSIONS` and `optimization_goal IN (LEAD, SIGN_UP, PURCHASE)`. Same-store advertisers; **7-day bake**
- **Goals:** none

---

### DPA ROAS* (R28D)

- **Owner:** Ryan Sekulic
- **Tabs:** GTM
- **Value:** same series as KPI [gROAS*](#groas-r28d)
- **Color:** lower-bound rule when `gROAS_s_pi_lo` exists (KPI gROAS* stays grey)
- **Actuals:** `aggregated_shopping_impressions`
- **Goals:** optional lower bound only

---

### Revenue-Weighted CAPI Adoption - LCS + MM, %

- **Owner:** BA
- **Tabs:** GTM
- **Value:** 90d revenue of CAPI-active MAAs ÷ 90d revenue of eligible MAAs. Comps are percentage points
- **Color:** grey
- **Actuals:** `msmt_foundation_rolling_revenue`. Eligible: 28d conversion/catalog revenue > 0, web-active, CONVERSIONS / CATALOG_SALES, optimization not CLICKS / UNKNOWN. CAPI = `is_web_capi_active_28d`. **LCS + MM only**
- **Goals:** none

---

### # Credit Line Setups - Global LCS + Global MM (QTD)

- **Owner:** Ads DS
- **Tabs:** GTM
- **Value:** QTD cumulative distinct `funding_instrument_id`
- **Color:** grey; status display off
- **Actuals:** `reddit-ads-prod.business_analytics_prod.credit_line_setups`
- **Goals:** none

---

### % of Lower Funnel Revenue Using Automated Targeting + DPA (R7D)

- **Owner:** Ads DS
- **Tabs:** GTM
- **Value:** within-quarter rolling 7 days of lower-funnel AT-or-DPA revenue ÷ lower-funnel delivered revenue. Comps are percentage points
- **Color:** grey; status display off
- **Actuals:** `reddit-ads-prod.business_analytics_prod.product_adoption_revenue`. `del_automated_targeting_revenue` is already expansion **or** DPA — do not add DPA again
- **Goals:** none

---

### Shopping Revenue, Measured Revenue, HQ Signal (GTM)

See [Shopping](#shopping-revenue-qtd-), [Measured](#overall-measured-revenue-qtd-), [HQ Signal](#high-quality-signal-adoption-).

---

### Reach / Frequency / Depth diagnostics (GTM)

Same calc as the [KPI headlines](#reach--frequency--depth-kpi-headlines). GTM adds two trees per family:

| Tree | Children |
|---|---|
| by Daily Spend Cohort | parent + 4 tiers + 3 lifecycles under each tier |
| by Sales Channel | parent + 5 channels |

**Tiers:** `<$50/day`, `$50-$200/day`, `$200-$1000/day`, `$1000+/day`  
**Lifecycles:** Newly Activated, Rolling Active, Reactivated  
**Channels:** LCS, MM, SMB Managed, SMB Unmanaged, Channel Partnerships

Every display name and column → [appendix](#appendix--gtm-rfd-child-names).

---

### New Advertisers Activated (QTD), # — and channels

- **Owner:** Ads DS
- **Tabs:** GTM
- **Value:** quarter sum (R28 MoM, same-elapsed QoQ / YoY)
- **Color:** year-over-year sign
- **Actuals:** `direct_ads_revenue_by_sales_channel`. Activation = first day with qualifying delivered spend (`delivered_revenue > 0`, exclude House Ads / internal) at `ads_account_business_id`. Channel = as-was primary on that day
- **Goals:** none

| Display | Column |
|---|---|
| New Advertisers Activated (QTD), # | `total_activations_sum` |
| New Advertisers Activated - Global LCS (QTD), # | `global_lcs_activations_sum` |
| New Advertisers Activated - Global MM (QTD), # | `global_mm_activations_sum` |
| New Advertisers Activated - Global SMB (QTD), # | `global_smb_activations_sum` |
| New Advertisers Activated - Global Unmanaged (QTD), # | `global_unmanaged_smb_activations_sum` |

---

### Retention (R91D) and Retention (R28D)

- **Owner:** Ads DS
- **Tabs:** GTM
- **Value:** same ads-revenue spine as KPI SMB retention. Comps are percentage points
- **Color:** grey
- **Actuals:** see columns. **R91:** `91baseline_0gap_91comparison`, headline = LCS + MM + SMB Managed, **91-day bake**. **R28:** `28baseline_0gap_28comparison`, headline = SMB Managed + Unmanaged, **28-day bake**
- **Goals:** none

| Display | Column |
|---|---|
| Retention (R91D), % | `retention91_df.overall_retained_91` |
| Retention - Global LCS (R91D), % | `lcs_retained_91` |
| Retention - Global MM (R91D), % | `mm_retained_91` |
| Retention - Global SMB Managed (R91D), % | `smb_retained_91` |
| Retention (R28D), % | `retention28_df.overall_retained_28` |
| Retention - Global SMB (Managed + Unmanaged) (R28D), % | `smb_combined_retained_all` |
| Retention - Global SMB Managed (R28D), % | `smb_retained_all` |
| Retention - Global Unmanaged (R28D), % | `smb_unmanaged_retained_all` |

---

### Budget Utilization, % — and bid types

- **Owner:** Ads DS
- **Tabs:** GTM
- **Value:** **blank**
- **Color:** —
- **Actuals:** none. Intended table `daily_flight_exp_var_budget_delivery_metrics_lean` died **2026-06-02**
- **Goals:** —
- **Watch:** do not reload. It would print ~100% (capped budget falls back to revenue).

| Display | Intended column |
|---|---|
| Budget Utilization, % | `bu` |
| Budget Utilization - Bidless, % | `bidless_bu` |
| Budget Utilization - Manual Bidding, % | `manual_bidding_bu` |
| Budget Utilization - Maximize Volume, % | `maximize_volume_bu` |
| Budget Utilization - Target CPX, % | `target_cpx_bu` |

---

### % Booking to Quota

- **Owner:** RSO
- **Tabs:** GTM
- **Value:** as-of attainment. Comps are percentage points
- **Color:** booking-to-quota by week of quarter (55/50, 80/75, 95/90)
- **Actuals:** Closed Won from `daily_snapshot_sfdc_pipeline` (`stage` `6 - Closed Won` or legacy `7 - Closed Won`), current-quarter bookings (pre-2024-07-01 × 0.98) ÷ Strat Fin full-quarter quota from `daily_quota_profile` (nearest snapshot ≤ each booking date)
- **Goals:** no CQ dollar goal

---

## Ads Supply Drivers

### WAUq (QTD), # — and US / ROW

- **Owner:** Logan Wilson
- **Tabs:** Supply
- **Value:** quarter average
- **Color:** grey
- **Actuals:** `rddt-tier0-metrics1-prod.wauq.tier0_wauq_reporting` — `wauq`, `us_wauq`, `row_wauq`
- **Goals:** none
- **Watch:** as-of is the Data clock (WAUq’s ready date is an input to that MIN).

---

### DAUq (QTD), # — Total / US / ROW / App / Web / geo × surface

- **Owner:** Logan Wilson
- **Tabs:** Supply. Total / US / ROW also on [Company Level](#dauq-qtd--and-us--row)
- **Value:** quarter average
- **Color:** Total / US / ROW use Impressions / DAUq (98 / 96). App / Web grey (no goals)
- **Actuals:** same `baseline_canonical_cube`
- **Goals:** Total / US / ROW from the DAUq sheet. App / Web none

| Breakout | Notes |
|---|---|
| Total / US / ROW | same as Company Level |
| App | iOS / Android |
| Web | web / web3x / mweb3x |
| US App / US Web / ROW App / ROW Web | geo × surface |
| App + Web vs Total | can be less than Total when `primary_app` is Other |

---

### Monetizable Feed Post Views (R7D) and Monetizable PDP Screen Views (R7D)

- **Owner:** Ads DS
- **Tabs:** Supply
- **Value:** within-quarter average of today + 6 prior rows. Headline **value** = sum of the four children. Headline comps run on the US-logged-in series, then the value is overwritten with the sum
- **Color:** year-over-year sign
- **Actuals:** `reddit-ads-prod.ads_ds_metrics.ad_supply_key_metrics`
- **Goals:** none

| Display | Column |
|---|---|
| Monetizable Feed Post Views (R7D), # | sum of the four feed columns |
| Monetizable Feed - Logged In US (R7D), # | `monetizable_feed_post_us_logged_in` |
| Monetizable Feed - Logged Out US (R7D), # | `monetizable_feed_post_us_logged_out` |
| Monetizable Feed - Logged In ROW (R7D), # | `monetizable_feed_post_row_logged_in` |
| Monetizable Feed - Logged Out ROW (R7D), # | `monetizable_feed_post_row_logged_out` |
| Monetizable PDP Screen Views (R7D), # | sum of the four PDP columns |
| Monetizable PDP - Logged In US (R7D), # | `monetizable_pdp_us_logged_in` |
| Monetizable PDP - Logged Out US (R7D), # | `monetizable_pdp_us_logged_out` |
| Monetizable PDP - Logged In ROW (R7D), # | `monetizable_pdp_row_logged_in` |
| Monetizable PDP - Logged Out ROW (R7D), # | `monetizable_pdp_row_logged_out` |

---

### Ad Impressions (QTD), # — and US / ROW

See [Company Level](#ad-impressions-qtd--and-us--row).

---

## Appendix — GTM RFD child names

Same calc as the [KPI headlines](#reach--frequency--depth-kpi-headlines).

**Suffixes:** spend `under_50` / `50_200` / `200_1000` / `1000_plus` · lifecycle `_new` / `_retained` / `_resurrected` · channel `_channel_lcs` / `_mm` / `_smb` / `_unmanaged` / `_partnerships`

### Reach

| Display name | Column |
|---|---|
| Reach (QTD Advertisers) by Daily Spend Cohort, # | `rfd_reach` |
| Reach (QTD Advertisers) - <$50/day | `rfd_reach_spend_under_50` |
| Reach (QTD Advertisers) - <$50/day - Newly Activated | `rfd_reach_spend_under_50_new` |
| Reach (QTD Advertisers) - <$50/day - Rolling Active | `rfd_reach_spend_under_50_retained` |
| Reach (QTD Advertisers) - <$50/day - Reactivated | `rfd_reach_spend_under_50_resurrected` |
| Reach (QTD Advertisers) - $50-$200/day | `rfd_reach_spend_50_200` |
| Reach (QTD Advertisers) - $50-$200/day - Newly Activated | `rfd_reach_spend_50_200_new` |
| Reach (QTD Advertisers) - $50-$200/day - Rolling Active | `rfd_reach_spend_50_200_retained` |
| Reach (QTD Advertisers) - $50-$200/day - Reactivated | `rfd_reach_spend_50_200_resurrected` |
| Reach (QTD Advertisers) - $200-$1000/day | `rfd_reach_spend_200_1000` |
| Reach (QTD Advertisers) - $200-$1000/day - Newly Activated | `rfd_reach_spend_200_1000_new` |
| Reach (QTD Advertisers) - $200-$1000/day - Rolling Active | `rfd_reach_spend_200_1000_retained` |
| Reach (QTD Advertisers) - $200-$1000/day - Reactivated | `rfd_reach_spend_200_1000_resurrected` |
| Reach (QTD Advertisers) - $1000+/day | `rfd_reach_spend_1000_plus` |
| Reach (QTD Advertisers) - $1000+/day - Newly Activated | `rfd_reach_spend_1000_plus_new` |
| Reach (QTD Advertisers) - $1000+/day - Rolling Active | `rfd_reach_spend_1000_plus_retained` |
| Reach (QTD Advertisers) - $1000+/day - Reactivated | `rfd_reach_spend_1000_plus_resurrected` |
| Reach (QTD Advertisers) by Sales Channel, # | `rfd_reach` |
| Reach (QTD Advertisers) - LCS, # | `rfd_reach_channel_lcs` |
| Reach (QTD Advertisers) - MM, # | `rfd_reach_channel_mm` |
| Reach (QTD Advertisers) - SMB Managed, # | `rfd_reach_channel_smb` |
| Reach (QTD Advertisers) - SMB Unmanaged, # | `rfd_reach_channel_unmanaged` |
| Reach (QTD Advertisers) - Channel Partnerships, # | `rfd_reach_channel_partnerships` |

### Frequency

Same 23 names with prefix `Frequency (QTD Active Days / Advertiser)` and columns `rfd_frequency…` (same suffixes).

### Depth

Same 23 names with prefix `Depth (QTD Revenue / Active Day)` and unit `$`, columns `rfd_depth…`.
