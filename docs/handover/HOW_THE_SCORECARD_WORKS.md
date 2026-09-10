# How the CATS Scorecard works

**As of:** 10 September 2026

The scorecard is a Hex app. It rebuilds every morning at **9:00 AM Chicago time**.

- **Most rows** come from the warehouse and refresh with the morning run.
- **A few rows** sit on a monthly sheet or a goal stored in the notebook. Those need extra checks after the run.

Use the jump list. You do not have to read this in order.

> Need one metric’s owner or source table? Open the [playbook](METRIC_PLAYBOOK.md) and search the [list](METRIC_PLAYBOOK.md#list-of-metrics).

---

## Jump to

| If you need… | Go here |
|---|---|
| To confirm Scale, Rev/FTE, A/B, or a goal | [How to refresh the numbers](#how-to-refresh-the-numbers) |
| To know whether something odd is intentional | [Choices we made on purpose](#choices-we-made-on-purpose) |
| Extra care: Scale, Rev/FTE, A/B, typed-in goals, Budget | [Rows that need extra care](#rows-that-need-extra-care) |
| Clock, percent-change windows, colors | [How the numbers are calculated](#how-the-numbers-are-calculated) |
| A cell looks stale, grey, zero, or the two tabs disagree | [When a number looks wrong](#when-a-number-looks-wrong) |

**Links**

- [Draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae)
- [Published](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest)
- [Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc/edit?gid=1774082212#gid=1774082212)
- [Automation plan](https://docs.google.com/document/d/1kBjrbheugF0CO_VRm-h6XLwKrzjNqjT4wfpLCkTUke8/edit?tab=t.0)

---

## Choices we made on purpose

These will look surprising in review. They are **intentional**.

### Choice: we wait for every daily source

The app prints one date: the latest day that **all** daily tables can support.

- Not “today.”
- Not “the last ads-revenue day.”
- If shopping or the DAUq cube is a day behind, the **whole** scorecard moves back.

That way a quarter-to-date sum never mixes a complete day with a missing one.

### Scale updates once a month

Pillar teams write actuals into Google Sheets at month-end.

- In **September** you will still see **July** on Operational Excellence.
- That is a **one-month lag**, not a broken refresh.

### Revenue per FTE is also monthly

Last-twelve-months ads revenue ÷ average billable Sales + Marketing headcount.

- Recalculating every day is expensive and does not change the story.
- We pin it to the **last month that has headcount**.

### Zero and missing are different

| What you see | What it means |
|---|---|
| `0`, `$0`, `0%` | The metric **really was zero** |
| `—` (a dash) | We **do not have** the data |

> If a failed pull shows `0`, that is a **bug**. It will look like the metric landed at zero.

### Same A/B metric → same value

The two tabs do **not** have to show the same A/B rows.

- Company Level has the Tier 2 set (CTR, kICR4, PiIR, VVR6, CPC, kCPA, Shopping ROAS)
- KPI adds **Post-Install CPA** and may keep its own labels (`kiCR4`, `PilR`)

If both tabs show the **same underlying metric**, they show the same **Value**, CQ / FY goals, and status. Labels may differ (`kiCR4` / `kICR4`, `PilR` / `PiIR`). **Post-Install CPA** is on KPI only.

**A/B color** (same rule on both tabs):

- **Quarter goal already hit** → green, any month
- **Last month of the quarter** (last 15 days) → green ≥95% of CQ, yellow 70–95%, red <70%
- **Earlier in the quarter** → grey — too early to call

We do **not** pace A/B against a day-elapsed QTD goal. Status uses the **full-quarter** goal.

### Budget Utilization is empty on purpose

- The old table stopped on **2 June 2026**.
- Turning it back on would print about **100%** utilization, which is misleading.
- **Leave it blank** until there is a new source.

### Other things that look wrong and are not

- **Scale “quarter-over-quarter”** = this month vs the last month of last quarter (July vs June) — not the same number of days into last quarter.
- **A/B grey** early in the quarter is the status rule, not a missing goal — unless the quarter goal is already hit (then it is green).
- **Retention** and **MixShift** sit behind the Data clock because they wait for a bake or a finished month.

---

## How to refresh the numbers

### Daily path (most of the dashboard)

1. Let the **9:00 AM Chicago** run finish.
2. Read the **Data clock** line on the app.
3. If you only changed a label or a small Python cell, run **that cell** and the **table under it**.

You do **not** need to rerun the whole notebook.

### These need extra checks

Warehouse rows refresh with the 9:00 run. Confirm these next — they sit on a monthly sheet, a quarter roll, or a goal in the notebook.

| What | Confirm | Then run | Looks right when |
|---|---|---|---|
| **Scale** (five rows) | The pillar sheet has the new month | The Scale sheet cells, then the KPI metrics cell and its table | The “as of” month moved. A known checksum means the pin failed — not a new month |
| **Rev/FTE** | The headcount pin has the new month | KPI metrics cell and its table | The date is the last month with headcount. Do not pair later partial revenue with last month’s headcount |
| **A/B** | The sheet has this month (or this quarter). If a label changed, update the Hex name map and the tracker name together | The A/B sheet cells, then **both** Company Level and KPI metrics + tables | Same metric, same value on both tabs. Watch `Price: Post-Install CPA` (goals key is `CPA A/B`) |
| **MAA / DAUq goals** | MAB Daily Goals Allocation and DAUq Latest Forecast are on the new quarter | Those sheet cells, then Company Level metrics + table | The goal column matches the sheet. The DAUq sheet is in **millions**; Hex stores **users** |
| **Goals in the notebook** | The metrics cell has the new quarter / weekly / waypoint | Edit that cell, then its table (and GTM if the playbook says the row is rebuilt) | The goal column changed. Editing the tracker sheet does **not** move the app |
| **Budget** | No replacement source yet | — | Leave empty. Do not reload the June table |

### Goals that live in the notebook

Hex does **not** read these from a sheet. You edit the metrics cell:

- Impressions
- Shopping’s weekly quarter-to-date target
- Measured Revenue’s quarterly steps — $200 / $350 / $450 / $500M
- Upper Funnel — $310M / $1.1B
- Rev/FTE’s fourth-quarter waypoint *(not set)*
- Scale’s fallback checksums

### After the morning run — check these

- [ ] Data clock looks right
- [ ] Scale and Rev/FTE show a **finished month**
- [ ] `0` means zero; a dash means missing
- [ ] The same metric on two tabs **matches**

---

## Rows that need extra care

These can look fine after a clean morning run and still be stale.

- **Formulas** → [playbook](METRIC_PLAYBOOK.md)
- **How to pull them** → [How to refresh](#how-to-refresh-the-numbers)

**Jump:** [Scale](#scale) · [Rev/FTE](#revfte) · [A/B](#ab-lifts) · [Goals in code](#goals-we-typed-in-code) · [Quarter sheets](#sheets-that-need-a-quarter-roll) · [Budget](#budget-utilization)

### Scale

- **Owner:** Virgilio Pigliucci
- **Rows:** Operational Excellence, Cloud Savings, Model Velocity, Experimentation Velocity, Ads SOTA ML
- **Source:** pillar Google Sheets → Hex **pins**
- **Watch for:** a new month on the sheet *and* a successful pin. A failed pin can sit on a saved **checksum** and the row still looks healthy
- **QoQ:** this month-end vs the last month of last quarter — not the same-elapsed quarter-to-date we use for revenue

### Rev/FTE

- **Owner:** Aaron Nelson
- **What it is:** ads revenue (finished months only) ÷ average last-twelve-months billable Sales + Marketing headcount
- **Waypoints:** $3.07M / $3.2M / $3.4M for the first three quarters
- **Q4:** not set
- **FY $3.7M:** a **level**, not the sum of four quarters

### A/B lifts

- **Owner:** Christa Benton
- **What the Value is:** this **calendar month’s** lift versus control, from the launch-tracker sheet. The sheet has one number per month. Hex does **not** add those months up, and it does **not** average them.
- **What the goal is:** the **quarter** target on that same sheet. Color compares this month’s lift to that full-quarter goal — not to a day-elapsed QTD bar. See [A/B color](#same-ab-metric--same-value).
- **Watch for:** Hex maps sheet labels to scorecard names. A missed rename leaves the goal **blank** and nothing alarms
- **Same metric → same value:** CTR, conversion-rate lift, install-rate lift, VVR6, CPC, kCPA, Shopping ROAS. Labels may differ (`kiCR4` / `kICR4`, `PilR` / `PiIR`)
- **KPI-only:** Post-Install CPA (goals key is `CPA A/B` — the rename that breaks most often)
- **Shopping ROAS A/B** is the same color rule, but its sheet is one row per **quarter**, so Value is this quarter’s lift — not a monthly one. That is a different row from [Shopping Revenue](#rows-that-do-not-follow-these).

### Goals we typed in code

Editing the tracker sheet does **nothing** to these. You edit the metrics cell:

- Impressions
- Shopping quarter-to-date
- Measured Revenue
- Upper Funnel
- HQ *(reference only)*
- Rev/FTE waypoints
- Scale checksums

### Sheets that need a quarter roll

- MAB (MAA goals)
- DAUq Latest Forecast
- A/B goals

> If the sheet is not rolled for the new quarter, Hex keeps the last row on or before the date — **last quarter’s target can look current**.

### Budget Utilization

- **Empty**
- Source table died on **2 June 2026**

We started a small ingest helper for MAA and DAUq **goals** only. It does not pull Scale yet. Longer plan: [automation Doc](https://docs.google.com/document/d/1kBjrbheugF0CO_VRm-h6XLwKrzjNqjT4wfpLCkTUke8/edit?tab=t.0).

---

## How the numbers are calculated

**Jump:** [Data clock](#data-clock) · [Percent change](#how-percent-change-is-calculated) · [How the value is built](#how-the-value-is-built) · [Colors](#status-colors) · [Exceptions](#rows-that-do-not-follow-these)

Almost every row is:

1. Take a source
2. Build a daily series in Hex
3. Pick a window
4. Look up a goal
5. Paint a color

Most rows read their **own** source so a late series cannot slide another metric’s date.

> The old `combined_df` calendar join is **gone**. Company Level uses `revenue_base_df` / `maa_df`, GTM uses its own frames (activations, booking, credit lines, AT+DPA), Supply uses `wauq_df` / `monetizable_feed_df`. Do not add a new row through a wide join.

### Data clock

```
latest date = the earliest “ready” day among ads, DAUq, and WAUq
```

- The ads side already takes the earliest ready day among its own tables (revenue, brand, thriving, shopping, and so on).
- DAUq and WAUq sit on other warehouse connections, so they have their own checks.
- **“Days into the quarter”** uses this guarded date, not the calendar.

If a freshness query comes back empty, Hex warns and falls back. Treat that as a **clock problem**, not a metric change.

Some rows then apply a **tighter window** on top of that date — that is **not** a second clock:

- **Retention** waits 28 or 91 days
- **Scale** and **Rev/FTE** use the last finished planning month
- **MixShift** uses the last finished month and a 7-day bake

| Source | We treat it as ready when |
|---|---|
| Ads realized revenue | Latest day with non-zero revenue |
| Brand pillar | Latest day with non-zero brand revenue |
| Thriving communities | Latest day with thriving > 0 |
| Monetizable feed | Latest day with feed views > 0 |
| Product adoption revenue | Latest day with delivered revenue ≠ 0 |
| Shopping impressions, rolling revenue, HQ scores, RFD, E2E | Latest date folder that has rows |
| DAUq cube | Latest day in the last two weeks with DAUq users > 0 |
| WAUq reporting | Latest day in the last two weeks with WAUq > 0 |

### How percent change is calculated

For most rows:

> **(this window − last window) ÷ last window**

- **As-of** is the [Data clock](#data-clock), not today
- If either side is missing, or last window is zero → **leave the cell empty**
- Do **not** write `0`

**Windows**

- **MoM** (quarter sums and averages): trailing **28 days** vs the **28 days before that**
- **QoQ / YoY** (quarter sums and averages): this quarter-to-date vs the **same number of days** into the last quarter / last year
- **MAA** (a rolling 28-day level): the stock on as-of vs that stock **28 / 91 / 365 days** earlier. It is already a rolling count, so we compare two snapshots — we do not sum or average a window, and we do not use same-elapsed QTD.

**A/B lifts** stay **blank** on comps. A change in lifts, if we ever show one, is subtraction (percentage points), not a ratio.

### How the value is built

Most daily rows do one of these three things. The rest are [below](#rows-that-do-not-follow-these).

**Add up the quarter** — ads revenue, impressions, Measured Revenue; Shopping’s *actual*

- **Value** = sum, quarter start through as-of
- **MoM / QoQ / YoY** = [windows](#how-percent-change-is-calculated) on those sums
- **In-quarter goal** = full-quarter goal × days elapsed ÷ days in the quarter

**A rolling 28-day level** — MAA and its LCS / MM / SMB breakouts

- **Value** = the stock on as-of
- **MoM / QoQ / YoY** = [windows](#how-percent-change-is-calculated)
- **Goals** come from the MAB sheet for that date — we do **not** scale them by days elapsed
- **Green** at 100% of that goal

**Average the quarter** — DAUq, Thriving, WAUq

- **Value** = mean of the daily series, quarter start through as-of
- **MoM / QoQ / YoY** = [windows](#how-percent-change-is-calculated) on those means
- **DAUq’s in-quarter goal is the full-quarter goal** — an average is not paced down by days elapsed

**eCPM** = revenue ÷ impressions × 1,000.

- Has a quarter goal (total only) from last quarter’s delivered-to-realized mix
- The in-quarter goal is blank and the status stays **grey**

### Status colors

**Pacing** = value ÷ in-quarter goal. No in-quarter goal → **grey**, never `0%`.

Hex picks a color from the row’s **status strategy** (`status_goal`). Live tabs use these:

| Metrics | Strategy | Green | Yellow | Else |
|---|---|---|---|---|
| Ads realized revenue; MAA (+ LCS / MM / SMB); Rev/FTE; Scale | `goal_binary` | ≥100% of the QTD (or Scale pacing) bar | — | below |
| Impressions; DAUq total / US / ROW | `impressions_pacing` | ≥98% | 96–98% | <96% |
| Upper Funnel | `goal_rev_2m` | ≥99.5% | another $2M would hit | else |
| Measured Revenue | `goal_rev_5m` | ≥99.5% | another $5M would hit | else |
| Shopping Revenue | `shopping_pace` | ≥85% of the weekly target | 70–85% | <70% |
| A/B (both tabs) | `ab_goal` | CQ already hit, or last 15 days of the quarter and ≥95% | last 15 days, 70–95% | last 15 days <70%; **earlier = grey** |
| MixShift iCR; New advertisers; Monetizable feed / PDP | `yoy` | YoY moving the right way (0.5% buffer) | — | else |
| Booking to Quota | `booking_quota` | Week of quarter 55% / 80% / 95% | 50 / 75 / 90 | else |
| DPA ROAS* | `lower_bounded_goal` | At or above the bound | — | below |
| eCPM; Thriving; WAUq; RFD; Retention; HQ Signal; CAPI; credit lines; AT+DPA; gROAS*; Budget; DAUq app / web breakouts | `grey` | — | — | always grey |

**Lower is better** (flips the “right way”): CPC, kCPA, Post-Install CPA, MixShift CPA.

Scale still uses `goal_binary`, but each row’s bar is its own pacing rule — see [Scale](#scale).

### Rows that do not follow these

| Row | What’s different |
|---|---|
| **Scale** | Monthly sheets. Each row has its own shape (a level, a year-to-date, a count, or a grade). OE “QoQ” = this month-end vs the last month of last quarter. See [Scale](#scale) |
| **Rev/FTE** | Monthly last-twelve-months level. MoM / QoQ / YoY = that level vs **1 / 3 / 12 months** earlier. See [Rev/FTE](#revfte) |
| **Shopping Revenue** | The dollar **actual** does add up the quarter (R28 MoM, same-elapsed QoQ). Two things do not: **YoY** is year-to-date vs the same calendar day last year, and the in-quarter **goal** is a weekly target we typed in — not CQ × days elapsed. This is **not** the Shopping ROAS A/B row. |
| **A/B lifts** | Value is this **month’s** lift from the tracker (one number per calendar month — we do not sum or average the quarter). MoM / QoQ / YoY stay **blank**. The **goal** is still the quarter target; color compares this month’s lift to that full-quarter goal (green if already hit; last month 95 / 70; otherwise grey). **Shopping ROAS A/B** uses the same color rule, but its sheet is one row per quarter. See [A/B](#ab-lifts) |
| **Reach / Frequency / Depth** | Snapshot on as-of. **MoM blank.** QoQ / YoY = same day-of-quarter in the prior quarter / prior year |
| **Retention** | Share still active after a 28- or 91-day wait. Comps are **percentage points** vs 1 / 3 / 12 months earlier (on the baked as-of) |
| **MixShift** | The value *is* the quarter-over-quarter MixShift (last finished month, 7-day bake, advertisers in both periods). MoM not defined |
| **HQ Signal** | Latest rate. 45% / 50% are reference only. Status grey |
| **Budget** | Empty. See [Budget](#budget-utilization) |
| **gROAS*** | Latest 28-day geometric ROAS. No official target. The GTM DPA ROAS* row can show a lower-bound status |

---

## When a number looks wrong

| What went wrong | What you will see |
|---|---|
| A daily source is late | The Data clock moves back. The 9:00 run can still succeed |
| Google Sheets is down | MAA, DAUq, A/B, or Scale goals go grey, or we keep the last successful pull |
| A planning-sheet row was renamed | A/B goals vanish. `Price: Post-Install CPA` is the usual miss |
| The quarter sheet was not rolled | Last quarter’s target, looking current |
| A typed-in goal was not updated | Impressions, Shopping weekly, Measured, Scale checksums, Rev/FTE Q4 |
| A Scale pin failed | A checksum. The row looks fine |

**Then ask:**

1. Is this a [quarter sum, a 28-day level, or a quarter average](#how-the-value-is-built) — or an [exception](#rows-that-do-not-follow-these)?
2. Should the date be the Data clock, or a finished month?
3. Is the goal from a sheet, from days elapsed, or from a number in the code?
4. If two tabs show the **same metric** (even under a slightly different label), the **value** must match.
