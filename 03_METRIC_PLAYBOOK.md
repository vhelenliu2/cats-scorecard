# CATS Scorecard — Metric Playbook

**For:** manager review and whoever owns the published app after handover

**Dashboard:** [CATS Scorecard](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest)

**As of:** 8 September 2026

This is the **catalog of every live row**. For each metric it records owner, cadence, and the end-to-end path:

**warehouse (or sheet) → Hex intermediate frame → window / goal / color**

Calculation families **A / B / C** and the color rules live in [How the CATS Scorecard Calculates](02_HOW_THE_DASHBOARD_CALCULATES.md). This playbook names the family and only restates the math when a row differs.

A **copy** is the same object on a second tab — change it once. A **recompute** is a second metric with the same rules — change both Metrics cells.

---

## How to use this doc

1. Use the **index** to find the tab and section.
2. Read the **Pipeline** (raw → intermediate → Hex).
3. Read **On the table** (owner, cadence, goal, color, children).
4. If MoM / color disagree with another row, check the calculation doc §7 before treating it as a bug.
5. If every ads row looks a day (or more) behind, check the **Data clock** / freshness guard in the calculation doc §3 before assuming a metric broke.

Live row counts (section headers excluded): Company Level **27** · CATS SC/KPIs **32** · GTM **108** · Supply **25**. GTM is large because Reach / Frequency / Depth expand into 69 diagnostic children (appendix).

---

## Index

| Metric | Tab | Family | Intermediate frame |
|---|---|---|---|
| Ads Realized Revenue (QTD), $ | Company Level | A | `revenue_base_df` → `combined_df` |
| MAA (R28D), # + LCS / MM / SMB | Company Level; **copied** to KPI | B | `maa_df` → `combined_df` |
| DAUq (QTD), # + US / ROW | Company Level; Total/US/ROW **copied** to Supply | C | `dauq_counts_df` |
| Thriving Communities, # + region / tier | Company Level | C | `thriving_communities_df` |
| Ad Impressions (QTD), # + US / ROW | Company Level; **copied** to Supply | A | `impressions_region_df` |
| eCPM (QTD), $ + US / ROW | Company Level | A (ratio) | `impressions_region_df` + `delivered_realized_ratio_df` |
| C-performance A/B (CTR, kICR4, PiIR, VVR6, CPC, kCPA) | Company Level; KPI (names differ slightly) | monthly A/B | `cats_c_performance_ab_metrics_df` |
| Shopping ROAS A/B | Company Level; **copied** to KPI | quarterly A/B | `c_shopping_performance_ab_df` |
| Upper Funnel Revenue (QTD), $ | KPI | Brand feed | `upper_funnel_revenue_df` |
| Post-Install CPA A/B | KPI only | monthly A/B | `cats_c_performance_ab_metrics_df` |
| Shopping Revenue (QTD), $ | KPI; **recomputed** on GTM | A + weekly goal | `shopping_rev_df` |
| gROAS* (R28D) | KPI | latest R28 | `shopping_g_roas_df` |
| Overall Measured Revenue (QTD), $ | KPI; **recomputed** on GTM | A | `measured_revenue_daily` |
| High Quality Signal Adoption, % | KPI; **recomputed** on GTM | latest rate | `hq_signal_df` → `hq_signal_summary` |
| Revenue / Sales + Marketing FTE | KPI | LTM level | `rev_fte_revenue_df` + FTE pin → `rev_fte_actuals` |
| Reach / Frequency / Depth headlines | KPI | day-D snapshot | `rfd_cats_df` |
| Retention (R28D) - SMB, % | KPI | baked 28d | `retention28_df` |
| Scale (OE, Cloud, Model, Exp, SOTA) | KPI | each its own | `scale_*_actuals` pins |
| MixShift Key3 CPA / iCR | GTM | MixShift | `mixshift_metrics_df` → `mixshift_metric_quarter_df` |
| DPA ROAS* (R28D) | GTM | latest R28 | `shopping_g_roas_df` |
| CAPI adoption, credit lines, AT+DPA | GTM | point / QTD | own frames → `combined_df` |
| RFD diagnostics (69 children) | GTM | day-D snapshot | `rfd_cats_df` |
| New Advertisers Activated + channels | GTM | A (QTD sum) | `new_activations_bus_df` → `combined_df` |
| Retention R91 / R28 + channels | GTM | baked | `retention91_df` / `retention28_df` |
| Budget Utilization + bid types | GTM | **blank** | stale lean budget table — do not reload |
| % Booking to Quota | GTM | as-of % | `booking_quota_df` → `combined_df` |
| WAUq (QTD), # + US / ROW | Supply | C | `wauq_df` → `combined_df` |
| DAUq App / Web / geo × surface | Supply | C | `dauq_counts_df` |
| Monetizable Feed / PDP (R7D) | Supply | R7 average | `monetizable_feed_df` → `combined_df` |

