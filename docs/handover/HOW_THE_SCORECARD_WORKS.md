# How the CATS Scorecard works

**As of:** 14 September 2026

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

### Choice: one broken table does not freeze the whole scorecard

The app prints one **Data clock** date (`latest_date`). It is **not** today and it is **not** “whatever ads revenue landed last.”

A source that is a day or two behind no longer pulls every row back. Instead:

- Sources within **3 days** of the freshest table stay **on the clock** and set `latest_date`.
- A source **more than 3 days** behind goes **off the clock** — only its own metrics blank (`—`), with an orange banner on the tab.

QTD math still uses one shared `latest_date` so rows on the clock never mix a full day with a gap.

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

### A/B color

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
| **A/B** | The sheet has this month (or this quarter). If a label changed, add the alias in Hex **Canonical Metric Map** and align the launch tracker column name | Run **C performance goals ab gsheet** → **C performance goals ad df with cpv**, then the affected **Metrics** → **Table** cells | Goals and values look current. Watch `Price: Post-Install CPA` → key `Post-Install CPA A/B` |
| **MAA / DAUq goals** | MAB Daily Goals Allocation and DAUq Latest Forecast are on the new quarter | Those sheet cells, then Company Level metrics + table | The goal column matches the sheet. The DAUq sheet is in **millions**; Hex stores **users** |
| **Sheet-backed KPI goals** | Roadmap KPIs, pacing sheet, brand feed, Rev/FTE sheet updated | Run goals chain → KPI Metrics → Table at quarter roll (9:00 run handles daily) | Goal columns match sheets |
| **Notebook constants only** | Impressions, HQ, Scale fallbacks, `_EXP_COUNTS`, `_SOTA_BY_Q` | Edit the named cell, then its table | Goal column changed |
| **Budget** | No replacement source yet | — | Leave empty. Do not reload the June table |

### Goals that auto-pull from sheets (9:00 run)

- **Shopping Revenue** — CQ/FY from Roadmap `KPIs` tab; paced QTD from the shopping pacing sheet (column AO, current week)
- **Overall Measured Revenue** — quarterly steps + FY from Roadmap `KPIs` tab
- **Upper Funnel Revenue** — brand pillar feed (`upper_funnel_revenue_df`)
- **Rev/FTE** — LTM waypoints from the Rev/FTE planning sheet
- **A/B lifts** — Roadmap `KPIs` tab (same chain as Company Level)
- **Scale** — linear pacing in `Scale foundations actuals` from roadmap rates + sheet/SQL actuals

### Goals still typed in the notebook

- Ad Impressions (`IMPRESSIONS_GOALS`)
- HQ Signal *(reference only; no source)*
- Experimentation `_EXP_COUNTS` when SQL is down
- SOTA `_SOTA_BY_Q` when the pillar doc grade changes
- Occasional Scale goal-rate or fallback constants

### After the morning run — check these

