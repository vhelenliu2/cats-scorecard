# Operations runbook — quarter roll and monthly & weekly upkeep

**As of:** 14 September 2026

This is the step-by-step guide for keeping the CATS Scorecard current: what to roll at the start of a quarter, what to check each month, and what to do when a number looks stale.

Most of the dashboard takes care of itself. The 9:00 AM Chicago run re-runs the whole notebook, so it refreshes every warehouse-backed row **and re-reads every connected Google Sheet**. Nothing that lives in a sheet needs you to press a button.

Your work is only two things the schedule cannot do: confirm upstream sheets were updated, and edit the few goals that still live as notebook constants.

**Working links**

- [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae) — where you make edits
- [Published app](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest) — what stakeholders see
- [Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc) — owner, goal source and actual source for every metric
- Background: [How the scorecard works](HOW_THE_SCORECARD_WORKS.md) · [Metric playbook](METRIC_PLAYBOOK.md)

---

## Before you start

| Cadence | When | Who | What |
|---|---|---|---|
| **Daily** | 9:00 AM Chicago auto-run | — | Nothing — warehouse + sheets refresh. Investigate only if a row looks wrong. |
| **Weekly** | After Vinay's team updates pacing | **Vinay Sridhar** (sheet) · **You** (verify) | Confirm [pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) col **AO** has the current week — no Hex edit. |
| **Monthly** | First week after month close (~20 min) | **Nikhil Khanted** (Scale actuals) · **Nick Asaad** (FTE sheet) · **You** (verify) | Confirm Scale sources + FTE month landed. See [Part 2](#part-2--monthly-upkeep) and [Scale Actuals](#actuals). Edit Hex only for Experimentation Velocity fallback or SOTA grade. |
| **Quarterly** | Week 1 of new quarter (~half day) | **Metric owners** ([Step 0](#step-0--confirm-the-new-quarters-goals-with-each-owner)) · **You** (roll) | Owners confirm goals are final → run quarter-roll cell chains → publish Hex → Change Log. |

**1. At the quarter roll, confirm goals with their owners before you touch Hex.**

This applies to the quarterly run only — it is about confirming the *new quarter's targets*, not about routine monthly work. A goal sheet that has not been rolled looks completely normal in Hex; it simply keeps serving last quarter's target. Nor does a populated sheet mean the targets are settled, since teams revise them through the year. Hex cannot detect either case, so a one-line confirmation from the owner is the only real check.

**2. Sheets refresh themselves. Only a handful of notebook constants need you.**

The 9:00 run re-reads every connected sheet. When a sheet-backed row looks wrong, fix the sheet — not Hex.

**Auto on the 9:00 run (confirm upstream, do not re-type):** A/B goals, Shopping CQ/FY and weekly paced QTD, Measured Revenue steps, Upper Funnel (brand feed), Rev/FTE waypoints, Scale actuals and linear goal pacing, MAA/DAUq, FTE headcount.

**Goals that are still manual in Hex:** Ad Impressions `IMPRESSIONS_GOALS`, HQ Signal (no source). Scale FY/CQ targets auto-pull from Roadmap KPIs — confirm with Virgilio only. Among Scale **actuals**, Experimentation `_EXP_COUNTS` when SQL is down is the only notebook edit.

Run cells by hand only to verify a change today instead of waiting for tomorrow's 9:00 run.

**3. When you do run cells: run the cell you changed, then the Table cell for that tab. Nothing else.**


| Tab                 | Metrics cell                  | Table cell                  |
| ------------------- | ----------------------------- | --------------------------- |
| Company Level Goals | `Company Level Goals df`      | `Company Level Goals Table` |
| CATS SC / KPIs      | `CATS SC KPIs Metrics`        | `CATS SC KPIs Table`        |
| Ads Product & GTM   | `Ads Product and GTM Metrics` | `Ads Product and GTM Table` |
| Ads Supply Drivers  | `Ads Supply Drivers Metrics`  | `Ads Supply Drivers Table`  |


Running a cell re-runs its dependencies, so a goal or label change never needs a full notebook run.

---

# Part 1 — Quarter roll

Do this in week 1 of the new quarter. Budget half a day, most of it waiting on other people.

## Step 0 — Confirm the new quarter's goals with each owner

**Ask every owner the same question first: are the goals final for the new quarter?**

Ask it even when the sheet already looks complete. A populated cell is not a confirmation — teams revise targets through the year, so numbers sitting in a sheet may be provisional, carried over from last quarter, or already superseded by a decision that has not been written down yet. Only the owner knows which. The last column below is a follow-up to that question, not a substitute for it.

Send these on day 1 so answers arrive while you work. Owners are from the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).


| Metric                       | Fragility | Owner                                                     | Goal source                                                                                                                                                                                                                                                                         | Then confirm                                                                                                                                                                                              |
| ---------------------------- | --------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ad Impressions (US / ROW)    | High      | Yoni Sauerbrun · Yona Kuritzky                            | [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?pli=1&gid=1740552033#gid=1740552033)                                                                                                                               | What are the two full-quarter numbers?                                                                                                                                                                    |
| High Quality Signal Adoption | High      | Aayush Shah · Emre Enes Yavuz                             | **No sheet or doc published**                                                                                                                                                                                                                                                       | Ask them directly for the quarter's target — there is no source to read                                                                                                                                   |
| All A/B lifts                | Medium    | Christa Benton                                            | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236)                                                                                                                                                     | Does the KPIs tab have the new quarter's column?                                                                                                                                                          |
| DAUq (+ US / ROW)            | Medium    | Logan Wilson                                              | [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431)                                                                                                                                                         | Is the Latest Forecast tab on the new quarter?                                                                                                                                                            |
| Revenue / S+M FTE            | Medium    | Aaron Nelson *(goal)* · Nick Asaad *(FTE)*                | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625)                                                                                                                                                      | Q4 waypoint is unset — confirm or leave blank                                                                                                                                                             |
| Scale (all 5 rows)           | Medium    | Virgilio Pigliucci *(goals)* · Nikhil Khanted *(actuals)* | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) `KPIs` tab + [2026 S-Scale Pillar Updates](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) | Are FY targets and quarterly steps still correct? See [Scale Our Foundations](#scale-our-foundations-cats-sc--kpis).                                                                                      |
| Shopping Revenue             | Medium    | Ryan Sekulic · Vinay Sridhar                              | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236)                                                                                                                                                     | Full-quarter goal, and confirm the new quarter's tab exists in the [pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) |
| Upper Funnel Revenue         | Medium    | Emily Glauser                                             | [Brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit?tab=t.0#bookmark=id.sw1mjrnh4i0a)                                                                                                                                            | Confirm CQ and FY targets                                                                                                                                                                                 |
| Ads Realized Revenue         | Low       | Bassem Haddad · Evie Sarkes                               | `daily_quota_profile` (warehouse)                                                                                                                                                                                                                                                   | Is the new quarter's quota loaded?                                                                                                                                                                        |
| MAA (+ LCS / MM / SMB)       | Low       | Ye Liu · Pengfei Qiao · Paola Madueno                     | [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562)                                                                                                                                                          | Are the new quarter's daily goals in the sheet?                                                                                                                                                           |
| Overall Measured Revenue     | Low       | Anirudha Sundaresan                                       | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236)                                                                                                                                                     | Confirm the new quarter's step                                                                                                                                                                            |
| Shopping ROAS A/B            | Low       | Ryan Sekulic · Lillian Kravitz                            | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934)                                                                                                                                                        | Is the new quarter's row present?                                                                                                                                                                         |