---

## Company Level Goals

### Ads Realized Revenue (QTD), $

**Owner:** Bassem Haddad, Evie Sarkes · **Cadence:** daily

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_measures.direct_ads_revenue_by_sales_channel`. Qualifying ads realized revenue (exclude House Ads / internal in the ranked-category step).
2. **Intermediate.** Ranked category frame → `revenue_base_df` (daily `SUM(realized_revenue)`) → joined into `combined_df.realized_revenue`.
3. **Goals.** Same warehouse family: `daily_quota_profile` (latest snapshot in the last 30 days) → `revenue_quota_df` (`current_quarter_goal`, `qtd_goal`). FY is blank.
4. **Hex.** Family **A**. Status `goal_binary` (≥100% of QTD quota / else red).

---

### MAA (R28D), # — and LCS / MM / SMB

**Owner:** DS Ye Liu / Pengfei Qiao; RSO Paola Madueno. KPI overlay also lists Yoni Sauerbrun. · **Cadence:** daily actuals; goals = planning sheet

**Pipeline**

1. **Raw.** Three warehouse tables, one business per day:
   - Spine: `rddt-ds-data1-prod.ad__attributes.businesses_comprehensive` ∩ `reddit-marketing.facts.lifecycle_28d_ads_account_business_id` (not dormant).
   - Spend: `direct_ads_revenue_by_sales_channel` — at least one qualifying delivered-revenue day in `[dt−27, dt]`; no House Ads or internal rows in that window.
2. **Intermediate.** `maa_df` counts distinct businesses on each `dt` (total + as-was LCS / MM / SMB). Joined into `combined_df` as `maa_rolling_28d`, `maa_lcs_rolling_28d`, `maa_mm_rolling_28d`, `maa_smb_rolling_28d`.
3. **Goals.** [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc) → Daily Goals Allocation → `maa_goals_df`. Columns: `Overall`, `Global LCS`, `Global MM`, `Global SMB`. EOQ / as-of / 31 Dec lookups (not prorated).
4. **Hex.** Family **B**. Status `goal_binary`. KPI **copies** these four objects.

Children do not have their own registry ids.

---

### DAUq (QTD), # — and US / ROW

**Owner:** Logan Wilson · **Cadence:** daily cube; goals = planning sheet

**Pipeline**

1. **Raw.** `rddt-tier0-metrics1-prod.dauq.baseline_canonical_cube`, filter `is_dauq`, measure `SUM(n_users)`. Same definition as [Daily DAUq Report v2](https://app.hex.tech/reddit/app/Daily-DAUq-Report-v2-033JmYVBjqTdtm70mD94CP/latest) / Ecosystem Health.
2. **Intermediate.** `dauq_counts_df` — one row per day: `dauq`, `dauq_us` (geo US), `dauq_row` (everyone else, including unknown geo), plus App / Web / geo×surface (used on Supply). **As-of = cube max date**, not ads `latest_date`.
3. **Goals.** [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ) → Latest Forecast. Sheet stores **millions**; Hex stores users. **QTD goal = CQ** (a mean is not paced down).
4. **Hex.** Family **C**. Status `impressions_pacing` (98 / 96). Grey if the goal is missing. Supply **copies** Total / US / ROW.

Registry name is still `DAUq (QTD), M`. Hex display is `DAUq (QTD), #`. Always join on `metric_id` `MET-419D6C123B19`, never on the hashed display name.