- [ ] Data clock looks right
- [ ] Scale and Rev/FTE show a **finished month**
- [ ] `0` means zero; a dash means missing
- [ ] Shopping Revenue and Measured Revenue **match** on KPI and GTM

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
- **What the goal is:** the **quarter** target on that same sheet. Color compares this month’s lift to that full-quarter goal — not to a day-elapsed QTD bar. See [A/B color](#ab-color).
- **Watch for:** Hex maps sheet labels to scorecard names. A missed rename leaves the goal **blank** and nothing alarms. `Price: Post-Install CPA` → `Post-Install CPA A/B` is the rename that breaks most often.
- **Shopping ROAS A/B** is the same color rule, but its sheet is one row per **quarter**, so Value is this quarter’s lift — not a monthly one. That is a different row from [Shopping Revenue](#rows-that-do-not-follow-these).

### Goals we typed in code

Only these ignore sheet updates — you edit the named Hex cell:

- Impressions
- HQ Signal *(reference only)*
- Experimentation `_EXP_COUNTS` when SQL is down
- SOTA `_SOTA_BY_Q` when the pillar grade changes
- Scale fallbacks when a sheet pull fails

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

Built in the Hex cell **`Quarter dates based on latest date`**. It reads three freshness SQL frames: ads (`latest_date_df`), DAUq (`dauq_date_freshness_df`), WAUq (`wauq_date_freshness_df`). Each row is one warehouse source and its **max ready** date.

**The math (in plain terms)**

| Term | Meaning |
|---|---|
| **Leading edge** | The freshest `max ready` date any source has reached |
| **Lag** | How many days a source sits behind the leading edge |
| **Current** | Lag ≤ **3 days** — this source counts toward the clock |
| **Lagging** | Lag > 3 days — off the clock; guarded metrics show `—` |
| **`latest_date`** | The **earliest** `max ready` among **current** sources |

The clock can sit at most **3 days** behind the leading edge. Weekend and holiday pipeline jitter stays on the clock; a genuinely broken table does not.

**What you see on a run**

The cell prints `latest_date`, `leading_edge`, and a per-source table (`role`, which source `← sets clock`, which `← off clock, dependent metrics blank`).

- **`data_delayed`** when `latest_date` < `leading_edge` — the app still publishes; lagging sources are handled per metric.
- **Orange tab banner** names metrics blanked for staleness and which source is behind.
- **`WARN systemic freshness incident`** when most sources are lagging — treat pacing colors as unreliable.

**What to do**

1. Read the cell output before debugging a single metric.
2. One `lagging` source → expect `—` on its metrics only.
3. To refresh the clock: run the three freshness SQL cells + **`Quarter dates based on latest date`**. Do not rerun the whole notebook.

**Not the shared daily clock** (these use their own as-of rules):

- **Measured Revenue** — sums through the component’s own latest day (a few days behind ads is normal)
- **Scale** and **Rev/FTE** — last finished planning month
- **Retention** — 28- or 91-day bake after the clock
- **MixShift** — last finished month + 7-day bake

**How each source gets its max ready date**

| Source | Ready when |
|---|---|
| Ads realized revenue | Latest day with non-zero revenue |
| Brand pillar | Latest day with non-zero brand revenue |
| Thriving communities | Latest day with thriving > 0 |
| Monetizable feed | Latest day with feed views > 0 |
| Product adoption revenue | Latest day with delivered revenue ≠ 0 |
| Shopping impressions, rolling revenue, HQ scores, RFD, E2E | Latest date folder that has rows |
| DAUq cube | Latest day in the last two weeks with DAUq users > 0 |
| WAUq reporting | Latest day in the last two weeks with WAUq > 0 |

**“Days into the quarter”** and QTD pacing use `latest_date`, not the calendar.

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
| Shopping Revenue — KPI tab only; the GTM copy is grey | `shopping_pace` | ≥85% of the weekly target | 70–85% | <70% |
| A/B (both tabs) | `ab_goal` | CQ already hit, or last 15 days of the quarter and ≥95% | last 15 days, 70–95% | last 15 days <70%; **earlier = grey** |
| MixShift iCR; New advertisers; Monetizable feed / PDP | `yoy` | YoY moving the right way (0.5% buffer) | — | else |
| Booking to Quota | `booking_quota` | Week of quarter 55% / 80% / 95% | 50 / 75 / 90 | else |
| DPA ROAS* | `lower_bounded_goal` | At or above the bound | — | below |
| eCPM; Thriving; WAUq; RFD; Retention; HQ Signal; CAPI; credit lines; AT+DPA; gROAS*; Budget; DAUq app / web breakouts | `grey` | — | — | always grey |

**Lower is better** (flips the “right way”): CPC, kCPA, Post-Install CPA, MixShift CPA.

Scale still uses `goal_binary`, but each row’s bar is its own pacing rule — see [Scale](#scale).

Any row can fall back to grey regardless of its strategy: a stale source, a pacing that cannot be computed, or a governance flag of Missing / Stale / Blocked all override the colour. That is why Company Level DAUq paces normally while the Supply-tab copies of DAUq and Impressions are always grey — the Supply rows are display duplicates and their goals live on Company Level. The full precedence order is in the [operations runbook](OPERATIONS_RUNBOOK.md#status-colours--how-they-are-decided).

### Rows that do not follow these

| Row | What’s different |
|---|---|
| **Scale** | Monthly sheets. Each row has its own shape (a level, a year-to-date, a count, or a grade). OE “QoQ” = this month-end vs the last month of last quarter. See [Scale](#scale) |
| **Rev/FTE** | Monthly last-twelve-months level. MoM / QoQ / YoY = that level vs **1 / 3 / 12 months** earlier. See [Rev/FTE](#revfte) |
| **Shopping Revenue** | The dollar **actual** does add up the quarter (R28 MoM, same-elapsed QoQ). **YoY** is year-to-date vs the same calendar day last year. The in-quarter **paced goal** comes from the pacing sheet (column AO) — not CQ × days elapsed. This is **not** the Shopping ROAS A/B row. |
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
| A daily source is late | If lag ≤ 3 days, the clock may move back slightly. If lag > 3 days, that source goes off the clock and its metrics show `—` with a tab banner. The 9:00 run can still succeed |
| Google Sheets is down | MAA, DAUq, A/B, or Scale goals go grey, or we keep the last successful pull |
| A planning-sheet row was renamed | A/B goals vanish. `Price: Post-Install CPA` must map to `Post-Install CPA A/B` |
| The quarter sheet was not rolled | Last quarter’s target, looking current |
| A typed-in goal was not updated | Impressions, HQ, Scale fallbacks, `_EXP_COUNTS`, `_SOTA_BY_Q` |
| A sheet-backed goal looks stale | Roadmap KPIs, pacing sheet, brand feed, or Rev/FTE sheet not rolled/updated |
| A Scale pin failed | A checksum. The row looks fine |

**Then ask:**

1. Is this a [quarter sum, a 28-day level, or a quarter average](#how-the-value-is-built) — or an [exception](#rows-that-do-not-follow-these)?
2. Should the date be the Data clock, or a finished month?
3. Is the goal from a sheet, from days elapsed, or from a number in the code?
4. If a row is rebuilt on two tabs (e.g. Shopping Revenue, Measured Revenue), do the **values** match?