Do not start Step 1 for a metric until its owner has replied — a populated sheet does not count as a reply. If an owner is slow, roll the rest and leave that one for a follow-up pass.

---

## Step 1 — Company Level Goals tab

**Goals — do these four.** The three sheet-backed ones would refresh on tomorrow's 9:00 run anyway; you run the cells here so you can confirm the roll landed correctly today rather than finding out a day later.

1. **MAA** — confirm [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562) `Daily Goals Allocation` has the new quarter. Run `Maa goals gsheet` → `Maa goals df`.
2. **DAUq** — confirm [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431) `Latest Forecast` has the new quarter. Run `DAUq targets gsheet` → `DAUq official targets df`. The sheet is in millions and Hex stores users, so a `45` should land as ~45,000,000.
3. **A/B goals** — confirm [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) `KPIs` has the new quarter's column. Run `C performance goals ab gsheet` → `C performance goals ab df` → `C performance goals ad df with cpv`.
4. **Ad Impressions** — hard-coded, no sheet connection. Read the two full-quarter numbers from [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?pli=1&gid=1740552033#gid=1740552033) Roq_Outlook tab search for Impression Goal and add a new key to `IMPRESSIONS_GOALS` in `Company Level Goals df`. The key must match the quarter label exactly, for example `'Q4 2026'`. eCPM goals derive from impressions and revenue and need no edit.

```python
IMPRESSIONS_GOALS = {'Q3 2026': {'US': 59_800_000_000, 'ROW': 57_900_000_000}}
```

**Actuals on this tab** — no action on any of them. Every row here is either warehouse-backed or read from a sheet by the 9:00 run.


| Metric                                                          | Actual source                                                                                                                              | Source updates | What you do |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------- | ----------- |
| Tier 2 A/B — CTR, kICR4, PiIR, VVR6, CPC, kCPA                  | [Ads Launch Review Sign-up Sheet](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) | Weekly         | Nothing     |
| Shopping ROAS A/B                                               | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934)               | Weekly         | Nothing     |
| Ads Realized Revenue, MAA, DAUq, Thriving, Ad Impressions, eCPM | Warehouse                                                                                                                                  | Daily          | Nothing     |