---

### Thriving Communities, # — and US / ROW / Gold / Silver / Bronze

**Owner:** Ben Feinberg, Victor Ronda · **Cadence:** daily · **Goals:** none (by design)

**Pipeline**

1. **Raw.** `rddt-ds-data1-prod.subreddit__daily.thriving_communities_v2`.
2. **Intermediate.** `thriving_communities_df` — daily thriving counts by region and Gold / Silver / Bronze. As-of = series max date.
3. **Hex.** Family **C**, then rounded to an integer. Status `grey`. Region children have status display off.

---

### Ad Impressions (QTD), # — and US / ROW

**Owner:** DS Yoni Sauerbrun; Finance Yona Kuritzky · **Cadence:** daily actuals; goals = code each quarter

**Pipeline**

1. **Raw.** `direct_ads_revenue_by_sales_channel` (`impressions`, `location_country`). Internal accounts excluded.
2. **Intermediate.** `impressions_region_df` — daily impressions by US / ROW.
3. **Goals.** Hardcoded `IMPRESSIONS_GOALS` in the Company Level Metrics cell. Q3 2026: US 59.8B + ROW 57.9B. QTD = CQ × day-elapsed. Must be edited when the quarter rolls.
4. **Hex.** Family **A**. Status `impressions_pacing`. Supply **copies** parent and children.

---

### eCPM (QTD), $ — and US / ROW

**Owner:** same as Impressions · **Cadence:** daily

**Pipeline**

1. **Raw.** Same ads revenue table (realized revenue + impressions).
2. **Intermediate.** `impressions_region_df` for the two sums. `delivered_realized_ratio_df` (prior-quarter delivered ÷ realized) for the CQ goal.
3. **Hex.** Family **A** on the ratio `revenue / impressions × 1,000`. CQ goal (total only): revenue CQ × prior-Q delivered/realized ÷ impressions CQ × 1,000. QTD goal blank. US/ROW goals blank. Status `grey`.

---

### C-performance A/B (Company Level)

**Owner:** Christa Benton · **Cadence:** monthly actuals; goals = planning sheet

**Pipeline**

1. **Raw.** C-performance launch-tracker / A/B actuals sheet (monthly lift vs control).
2. **Intermediate.** `cats_c_performance_ab_metrics_df`. Goals: C-performance A/B goals sheet, through the Hex rename map, into the consolidator.
3. **Hex.** Value = **current calendar month**. QTD goal blank. Comps blank or percentage-point (calculation doc §4). Status `ab_goal`.

| Display name | Actuals / goals key | Direction |
|---|---|---|
| CTR A/B | CTR A/B | Higher better |
| kICR4 A/B | kICR4 A/B | Higher better |
| PiIR A/B | PiIR A/B | Higher better |
| VVR6 A/B | VVR6 A/B | Higher better |
| CPC A/B | CPC A/B | Lower better |
| kCPA A/B | kCPA4 A/B (display drops the 4) | Lower better |

Not on this tab: CPV6 A/B, Post-Install CPA (KPI only).

---

### Shopping ROAS A/B

**Owner:** Ryan Sekulic, Lillian Kravitz · **Cadence:** monthly / quarterly sheet

**Pipeline**

1. **Raw / intermediate.** `c_shopping_performance_ab_df` current quarter (`Shopping ROAS A/B`, `Shopping ROAS A/B Goal`). FY defaults to 0.60 if the sheet is quiet.
2. **Hex.** Current-quarter lift. Comps blank. Status `ab_goal`. KPI **copies** this object.

---

## CATS SC / KPIs

### Upper Funnel Revenue (QTD), $