The one thing that silently breaks the A/B rows is a **renamed label** in the tracker, which blanks the goal without any warning. 

**Then run:** `Company Level Goals df` → `Company Level Goals Table`.

---

## Step 2 — CATS SC / KPIs tab

Most KPI goals auto-pull on the 9:00 run. Confirm upstream sources in Step 0, then run the sheet chain once at quarter roll so you can verify today.

**Quarter roll — run this chain once:**

`C performance goals ab gsheet` → `C performance goals ab df` → `C performance goals ad df with cpv` → `Rev FTE gsheet` → `Rev FTE df` → `Rev FTE actuals` → `CATS SC KPIs Metrics` → `CATS SC KPIs Table`

That chain reads Roadmap KPIs (Shopping + Measured + A/B), the shopping pacing sheet (column AO), the brand feed (Upper Funnel), and Rev/FTE waypoints.


| Goal                         | Auto-pull source                                                                                                                                                                                                    | Your job                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Shopping Revenue — CQ and FY | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) `KPIs` tab → `cats_kpi_sheet_goals`                                              | Confirm the new quarter's column; run the chain above at roll                                     |
| Shopping Revenue — paced QTD | [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) col **AO**, current week → same dict                             | Confirm Vinay's team updated the current quarter tab each week — Hex reads it on the 9:00 run     |
| Overall Measured Revenue     | Roadmap `KPIs` tab → `cats_kpi_sheet_goals`                                                                                                                                                                         | Confirm quarterly steps at roll                                                                   |
| Upper Funnel Revenue         | Brand pillar feed (`upper_funnel_revenue_df`)                                                                                                                                                                       | Confirm CQ/FY with Emily at roll                                                                  |
| Revenue / S+M FTE            | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) → `rev_fte_actuals`                                                                  | Confirm waypoints at roll; monthly = confirm new FTE month only                                   |
| High Quality Signal Adoption | **Manual** — no published source                                                                                                                                                                                    | Ask Aayush Shah or Emre Enes Yavuz for reference targets; status stays grey                       |
| Scale (five rows)            | [Roadmap KPIs tab](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) → `cats_kpi_sheet_goals` → `Scale foundations actuals` (linear pacing); SOTA actual from pillar doc | See [Scale Our Foundations](#scale-our-foundations-cats-sc--kpis) — verify sheet targets match pacing methodology; no notebook edit when Virgilio updates a rate |


**Other actuals on this tab** (warehouse or sheet — no typing):


| Metric                                                                                                        | Actual source                                                                                                                                      | Source updates | What you do                         |
| ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ----------------------------------- |
| Revenue / S+M FTE                                                                                             | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) + warehouse revenue | Monthly        | Confirm the sheet has the new month |
| A/B lifts, incl. Post-Install CPA                                                                             | [Ads Launch Review Sign-up Sheet](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925)         | Weekly         | Nothing                             |
| Shopping ROAS A/B                                                                                             | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934)                       | Weekly         | Nothing                             |
| Upper Funnel, Shopping Revenue, Measured Revenue, HQ Signal, gROAS, MAA, Reach / Frequency / Depth, Retention | Warehouse and Hex components                                                                                                                       | Daily          | Nothing                             |