**Owner:** Emily Glauser · **Cadence:** daily feed

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_metrics.brand_pillar_daily_comprehensive_summary`.`brand_revenue`. GLOBAL = all location types. Same logic as the [Brand Pillar](https://app.hex.tech/reddit/app/Brand-Pillar-Business-Overview-Dashboard-6mNDevMXkAFJjOGjuervnI/latest?tab=revenue_summary) revenue tab.
2. **Intermediate.** `upper_funnel_revenue_df` — one row: QTD / YTD sums, Brand-style MTD MoM, same-elapsed QoQ / YoY, plus CQ $310M and FY $1.1B.
3. **Hex.** Value and comps come from that feed (not recomputed as family A). QTD goal = CQ × CATS day-elapsed. Status `goal_rev_2m` ($2M yellow buffer).

`% of top 200 brand advertisers who adopt 3+ best practices` is **not** on this tab.

---

### Performance A/B (KPI)

Same monthly pipeline as Company Level. Comps **blank**. Display names differ slightly.

| Display name | Actuals col | Goals key | Direction |
|---|---|---|---|
| CTR A/B | CTR A/B | CTR A/B | Higher better |
| kiCR4 A/B | kICR4 A/B | kICR4 A/B | Higher better |
| PilR A/B | PiIR A/B | PiIR A/B | Higher better |
| CPC A/B | CPC A/B | CPC A/B | Lower better |
| kCPA A/B | kCPA4 A/B | kCPA4 A/B | Lower better |
| Post-Install CPA A/B | Post-Install CPA A/B | **CPA A/B** (different key) | Lower better |
| VVR6 A/B | VVR6 A/B | VVR6 A/B | Higher better (under Brand) |

---

### Shopping Revenue (QTD), $

**Owner:** Ryan Sekulic, Vinay Sridhar · **Cadence:** daily actuals; QTD goal = code

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_measures.aggregated_shopping_impressions` (Catalog Sales / DPA + custom product ads). Exclude listed internal ad accounts and `business_name = Reddit`. Optional CAPI flag from `capi_accounts_daily` is in the query; the published value is `SUM(revenue)`.
2. **Intermediate.** `shopping_rev_df` — daily `shopping_rev`.
3. **Hex.** Family **A** for the actual and R28 MoM. QoQ = same-elapsed QTD. YoY = YTD vs prior-year same calendar day. CQ $22M, FY $70M. **QTD goal is a hardcoded weekly paced target** ($5,614,458 as of this writing). Status `shopping_pace` (85 / 70). **Recomputed** on GTM — keep the weekly number in sync.

---

### gROAS* (R28D)

**Owner:** Ryan Sekulic · **Cadence:** daily · **Goals:** none

**Pipeline**

1. **Raw.** `aggregated_shopping_impressions` (pixel-enabled purchase value / ad views, geometric R28).
2. **Intermediate.** `shopping_g_roas_df`.`gROAS_s`.
3. **Hex.** Latest value on or before ads as-of. Comps not wired. Status `grey`. GTM DPA ROAS* uses the **same series** with a different status rule.

---

### Overall Measured Revenue (QTD), $

**Owner:** Anirudha Sundaresan · **Cadence:** daily component

**Pipeline**

1. **Raw / intermediate.** Hex component `measured_revenue_daily` (Measured Revenue project). Column `measured_revenue`.
2. **Hex.** Family **A** over CATS `latest_date`. CQ 2026: $200 / $350 / $450 / $500M. FY $1.5B. QTD = CQ × day-elapsed. Status `goal_rev_5m` ($5M yellow). **Recomputed** on GTM.

---

### High Quality Signal Adoption, %

**Owner:** Aayush Shah, Emre Enes Yavuz · **Cadence:** daily

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_measures.msmt_foundation_rolling_revenue` (28d / 90d conversion + catalog sales revenue, web-active MAAs, exclude CLICKS / UNKNOWN) **and** `rddt-ads-measurement1-prod.conversion_signals.conversion_signals_quality_score` (pixel overall score, integration ALL). An account is HQ only if **every** active optimization-goal event meets the threshold (0.6 for PageVisit / ViewContent, else 0.7) on a 28-day average score.
2. **Intermediate.** `hq_signal_df` — daily `hq_revenue_rate` = HQ 90d revenue ÷ eligible 90d revenue. Python `hq_signal_summary` takes the latest rate on or before ads as-of and pp deltas vs 1 / 3 / 12 months earlier.
3. **Hex.** Latest rate. CQ 45% / FY 50% reference. QTD blank. Status `grey` (rule pending). **Recomputed** on GTM.

---

### Revenue / Sales + Marketing FTE (LTM as of {month}), $

**Owner:** Aaron Nelson · **Cadence:** monthly (held until FTE lands)

**Pipeline**

1. **Raw.** Ads revenue: same table as Company Level (`direct_ads_revenue_by_sales_channel`) rolled to **completed months** → `rev_fte_revenue_df`. FTE: planning sheet pin `rev_fte_all_values` (billable Sales + Marketing).
2. **Intermediate.** `rev_fte_actuals` — LTM ads revenue ÷ average LTM billable FTE. **As-of = last month that has FTE** (do not mix a later partial revenue month with held-forward FTE).
3. **Hex.** Not family A/B/C. Comps = % change of that **level** vs 1 / 3 / 12 months earlier. CQ waypoints Q1–Q3 $3.07 / $3.2 / $3.4M. Q4 unset. FY $3.7M is a **level**. QTD goal = linear path from the prior waypoint. Status `goal_binary`.

---

### Reach / Frequency / Depth (KPI headlines)

**Owner:** Ye Liu, Dana Avgil · **Cadence:** daily snapshot · **Goals:** none

**Pipeline** — same as GTM diagnostics; this tab only shows the three totals.

1. **Raw.** `rddt-ds-data1-prod.sandbox.t_pillar_rfd_daily_v2`. Demand Health QTD mode: `window_label = QTD`, `revenue_basis = delivered`, `basis_used = as_was`, baked, Business ID. Channels: LCS, Mid-Market, SMB, Unmanaged, Partnerships (exclude Unknown / Other).
2. **Intermediate.** `rfd_cats_df`:
   - Reach = `SUM(advertisers)`
   - Frequency = `SUM(active_days) / SUM(advertisers)`
   - Depth = `SUM(window_revenue) / SUM(active_days)`
3. **Hex.** Value = snapshot on as-of. MoM blank. QoQ / YoY = same day-of-quarter. Status `grey`.

| Display name | Column |
|---|---|
| Reach (QTD Advertisers), # | `rfd_reach` |
| Frequency (QTD Active Days / Advertiser), # | `rfd_frequency` |
| Depth (QTD Revenue / Active Day), $ | `rfd_depth` |

---

### Retention (R28D) - SMB, %

**Owner:** Ye Liu · **Cadence:** daily with a **28-day bake**

**Pipeline**

1. **Raw.** `direct_ads_revenue_by_sales_channel`. Qualifying delivered spend; grain `ads_account_business_id`. Business Lifecycle `28baseline_0gap_28comparison`: share of businesses active in the trailing 28d baseline that return with spend in the next 28d.
2. **Intermediate.** `retention28_df`.`smb_combined_retained_all` (SMB Managed + Unmanaged).
3. **Hex.** `build_baked_retention_metric` — as-of is 28 days behind ads `latest_date`. Comps = percentage points. Status `grey`. Matches GTM “Global SMB (Managed + Unmanaged)”.

---

### Scale Our Foundations

**Owner:** Virgilio Pigliucci · **Cadence:** monthly (month-end pins) · Not family A/B/C

**Pipeline (all five).** Planning / Manager Dashboard / launch-tracker Google Sheets are pinned into Hex (`scale_*_all_values`). Python cells produce `scale_oe_actuals`, `scale_cloud_actuals`, `scale_ml_actuals`, `scale_exp_actuals`, `scale_sota_actuals`. If a pin fails, the row can sit on a pillar checksum without looking broken.

| Display name | What the pin computes | Goal / pacing | Status |
|---|---|---|---|
| Operational Excellence (as of {month}), sum | Unweighted **sum** of Manager Dashboard team scores at month-end (a level) | CQ +5%, FY +40%. QTD rate = +5% × completed months / 3. **Pacing = QoQ ÷ that rate** | `goal_binary` |
| Cloud Savings (YTD as of {month}), $ | Tracker C1 **YTD** COR savings; else pillar Q3 YTD $9.2M | FY $10M. QTD bar = FY × completed months / 12. CQ blank. QoQ uses hardcoded Q1 $0.34M / Q2 $5.7M | `goal_binary` |
| Model Velocity (QTD as of {month}), # | QTD count of Ranking + Retrieval + Shopping launches with KPI movement (exclude bugs / deprecations / backtests / 0). Q2 checksum 23 | FY +25% YoY. QTD = last-year same-elapsed × 1.25 | `goal_binary` |
| Experimentation Velocity (QTD as of {month}), # | QTD distinct qualifying Ads experiments. Insights app is unread; pillar checksums until SQL is granted. Links to [Ads Experimentation Insights](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) | FY +33% YoY. QTD = last-year same-elapsed × 1.33 | `goal_binary` |
| Ads SOTA ML (as of {month}) | Subjective grade from the Scale pillar table | Path C- (Jan) → C (Q2) → B- (Q3) → B (Dec) | `goal_binary` |

Do not reuse retired registry names Marketplace Efficiency or Ads Tier0 Availability for Model Velocity or SOTA.

---

## Ads Product & GTM

### Same-Store MixShift Key3 CPA / iCR (QoQ), %

**Owner:** Emre Enes Yavuz · **Cadence:** monthly (last complete month) · **Goals:** none

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_metrics.e2e_performance`. Key3 = `objective_type = CONVERSIONS` and `optimization_goal IN (LEAD, SIGN_UP, PURCHASE)`. Same-store: advertisers in both periods. 7-day bake. Aligned with E2E Performance “Conversions QTD Overall”.
2. **Intermediate.** `mixshift_metrics_df` (daily / weekly advertiser rates) → `mixshift_metrics_comp_df` → `mixshift_metric_quarter_df` (QoQ and YoY MixShift). Headline fields: weighted log-geo change CPA and iCR.
3. **Hex.** **Value is the QoQ MixShift.** MoM not defined. YoY = YoY MixShift. Status `yoy`. CPA is lower-is-better; iCR is higher-is-better.