---

### Scale Our Foundations (CATS SC / KPIs)

**Goal owner:** Virgilio Pigliucci · **Actuals verification:** Nikhil Khanted

**Goal sources:** [CATS Roadmap Planning — KPIs tab](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) (FY / CQ targets) · [2026 S-Scale Pillar Updates](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) (Actuals tracking links, performance readout)

Virgilio asked for **linear pacing across the year** — QTD goal bars scale with elapsed calendar time, not a flat quarter target.

**Goals auto-pull** from [Roadmap KPIs tab](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) on the 9:00 run — no notebook edit when Virgilio updates a target. Your job is to **confirm with Virgilio that the sheet targets are final** and that pacing colours look right after the next run.

**Goals chain:** `C performance goals ab gsheet` → `C performance goals ab df` → `C performance goals ad df with cpv` → `cats_kpi_sheet_goals` → `Scale foundations actuals` → `CATS SC KPIs Metrics` → `CATS SC KPIs Table`

**Actuals chain:** tracking source → `Scale * gsheet` / SQL → `Scale * df` → `Scale foundations actuals` → `CATS SC KPIs Metrics` → `CATS SC KPIs Table`

**Trap:** Failed sheet pulls fall back to checksums and still look healthy. If Value and “as of {month}” do not move month over month, check the source with Nikhil — do not type a cover number.

#### Goals

**All five goals** auto-pull from the [CATS Roadmap KPIs tab](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) on the 9:00 run — no notebook edit when Virgilio updates a target. QTD goal bars apply **linear pacing** (below) on top of the sheet targets. Confirm with Virgilio that targets are **final** and that status colours look right after the next run.

All rows use `goal_binary`: **Green** = at or above 100% of the paced bar · **Yellow** = never · **Red** = below 100%.


| Metric | Source | KPI row | Current CQ / FY target | QTD pacing rule | Status (Green / Yellow / Red) | Confirm with owner |
| --- | --- | --- | --- | --- | --- | --- |
| Operational Excellence | [CATS Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) | M10n / Operational Excellence | CQ rate from **current quarter column**; FY rate from **FY Goal column** | **CQ rate × (completed months in quarter ÷ 3)**; status compares **QoQ** to that rate (not Value) | **Green:** QoQ ≥ QTD rate · **Yellow:** — · **Red:** QoQ < QTD rate | Virgilio: are CQ / FY targets final? Do status colours match intent? |
| Cloud Savings | [CATS Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) | Cloud Savings | FY $ from **FY Goal column** (CQ often blank) | **FY target × (completed months ÷ 12)** | **Green:** YTD $ ≥ QTD bar · **Yellow:** — · **Red:** YTD $ < QTD bar | Virgilio: is FY $ target final? Do status colours match intent? |
| Model Velocity | [CATS Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) | Model Velocity | FY YoY % from **FY Goal column** | **Last-year same-elapsed launch count × (1 + FY rate)** | **Green:** QTD count ≥ QTD goal · **Yellow:** — · **Red:** QTD count < QTD goal | Virgilio: is FY YoY rate final? Do status colours match intent? |
| Experimentation Velocity | [CATS Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) | Experimentation Velocity | FY YoY % from **FY Goal column** | **LY same-elapsed count × (1 + FY rate)**; CQ bar = LY full quarter × rate | **Green:** QTD count ≥ QTD goal · **Yellow:** — · **Red:** QTD count < QTD goal | Virgilio: is FY YoY rate final? Do status colours match intent? |
| Ads SOTA ML | [CATS Roadmap KPIs](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236) | Ads SOTA ML | FY letter grade from **FY Goal column** | **Linear path calendar year:** expected rank = 1.7 + 1.3 × (months elapsed ÷ 12), mapped to letter grade | **Green:** current grade ≥ paced grade · **Yellow:** — · **Red:** current grade < paced grade | Virgilio: is FY grade final? Do status colours match intent? (Actual grade auto-scans [pillar doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) — confirm readout is posted.) |