---

### DPA ROAS* (R28D)

**Owner:** Ryan Sekulic · **Cadence:** daily

**Pipeline.** Same raw table and `shopping_g_roas_df.gROAS_s` as KPI gROAS*. Hex uses `generate_metric` point comparisons. Optional lower bound `gROAS_s_pi_lo`. Status `lower_bounded_goal` when a bound exists (KPI gROAS* is grey / no comps).

---

### Revenue-Weighted CAPI Adoption - LCS + MM, %

**Owner:** BA · **Cadence:** daily · **Goals:** none

**Pipeline**

1. **Raw.** `msmt_foundation_rolling_revenue`. Eligible MAAs: 28d conversion/catalog revenue > 0, web-active, objectives CONVERSIONS / CATALOG_SALES, optimization not CLICKS / UNKNOWN. CAPI adopter = `is_web_capi_active_28d`. Channels LCS + MM only.
2. **Intermediate.** `capi_covered_shopping_df`.`perc_capi_shop_rev` = 90d revenue of CAPI-active MAAs ÷ 90d revenue of eligible MAAs. Joined into `combined_df`.
3. **Hex.** Point comparison; comps = percentage points. Status `grey`.

---

### # Credit Line Setups - Global LCS + Global MM (QTD)

**Owner:** Ads DS · **Cadence:** daily · **Goals:** none

**Pipeline**

1. **Raw.** `reddit-ads-prod.business_analytics_prod.credit_line_setups` (distinct `funding_instrument_id`).
2. **Intermediate.** `credit_lines_setup_df`.`cl_setup_num` — QTD cumulative → `combined_df`.
3. **Hex.** Point / QTD cumulative. Status grey; **status display off**.

---

### % of Lower Funnel Revenue Using Automated Targeting + DPA (R7D)

**Owner:** Ads DS · **Cadence:** daily (7-day window) · **Goals:** none

**Pipeline**

1. **Raw.** `reddit-ads-prod.business_analytics_prod.product_adoption_revenue`. Upstream `del_automated_targeting_revenue` = delivered revenue where expansion **or** DPA (already a union — do not add DPA again).
2. **Intermediate.** `lower_funnel_at_dpa_df` — within-quarter rolling 7 days (current + 6 prior rows) of lower-funnel AT-or-DPA revenue ÷ lower-funnel delivered revenue → `combined_df.lower_funnel_rev_at_dpa_perc`.
3. **Hex.** Point comparison; comps = percentage points. Status grey; **status display off**.

---

### Shopping Revenue, Measured Revenue, HQ Signal (GTM)

Same pipelines as the KPI cards. These three are **recomputed** here, not copies. Shopping weekly QTD goal must stay in sync with KPI.

---

### Reach / Frequency / Depth diagnostics (GTM)

Same pipeline as the KPI headlines (`t_pillar_rfd_daily_v2` → `rfd_cats_df`). GTM adds two trees per family:

- **by Daily Spend Cohort** — parent + 4 tiers + 3 lifecycles under each tier
- **by Sales Channel** — parent + 5 channels

Spend tiers: `<$50/day`, `$50-$200/day`, `$200-$1000/day`, `$1000+/day`.  
Lifecycles: Newly Activated, Rolling Active, Reactivated.  
Channels: LCS, MM, SMB Managed, SMB Unmanaged, Channel Partnerships.

Owner, cadence, calc, and status are identical to the headlines (Ye Liu / Dana Avgil; daily snapshot; day-D; grey). Every display name and column is in the appendix.

---

### New Advertisers Activated (QTD), # — and channels

**Owner:** Ads DS · **Cadence:** daily · **Goals:** none

**Pipeline**

1. **Raw.** `direct_ads_revenue_by_sales_channel`. Activation = first day with qualifying delivered spend (`delivered_revenue > 0`, exclude House Ads / internal) at `ads_account_business_id`. Channel = as-was primary on that day.
2. **Intermediate.** `new_activations_bus_df` — daily first-spend counts → `combined_df` as `total_activations_sum`, `global_lcs_activations_sum`, `global_mm_activations_sum`, `global_smb_activations_sum` (Managed), `global_unmanaged_smb_activations_sum`.
3. **Hex.** Family **A** (QTD sum, R28 MoM, same-elapsed QoQ/YoY). Status `yoy`.

| Display name | Column |
|---|---|
| New Advertisers Activated (QTD), # | `total_activations_sum` |
| New Advertisers Activated - Global LCS (QTD), # | `global_lcs_activations_sum` |
| New Advertisers Activated - Global MM (QTD), # | `global_mm_activations_sum` |
| New Advertisers Activated - Global SMB (QTD), # | `global_smb_activations_sum` |
| New Advertisers Activated - Global Unmanaged (QTD), # | `global_unmanaged_smb_activations_sum` |

---

### Retention (R91D) and Retention (R28D)

**Owner:** Ads DS · **Goals:** none

**Pipeline.** Same ads-revenue spine as KPI SMB retention.

- **R91.** `retention91_df`. Business Lifecycle `91baseline_0gap_91comparison`. Headline population = LCS + MM + SMB Managed. **91-day bake**.
- **R28.** `retention28_df`. `28baseline_0gap_28comparison`. Headline = SMB Managed + Unmanaged. **28-day bake**.

Hex: `build_baked_retention_metric`. Comps = percentage points. Status `grey`.

| Display name | Frame.column |
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

**Owner:** Ads DS · **All values None**