#### Actuals

Output dicts from **`Scale foundations actuals`** that **`CATS SC KPIs Metrics`** reads (`scale_oe_actuals`, etc.).


| Metric | Tracking source | Notebook path → variable | Value & comps | Monthly action |
|---|---|---|---|---|
| Operational Excellence | [Manager Dashboard](https://docs.google.com/spreadsheets/d/1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU/edit?gid=876519945) | `Scale OE gsheet` → `Scale OE df` → **`scale_oe_actuals`** | **Auto.** Sum of team scores at latest completed month-end (skip summary rows). MoM / QoQ / YoY = same-team % change vs prior month, prior-Q-end, or Dec 2025 | Confirm new month column (~1 mo lag OK) |
| Cloud Savings | [Efficiencies tracker](https://docs.google.com/spreadsheets/d/1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY/edit?gid=915660352) C1/E1 | `Scale cloud gsheet` → `Scale cloud df` → **`scale_cloud_actuals`** | **Auto.** YTD from C1 (checksum if unreadable). **MoM / QoQ / YoY intentionally blank** — savings have no reliable as-of date to phase a comparison from | Confirm C1 moved |
| Model Velocity | [Ranking](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=477633216#gid=477633216) · [Retrieval](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=972292259#gid=972292259) · [Shopping](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934#gid=90038934) | `Scale ML gsheet` → four df cells → **`scale_ml_actuals`** | **Auto.** QTD launch count = sum across the three tracking tabs (Ranking + Retrieval + Shopping) of launches with **>0 impact, excluding bug fixes** (also drops backtests / deprecations / undated) | Confirm new launches on 2026 tabs |
| Experimentation Velocity | [Insights](https://app.hex.tech/reddit/app/Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ/latest) QTD card | `Scale exp treatment starts df` → **`scale_exp_actuals`**; else **`_EXP_COUNTS`** | **Auto if SQL runs.** QTD distinct experiments (Ads Exp, `unique_objects > 1000`). Read **QTD not YTD** | If SQL down: update `_EXP_COUNTS[(year, quarter)]` from QTD card after month close |
| Ads SOTA ML | [Pillar doc — Subjective readout](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) | `Scale foundations actuals` → `scale_sota_actuals` (auto-scan) | Hex picks **most recent dated grade** in Subjective readout. MoM / QoQ / YoY blank | Confirm new readout posted — no Hex edit |


**After any notebook edit:** `Scale foundations actuals` → `CATS SC KPIs Metrics` → `CATS SC KPIs Table`. Verification only → wait for 9:00 run.

---

## Step 3 — Ads Product & GTM tab

Shopping and Measured on this tab are **actuals only** (goals live on CATS SC / KPIs). No goal edits here.

**Actuals on this tab** — every row is warehouse-backed or reads a Hex component. Budget Utilization stays blank: its source table stopped on 2 June 2026.

**Then run:** `Ads Product and GTM Metrics` → `Ads Product and GTM Table` (optional verification at quarter roll).

---

## Step 4 — Ads Supply Drivers tab

DAUq targets come from the sheet you refreshed in Step 1; WAUq, Monetizable Feed and PDP have no targets by design, and all four are warehouse-backed.

**Then run:** `Ads Supply Drivers Metrics` → `Ads Supply Drivers Table`.

---

## Step 5 — Verify in the draft, then publish

Check your work in the [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae) — the published app will not show any of it until you publish, so the draft is the only place your changes exist. Confirm:

- Goal columns show the new quarter, not the previous one
- No goal column is unexpectedly blank
- A/B rows are grey early in the quarter — that is the intended status, not a bug

Publish once the draft looks right, then record notebook constant edits in the **Change Log** tab of the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc). Sheet-backed goals audit through their source sheets.

---

# Part 2 — Monthly upkeep

Run this after the S-pillar team closes the month, usually in the first week (~20 minutes). The 9:00 run re-reads connected sheets automatically — your job is to **verify sources updated**, not re-type numbers.

**Scale Our Foundations:** Follow the **Goals** and **Actuals** tables in [Scale Our Foundations](#scale-our-foundations-cats-sc--kpis) (Step 2). Goals auto-pull from Roadmap KPIs — verify only. Only Experimentation (when SQL is down) needs a notebook edit among Scale actuals.

## Revenue / Sales + Marketing FTE

**Goal owner: Aaron Nelson. Monthly FTE: Nick Asaad.** Revenue comes from the warehouse; headcount comes from a sheet.

Confirm the new month is in the [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625). That is the whole task — the 9:00 run reads the sheet and rebuilds the row. Nothing to edit, nothing to run.

The row title reads `(LTM as of <month>)` and should show the last month that has headcount. If headcount has not landed, leave it — pairing newer revenue with older headcount produces a wrong number, not a fresher one.

---

# Weekly — Shopping Revenue pacing goal

**Owner: Vinay Sridhar.** His team updates the paced QTD target each week on the [shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) (`Q{n} DPA tracker` tab, column **AO**).

**You do not edit Hex for this.** The 9:00 run reads column AO via `C performance goals ad df with cpv` → `cats_kpi_sheet_goals` → `CATS SC KPIs Metrics`.

If pacing colour looks wrong after the sheet was updated, confirm the current quarter's tab exists and column AO has the current week's row — then run `C performance goals ab gsheet` through `CATS SC KPIs Table` to verify today.

---

# Status colours — how they are decided

You will rarely change these, but you should know where they live in case an owner asks for a different threshold.

Every row has a **status rule**: a named string that turns value and goal into a colour. The rule is set in that tab's Metrics cell through `.with_status(...)`, alongside a plain-English `definition` that becomes the tooltip. The rules themselves are implemented in the **Status Strategies** cell.

The rules currently in use (10 total — see `[docs/goaling/REFERENCE_status_policies.md](../goaling/REFERENCE_status_policies.md)`):


| Rule                 | Green                                        | Yellow     | Red   | Used by                                                                                                                                         |
| -------------------- | -------------------------------------------- | ---------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `goal_binary`        | ≥100%                                        | —          | <100% | MAA family, Ads Realized Revenue, Rev/FTE, all Scale rows                                                                                       |
| `goal_rev_2m`        | ≥99.5%                                       | within $2M | else  | Upper Funnel Revenue                                                                                                                            |
| `goal_rev_5m`        | ≥99.5%                                       | within $5M | else  | Overall Measured Revenue                                                                                                                        |
| `impressions_pacing` | ≥98%                                         | 96–98%     | <96%  | Company Level — Ad Impressions **and DAUq**, each as total / US / ROW                                                                           |
| `shopping_pace`      | ≥85% of the paced target                     | 70–85%     | <70%  | Shopping Revenue **on the KPIs tab only** — the GTM copy is grey by design                                                                      |
| `ab_goal`            | goal met any time, or ≥95% in the last month | 70–95%     | <70%  | every A/B row — grey in months 1 and 2, by design                                                                                               |
| `yoy`                | YoY moving the right way                     | —          | else  | MixShift iCR, New Advertisers Activated, Monetizable Feed / PDP — **and MixShift CPA, where the test is inverted** because falling cost is good |
| `booking_quota`      | week-of-quarter thresholds                   | see rule   | else  | Input Demand — % Booking to Quota                                                                                                               |
| `lower_bounded_goal` | at/above floor                               | —          | below | GTM — Marketplace Efficiency                                                                                                                    |
| `grey`               | always grey                                  | —          | —     | rows with no official target: gROAS, Reach / Frequency / Depth, Retention, HQ Signal                                                            |


Two things the table cannot show.

**A row can end up grey whatever its rule says.** The assignment runs in layers, and the last one wins:

```
1. .with_status(...) in the tab's Metrics cell
2. a patch cell reassigning status_goal     ← the A/B patches do this
3. a conditional override                   ← source is stale, or pacing cannot be computed
4. apply_governance_warnings                ← governance marks the metric Missing / Stale / Blocked
```

Company Level DAUq is the clearest example: it runs `impressions_pacing` when it has a goal and a computable pacing, and drops to grey when it does not. The Supply-tab copies of DAUq and Ad Impressions are forced grey at layer 3 every time — they are display duplicates, and their goals live on Company Level.

`**goal_binary` covers rows with quite different maths.** All of them share the same ≥100% test, but each passes its own sentence into the tooltip: Ads Realized Revenue and MAA measure against the QTD goal, Rev/FTE against a linear path between quarterly waypoints, and each Scale row supplies its own pacing function.

**Two rule names in older notes are not live.** `goal_rev` was replaced by `goal_rev_2m` and `goal_rev_5m`; `dauq` was never implemented, and DAUq uses `impressions_pacing`. If you meet either in an older document, this table is the current one.

**To change thresholds:**

1. Open the Hex draft → **Status Strategies** cell.
2. Edit the strategy class for that rule (thresholds are in the class body, e.g. `GoalBinaryStatusStrategy`).
3. If row assignments changed, update `**ACTIVE_STATUS_RULES**` at the top of the same cell.
4. Update the matching row in [REFERENCE_status_policies.md](../goaling/REFERENCE_status_policies.md) and in the Status colors section of [How the scorecard works](HOW_THE_SCORECARD_WORKS.md) — all three lists have to move together or they drift apart again.
5. Run **Status Strategies** → affected tab **Metrics** → **Table**.

Only these 10 rule names are valid. An unrecognised string raises a `ValueError` and the whole tab fails to build. Do not add legacy rules “just in case”.

---

# When something looks stale

Start with the clock before investigating any single metric. Open the draft and read the output of `**Quarter dates based on latest date**` — it prints the clock date, the freshest date available, and the status of every source.


| What you see                                     | What it means                                                        | What to do                                                                                                                                                                                                               |
| ------------------------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Clock moved back a day or two                    | A source is slightly behind, within the 3-day tolerance              | Nothing — normal pipeline timing                                                                                                                                                                                         |
| A metric shows `—` and an orange banner names it | Its source is more than 3 days behind and was dropped from the clock | Note the source in the banner; escalate to the warehouse owner if it persists                                                                                                                                            |
| `WARN systemic freshness incident`               | Most sources are behind — a warehouse-wide problem                   | Do not trust pacing colours; flag before anyone reads the numbers                                                                                                                                                        |
| A Scale row matches last month exactly           | The sheet was not updated, or the pull failed back to a checksum     | Check the sheet, then ask Nikhil                                                                                                                                                                                         |
| An A/B goal is suddenly blank                    | A label in the goals sheet was renamed and no longer matches the map | Compare the sheet label to **Canonical Metric Map** / **C performance goals ad df with cpv** output. See [Post-Install CPA A/B vs plain CPA](#post-install-cpa-ab-vs-plain-cpa).                                         |
| A goal column looks like last quarter's          | The sheet was never rolled                                           | Confirm with the owner and get the sheet rolled. The next 9:00 run picks it up; run its source cells if you need to see it today                                                                                         |
| Shopping pacing colour looks wrong               | Pacing sheet tab or column AO not updated for the current week       | Confirm `Q{n} DPA tracker` col AO on the [pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712); re-run goals chain → KPI Metrics → Table |
| Budget Utilization is empty                      | Intentional — source table died 2 June 2026                          | Leave it. Dana owns replace-or-retire                                                                                                                                                                                    |


Two rules worth repeating: a `0` means the metric really was zero, and a dash means we do not have the data — never convert a failed pull into a zero. And never re-run the whole notebook to fix a stale row; find the source cell and run that.

## Post-Install CPA A/B vs plain CPA

These are **two different metrics**. Do not merge their goals or actuals.


| What                           | Goals sheet label              | Canonical key          | Actual source (launch tracker)                                                           | Displayed on               |
| ------------------------------ | ------------------------------ | ---------------------- | ---------------------------------------------------------------------------------------- | -------------------------- |
| **Post-Install CPA A/B**       | `Price: Post-Install CPA`      | `Post-Install CPA A/B` | `Post-Install Cost (CPA)` → `Post-Install CPA A/B` in `cats_c_performance_ab_metrics_df` | KPI tab only               |
| **Plain CPA** *(if published)* | `Price: CPA`, `CPA`, `CPA A/B` | `CPA A/B`              | `CPA` column → `CPA A/B`                                                                 | not on Company Level today |


**Install Cost (CPI)** is a third metric (`CPI A/B`) — never substitute it for Post-Install CPA.

The only deliberate “same metric, two names” case is **kCPA**: display `kCPA A/B`, actuals/goals key `kCPA4 A/B`.

If a goal is blank after a sheet rename:

1. Note the exact label on the [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) `KPIs` tab.
2. Open the Hex draft and run **C performance goals ab gsheet** → **C performance goals ad df with cpv** (or read **Canonical Metric Map**).
3. If the label is missing from the map, add an explicit alias in **Canonical Metric Map** and the `metric_rename` block in **C performance goals ad df with cpv** — then re-run those cells → **CATS SC KPIs Metrics** → **CATS SC KPIs Table**.
4. Do **not** map Post-Install labels onto plain `CPA A/B` (see table above).

---

# Who owns what

Owner, goal source and actual source for every metric live in one place: the **[CATS Scorecard Data Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc)**. Use it rather than a copy in this document, so there is only one list to keep current.

Two things it does not cover: Hex project access and publishing sit with the current Hex project owner, and the Budget Utilization replace-or-retire decision sits with Dana.

---

# Quick checklists

**Quarter roll**

- [ ] Every owner has confirmed the goals are **final** for the new quarter — a populated sheet is not a confirmation. Includes HQ Signal, which has no sheet at all.
- [ ] Company Level: MAA, DAUq and A/B sheets confirmed rolled; `IMPRESSIONS_GOALS` updated from Daily Forecast – Live
- [ ] KPIs: Roadmap KPIs + pacing sheet + Rev/FTE sheet confirmed; goals chain run → KPI Table verified
- [ ] Scale: Virgilio confirmed current quarter + **FY Goal** columns on [Roadmap KPIs tab](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236#gid=114524236); status colours look right; `_EXP_COUNTS` updated if SQL was down at roll
- [ ] GTM: Metrics → Table re-run (actuals-only rows; no goal sync needed)
- [ ] Supply: table re-run
- [ ] Draft reviewed, then published
- [ ] Change Log updated in the governance sheet

**Monthly**

- [ ] Scale actuals verified per [Scale Our Foundations → Actuals](#scale-our-foundations-cats-sc--kpis) (monthly action column)
- [ ] FTE sheet has the new month
- [ ] If any Scale notebook constant edited: `Scale foundations actuals` → KPIs metrics → table re-run, and published

**Weekly**

- [ ] Vinay's team updated column AO on the current quarter's DPA tracker tab
- [ ] After Monday 9:00 run (or spot-check): Shopping pacing colour on KPI tab looks right