Intended pipeline (do **not** turn back on): `daily_flight_exp_var_budget_delivery_metrics_lean` → `campaign_budgets_df` → `budget_utilization_df` / bid-strategy frame. Formula: QTD spend ÷ QTD budget.

The lean table’s max `dt` is **2026-06-02**. Reloading it would print ~100% (capped budget falls back to revenue). Rows stay blank until a new source exists.

| Display name | Intended column |
|---|---|
| Budget Utilization, % | `bu` |
| Budget Utilization - Bidless, % | `bidless_bu` |
| Budget Utilization - Manual Bidding, % | `manual_bidding_bu` |
| Budget Utilization - Maximize Volume, % | `maximize_volume_bu` |
| Budget Utilization - Target CPX, % | `target_cpx_bu` |

---

### % Booking to Quota

**Owner:** RSO · **Cadence:** daily

**Pipeline**

1. **Raw.** Numerator: `daily_snapshot_sfdc_pipeline` Closed Won (`stage` `6 - Closed Won` or legacy `7 - Closed Won`), current-quarter bookings. Pre-2024-07-01 rows × 0.98. Denominator: Strat Fin full-quarter quota from `daily_quota_profile` (nearest snapshot ≤ each booking date).
2. **Intermediate.** `booking_quota_df` → `combined_df.overall_quota_perc`.
3. **Hex.** As-of attainment. Comps = percentage points. Status `booking_quota` (week 1 ≥55/50, week 4 ≥80/75, week 8 ≥95/90). No CQ dollar goal.

---

## Ads Supply Drivers

### WAUq (QTD), # — and US / ROW

**Owner:** Logan Wilson · **Cadence:** daily · **Goals:** none

**Pipeline**

1. **Raw.** `rddt-tier0-metrics1-prod.wauq.tier0_wauq_reporting`.
2. **Intermediate.** `wauq_df` → `combined_df` as `wauq`, `us_wauq`, `row_wauq`. As-of = series max date.
3. **Hex.** Family **C**. Status `grey`.

---

### DAUq (QTD), # — Total / US / ROW / App / Web / geo × surface

**Owner:** Logan Wilson · **Cadence:** daily cube

**Pipeline.** Same `baseline_canonical_cube` → `dauq_counts_df` as Company Level.

- Total / US / ROW: **copied** from Company Level (goals + `impressions_pacing`).
- App / Web / US App / US Web / ROW App / ROW Web: built here from `dauq_app`, `dauq_web`, `dauq_us_app`, `dauq_us_web`, `dauq_row_app`, `dauq_row_web`. App = iOS / Android. Web = web / web3x / mweb3x. App + Web can be less than Total when `primary_app` is Other. **No goals.** Status `grey`.

---

### Monetizable Feed Post Views (R7D) and Monetizable PDP Screen Views (R7D)

**Owner:** Ads DS · **Cadence:** daily (7-day window) · **Goals:** none

**Pipeline**

1. **Raw.** `reddit-ads-prod.ads_ds_metrics.ad_supply_key_metrics` (`monetizable_feed_post_views`, `monetizable_pdp_screenviews`), split US/ROW × logged-in/out.
2. **Intermediate.** `monetizable_feed_raw_df` → `monetizable_feed_df` (within-quarter average of today + 6 prior rows) → `combined_df`.
3. **Hex.** Each child is that R7D average. Headline **value** is the **sum of the four children**. Status `yoy`. Headline comps are computed on the US-logged-in series, then the value is overwritten with the sum.

| Display name | Column |
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

**Copy** of Company Level (same `impressions_region_df`, same hardcoded CQ, same family A / `impressions_pacing`).

---

## Appendix — GTM RFD child names

Same calc as the KPI headlines. Suffixes: spend `under_50` / `50_200` / `200_1000` / `1000_plus`; lifecycle `_new` / `_retained` / `_resurrected`; channel `_channel_lcs` / `_mm` / `_smb` / `_unmanaged` / `_partnerships`.

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
