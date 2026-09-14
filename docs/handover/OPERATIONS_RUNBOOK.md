# Operations runbook — quarter roll and monthly upkeep

**As of:** 14 September 2026

This is the step-by-step guide for keeping the CATS Scorecard current: what to roll at the start of a quarter, what to check each month, and what to do when a number looks stale.

Most of the dashboard takes care of itself. The 9:00 AM Chicago run re-runs the whole notebook, so it refreshes every warehouse-backed row **and re-reads every connected Google Sheet**. Nothing that lives in a sheet needs you to press a button.

Your work is only the two things the schedule cannot do: confirm that the humans upstream actually updated their sheets, and edit the values that are typed directly into the notebook.

**Working links**

- [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae) — where you make edits
- [Published app](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest) — what stakeholders see
- [Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc) — owner, goal source and actual source for every metric
- Background: [How the scorecard works](HOW_THE_SCORECARD_WORKS.md) · [Metric playbook](METRIC_PLAYBOOK.md)

---

## Two rules before you start

**1. At the quarter roll, confirm goals with their owners before you touch Hex.**

This applies to the quarterly run only — it is about confirming the *new quarter's targets*, not about routine monthly work. A goal sheet that has not been rolled looks completely normal in Hex; it simply keeps serving last quarter's target. Nor does a populated sheet mean the targets are settled, since teams revise them through the year. Hex cannot detect either case, so a one-line confirmation from the owner is the only real check.

**2. Sheets refresh themselves. Only typed-in values need you.**

If a number lives in a Google Sheet — A/B actuals, Shopping ROAS, Scale, FTE headcount, MAA and DAUq goals — the 9:00 run picks up whatever the sheet says that morning. There is nothing to run. When a sheet-backed row looks wrong, the sheet is the problem, not Hex.

If a number is typed into the notebook — the hard-coded goals, the SOTA grade, the Experimentation count, the weekly Shopping paced target — the schedule can never change it. You edit the draft and publish. That is the entire manual surface of this dashboard.

Running cells by hand is only for seeing a change immediately instead of waiting for tomorrow's 9:00 run.

**3. When you do run cells: run the cell you changed, then the Table cell for that tab. Nothing else.**

| Tab | Metrics cell | Table cell |
|---|---|---|
| Company Level Goals | `Company Level Goals df` | `Company Level Goals Table` |
| CATS SC / KPIs | `CATS SC KPIs Metrics` | `CATS SC KPIs Table` |
| Ads Product & GTM | `Ads Product and GTM Metrics` | `Ads Product and GTM Table` |
| Ads Supply Drivers | `Ads Supply Drivers Metrics` | `Ads Supply Drivers Table` |

Running a cell re-runs its dependencies, so a goal or label change never needs a full notebook run.

---

# Part 1 — Quarter roll

Do this in week 1 of the new quarter. Budget half a day, most of it waiting on other people.

## Step 0 — Confirm the new quarter's goals with each owner

**Ask every owner the same question first: are the goals final for the new quarter?**

Ask it even when the sheet already looks complete. A populated cell is not a confirmation — teams revise targets through the year, so numbers sitting in a sheet may be provisional, carried over from last quarter, or already superseded by a decision that has not been written down yet. Only the owner knows which. The last column below is a follow-up to that question, not a substitute for it.

Send these on day 1 so answers arrive while you work. Owners are from the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).

| Metric | Owner | Goal source | Then confirm |
|---|---|---|---|
| Ads Realized Revenue | Bassem Haddad · Evie Sarkes | `daily_quota_profile` (warehouse) | Is the new quarter's quota loaded? |
| MAA (+ LCS / MM / SMB) | Ye Liu · Pengfei Qiao · Paola Madueno | [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562) | Are the new quarter's daily goals in the sheet? |
| DAUq (+ US / ROW) | Logan Wilson | [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431) | Is the Latest Forecast tab on the new quarter? |
| Ad Impressions (US / ROW) | Yoni Sauerbrun · Yona Kuritzky | [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?pli=1&gid=1740552033#gid=1740552033) | What are the two full-quarter numbers? |
| All A/B lifts | Christa Benton | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Does the KPIs tab have the new quarter's column? |
| Shopping Revenue | Ryan Sekulic · Vinay Sridhar | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Full-quarter goal, and confirm the new quarter's tab exists in the [pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) |
| Shopping ROAS A/B | Ryan Sekulic · Lillian Kravitz | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) | Is the new quarter's row present? |
| Upper Funnel Revenue | Emily Glauser | [Brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit?tab=t.0#bookmark=id.sw1mjrnh4i0a) | Confirm CQ and FY targets |
| Overall Measured Revenue | Anirudha Sundaresan | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) | Confirm the new quarter's step |
| High Quality Signal Adoption | Aayush Shah · Emre Enes Yavuz | **No sheet or doc published** | Ask them directly for the quarter's target — there is no source to read |
| Revenue / S+M FTE | Aaron Nelson *(goal)* · Nick Asaad *(FTE)* | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) | Q4 waypoint is unset — confirm or leave blank |
| Scale (all 5 rows) | Virgilio Pigliucci · Nikhil Khanted | [2026 S-Scale Pillar Updates](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) | Are the new quarter's goals set? |

Do not start Step 1 for a metric until its owner has replied — a populated sheet does not count as a reply. If an owner is slow, roll the rest and leave that one for a follow-up pass.

---

## Step 1 — Company Level Goals tab

**Goals — do these four.** The three sheet-backed ones would refresh on tomorrow's 9:00 run anyway; you run the cells here so you can confirm the roll landed correctly today rather than finding out a day later.

1. **MAA** — confirm [MAB Goaling 2026](https://docs.google.com/spreadsheets/d/1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc/edit?gid=908340562) `Daily Goals Allocation` has the new quarter. Run `Maa goals gsheet` → `Maa goals df`.
2. **DAUq** — confirm [DAUq Master Sheet](https://docs.google.com/spreadsheets/d/1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ/edit?gid=964936431) `Latest Forecast` has the new quarter. Run `DAUq targets gsheet` → `DAUq official targets df`. The sheet is in millions and Hex stores users, so a `45` should land as ~45,000,000.
3. **A/B goals** — confirm [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) `KPIs` has the new quarter's column. Run `C performance goals ab gsheet` → `C performance goals ab df` → `C performance goals ad df with cpv`.
4. **Ad Impressions** — hard-coded, no sheet connection. Read the two full-quarter numbers from [Daily Forecast – Live](https://docs.google.com/spreadsheets/d/1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0/edit?pli=1&gid=1740552033#gid=1740552033) and add a new key to `IMPRESSIONS_GOALS` in `Company Level Goals df`. The key must match the quarter label exactly, for example `'Q4 2026'`. eCPM goals derive from impressions and revenue and need no edit.

```python
IMPRESSIONS_GOALS = {'Q3 2026': {'US': 59_800_000_000, 'ROW': 57_900_000_000}}
```

**Actuals on this tab** — no action on any of them. Every row here is either warehouse-backed or read from a sheet by the 9:00 run.

| Metric | Actual source | Source updates | What you do |
|---|---|---|---|
| Tier 2 A/B — CTR, kICR4, PiIR, VVR6, CPC, kCPA | [Ads Launch Review Sign-up Sheet](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) | Weekly | Nothing |
| Shopping ROAS A/B | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) | Weekly | Nothing |
| Ads Realized Revenue, MAA, DAUq, Thriving, Ad Impressions, eCPM | Warehouse | Daily | Nothing |

The one thing that silently breaks the A/B rows is a **renamed label** in the tracker, which blanks the goal without any warning. See the [note on Post-Install CPA](#a-note-on-post-install-cpa-and-cpa-ab).

**Then run:** `Company Level Goals df` → `Company Level Goals Table`.

---

## Step 2 — CATS SC / KPIs tab

This tab carries the most hard-coded goals. All of them live in `CATS SC KPIs Metrics` — there is no sheet connection, so each is read from its source and typed in.

| Goal | Variable | Current value | Where the number comes from |
|---|---|---|---|
| Shopping Revenue — quarter and FY | `shop_q_goal`, `shop_annual_target` | `22_000_000`, `70_000_000` | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) |
| Shopping Revenue — paced QTD | `shop_qtd_goal` | `17_184_895` — **changes weekly** | [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712), tab `Q3 DPA tracker`, **column AO**. See the weekly section; never assume the value above is current. |
| Overall Measured Revenue | `_measured_q_goals`, `_measured_year_goal` | `{1: 200M, 2: 350M, 3: 450M, 4: 500M}`, `1.5B` | [CATS Roadmap Planning](https://docs.google.com/spreadsheets/d/1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw/edit?gid=114524236) |
| Upper Funnel Revenue | `uf_q_goal`, `uf_year_goal` | `310_000_000`, `1_100_000_000` | [Brand goals doc](https://docs.google.com/document/d/1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8/edit?tab=t.0#bookmark=id.sw1mjrnh4i0a) |
| Revenue / S+M FTE | `_fte_q_goals`, `_fte_year_goal` | `{1: 3.07M, 2: 3.2M, 3: 3.4M, 4: None}`, `3.7M` | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) |
| High Quality Signal Adoption | reference only — status stays grey | Q3 45%, FY 50% | No published source. Ask Aayush Shah or Emre Enes Yavuz. |

Scale goals come from the [pillar doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt), not the notebook. Confirm with Virgilio that the new quarter's targets are set.

**Actuals on this tab**, most hands-on first. Only the two Scale rows at the top need a person.

| Metric | Actual source | Source updates | What you do |
|---|---|---|---|
| Experimentation Velocity · Ads SOTA ML | A dashboard and the pillar doc — **not connected to Hex** | Monthly | **Type the value in.** See Part 2 |
| Operational Excellence · Cloud Savings · Model Velocity | Pillar sheets | Monthly | Confirm the sheet has the new month — the read is automatic |
| Revenue / S+M FTE | [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625) + warehouse revenue | Monthly | Confirm the sheet has the new month |
| A/B lifts, incl. Post-Install CPA | [Ads Launch Review Sign-up Sheet](https://docs.google.com/spreadsheets/d/1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s/edit?gid=1457726925) | Weekly | Nothing |
| Shopping ROAS A/B | [Shopping 3H Tracker](https://docs.google.com/spreadsheets/d/1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0/edit?gid=90038934) | Weekly | Nothing |
| Upper Funnel, Shopping Revenue, Measured Revenue, HQ Signal, gROAS, MAA, Reach / Frequency / Depth, Retention | Warehouse and Hex components | Daily | Nothing |

**Then run:** `CATS SC KPIs Metrics` → `CATS SC KPIs Table`.

---

## Step 3 — Ads Product & GTM tab

Only the two mirrored goals need attention here.

In `Ads Product and GTM Metrics`, set `shop_q_goal`, `shop_qtd_goal`, `shop_annual_target`, `_measured_q_goals` and `_measured_year_goal` to exactly the values you used in Step 2.

**Actuals on this tab** — every row is warehouse-backed or reads a Hex component, so there is nothing to pull. The one exception is Budget Utilization, which stays blank: its source table stopped on 2 June 2026 and Dana owns the decision to replace or retire the row.

**Then run:** `Ads Product and GTM Metrics` → `Ads Product and GTM Table`.

---

## Step 4 — Ads Supply Drivers tab

No goal edits and no actuals work. DAUq targets come from the sheet you refreshed in Step 1; WAUq, Monetizable Feed and PDP have no targets by design, and all four are warehouse-backed.

**Then run:** `Ads Supply Drivers Metrics` → `Ads Supply Drivers Table`.

---

## Step 5 — Verify in the draft, then publish

Check your work in the [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae) — the published app will not show any of it until you publish, so the draft is the only place your changes exist. Confirm:

- Goal columns show the new quarter, not the previous one
- No goal column is unexpectedly blank
- A/B rows are grey early in the quarter — that is the intended status, not a bug

Publish once the draft looks right, then record what you changed in the **Change Log** tab of the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc). The hard-coded goals have no other audit trail.

---

# Part 2 — Monthly upkeep

Run this after the pillar teams close the month, usually in the first week. Expect about 20 minutes, most of it reading sheets rather than editing Hex. Only the **CATS SC / KPIs** tab needs attention.

Monthly upkeep is mostly **verification**: the sheets are re-read automatically every morning, so your job is to confirm the pillar teams actually published a new month. The only edits are the two Scale rows that are not connected to Hex at all.

## Scale Our Foundations — actuals, not goals

**This section is about actuals.** Scale goals are set once a quarter from the [2026 S-Scale Pillar Updates doc](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) and handled in the quarter roll.

**Monthly is the refresh cadence, not the measurement window.** None of these five is a monthly metric: Operational Excellence is a quarter-over-quarter change, Cloud Savings is year-to-date, Model Velocity is a quarter-to-date count, and Ads SOTA ML is a letter grade. What happens monthly is that the pillar teams update their sources and we re-read them.

**Actuals owner: Nikhil Khanted** — the person to verify a number with when it looks wrong. Virgilio Pigliucci owns the goals.

| Row | Actual source | Hex cells | How the number is derived |
|---|---|---|---|
| Operational Excellence | [M3 Manager-System Mapping](https://docs.google.com/spreadsheets/d/1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU/edit?gid=876519945), tab `Manager Dashboard` | `Scale foundations gsheet` → `Scale OE df` | Reads `A1:ZZ200`; each row a system, each month column a score, values above 1.5 read as percentages. Compares **same universe only** — a system missing from either month is dropped from both sides. Value is QoQ against the prior quarter-end month. |
| Cloud Savings | [Ads Initiatives and Efficiencies tracker 2026](https://docs.google.com/spreadsheets/d/1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY/edit?gid=915660352) | `Scale cloud gsheet` → `Scale cloud df` | Value is YTD savings from **cell C1**, FY goal from **cell E1**. If C1 is blank it falls back to summing the `Actual savings` column. MoM and QoQ use only dated rows, and are suppressed rather than shown as −100% when either side is zero. |
| Model Velocity | [Ranking ML KPIs](https://docs.google.com/spreadsheets/d/1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4/edit?gid=477633216) | `Scale ML gsheet` → the three `Scale ML … df` cells | Counts current-quarter launches with a **non-zero KPI movement** across the Ranking, Retrieval and Shopping tables. Excludes rows named *backtest*, *bug fix* or *deprecat*, and rows with a blank or zero value. Undated launches count toward the quarter but not the MoM/QoQ windows. |
| Experimentation Velocity | [Ads Experimentation Metrics dashboard](https://app.hex.tech/reddit/app/Ads-Experimentation-Metrics-031Wg80FsfMFpb7daAPehQ/latest) | Typed into `CATS SC KPIs Metrics` | Not wired to a query. Open the dashboard, read the QTD launch count, and type it in. |
| Ads SOTA ML | [2026 S-Scale Pillar Updates](https://docs.google.com/document/d/10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c/edit?tab=t.o2eroxuo1vpt) | Typed into `CATS SC KPIs Metrics` | A subjective letter grade from the pillar, currently `B-` as of 22 August 2026. Update when a new grade is published. |

### Steps

1. Confirm a new month-end row exists in the three pillar sheets. If one is missing, ask Nikhil — do not type a number into Hex to cover for it.
2. Read the Experimentation Velocity count off the dashboard and type it into `CATS SC KPIs Metrics`; update the SOTA grade if the pillar published a new one.
3. Run `CATS SC KPIs Metrics` → `CATS SC KPIs Table`, then publish.
4. Confirm the "as of" month in each row title moved forward.

Step 3 exists only because of the typed-in values in step 2. If nothing needed typing, there is nothing to run — the three sheet-backed rows will have refreshed on their own.

**The trap:** when a sheet cannot be read, these rows fall back to a saved **checksum** and still display a plausible number. A row that never changes month over month is the signal. Treat a checksum as missing data, not an actual.

## Revenue / Sales + Marketing FTE

**Goal owner: Aaron Nelson. Monthly FTE: Nick Asaad.** Revenue comes from the warehouse; headcount comes from a sheet.

Confirm the new month is in the [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625). That is the whole task — the 9:00 run reads the sheet and rebuilds the row. Nothing to edit, nothing to run.

The row title reads `(LTM as of <month>)` and should show the last month that has headcount. If headcount has not landed, leave it — pairing newer revenue with older headcount produces a wrong number, not a fresher one.

---

# Weekly — Shopping Revenue pacing goal

The only recurring weekly task. **Owner: Vinay Sridhar.**

His team publishes a new paced QTD target each week here:

**[Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) → tab `Q3 DPA tracker` → column AO**

1. Read the current week's value from column AO.
2. Update `shop_qtd_goal` in `CATS SC KPIs Metrics`.
3. Update `shop_qtd_goal` in `Ads Product and GTM Metrics` to the same value.
4. Run both Metrics cells → both Table cells.

The tab is named per quarter, so from Q4 it will be `Q4 DPA tracker`. If you cannot find the current quarter's tab, ask Vinay before falling back to the old one — a target from last quarter's tab will pace against the wrong denominator.

Shopping pacing colour is calculated against this number, so a stale target produces a confidently wrong status — green when the team is behind, or red when they are not.

---

# Status colours — how they are decided

You will rarely change these, but you should know where they live in case an owner asks for a different threshold.

Every row has a **status rule**: a named string that turns value and goal into a colour. The rule is set in that tab's Metrics cell through `.with_status(...)`, alongside a plain-English `definition` that becomes the tooltip. The rules themselves are implemented in the **Status Strategies** cell.

The rules currently in use:

| Rule | Green | Yellow | Red | Used by |
|---|---|---|---|---|
| `goal_rev` | ≥99.5% of QTD goal | within $0.5M of goal | else | Ads Realized Revenue |
| `goal_rev_2m` | ≥99.5% | within $2M | else | Upper Funnel Revenue |
| `goal_rev_5m` | ≥99.5% | within $5M | else | Overall Measured Revenue |
| `goal_binary` | ≥100% | — | <100% | MAA family, Rev/FTE, all Scale rows |
| `impressions_pacing` | ≥98% | 96–98% | <96% | Ad Impressions, eCPM, DAUq |
| `shopping_pace` | ≥85% of the paced target | 70–85% | <70% | Shopping Revenue |
| `ab_goal` | goal met any time, or ≥95% in the last month | 70–95% | <70% | every A/B row — grey in months 1 and 2, by design |
| `grey` | always grey | — | — | rows with no official target: gROAS, Reach / Frequency / Depth, Retention, HQ Signal |

**To change one:** get the new thresholds in writing from the metric owner, edit the `status_goal` string in that tab's Metrics cell, update the `definition` text so the tooltip still matches the behaviour, run the Metrics cell → Table cell, and note it in the Change Log.

Only registered rule names are valid. An unrecognised string raises a `ValueError` and the whole tab fails to build, so changing a threshold usually means picking a different existing rule rather than inventing one. The full catalogue of available rules is in [`docs/goaling/REFERENCE_status_policies.md`](../goaling/REFERENCE_status_policies.md).

---

# When something looks stale

Start with the clock before investigating any single metric. Open the draft and read the output of **`Quarter dates based on latest date`** — it prints the clock date, the freshest date available, and the status of every source.

| What you see | What it means | What to do |
|---|---|---|
| Clock moved back a day or two | A source is slightly behind, within the 3-day tolerance | Nothing — normal pipeline timing |
| A metric shows `—` and an orange banner names it | Its source is more than 3 days behind and was dropped from the clock | Note the source in the banner; escalate to the warehouse owner if it persists |
| `WARN systemic freshness incident` | Most sources are behind — a warehouse-wide problem | Do not trust pacing colours; flag before anyone reads the numbers |
| A Scale row matches last month exactly | The sheet was not updated, or the pull failed back to a checksum | Check the sheet, then ask Nikhil |
| An A/B goal is suddenly blank | A label in the goals sheet was renamed and no longer matches the canonical map | Compare the sheet label against the map in `C performance goals ad df with cpv`. See the note below. |
| A goal column looks like last quarter's | The sheet was never rolled | Confirm with the owner and get the sheet rolled. The next 9:00 run picks it up; run its source cells if you need to see it today |
| Shopping pacing colour looks wrong | `shop_qtd_goal` is a stale weekly target | Read the current week's value from column AO of the [pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712) and update both Metrics cells |
| Budget Utilization is empty | Intentional — source table died 2 June 2026 | Leave it. Dana owns replace-or-retire |

Two rules worth repeating: a `0` means the metric really was zero, and a dash means we do not have the data — never convert a failed pull into a zero. And never re-run the whole notebook to fix a stale row; find the source cell and run that.

## A note on Post-Install CPA and `CPA A/B`

These look like two metrics and are easy to mistake for a bug. They are not the same thing, but today they are wired together deliberately.

`CPA A/B` is **not a displayed row** — Company Level explicitly filters out any row with that name. It survives only as an internal *goals key*. The row people actually see is **Post-Install CPA A/B** on the KPIs tab, whose actuals come from the launch tracker and whose goal is looked up under the key `CPA A/B`. The goals sheet label `Price: Post-Install CPA` is mapped to that key on purpose; adding the mapping is what fixed a stretch of blank Post-Install CPA goals.

Two things to watch:

- The labels `CPA`, `Price: CPA`, `Price:CPA` and `Price: Post-Install CPA` all collapse to the same `CPA A/B` key. If the goals sheet ever carries both a plain CPA row and a Post-Install CPA row, one will silently overwrite the other.
- A legacy comparison map points `CPA A/B` at the **CPI** (Install Cost) column, which is a genuinely different metric.

If Christa ever publishes plain CPA and Post-Install CPA as separate goals, they need separate keys — do not extend the current mapping to cover both.

---

# Who owns what

Owner, goal source and actual source for every metric live in one place: the **[CATS Scorecard Data Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc)**. Use it rather than a copy in this document, so there is only one list to keep current.

Two things it does not cover: Hex project access and publishing sit with the current Hex project owner, and the Budget Utilization replace-or-retire decision sits with Dana.

---

# Quick checklists

**Quarter roll**

- [ ] Every owner has confirmed the goals are **final** for the new quarter — a populated sheet is not a confirmation. Includes HQ Signal, which has no sheet at all.
- [ ] Company Level: MAA, DAUq and A/B sheets confirmed rolled; `IMPRESSIONS_GOALS` updated from Daily Forecast – Live
- [ ] KPIs: Shopping, Measured, Upper Funnel, Rev/FTE goals updated
- [ ] GTM: Shopping and Measured mirrored with identical values
- [ ] Supply: table re-run
- [ ] Draft reviewed, then published
- [ ] Change Log updated in the governance sheet

**Monthly**

- [ ] The three Scale pillar sheets have a new month-end row
- [ ] Experimentation Velocity count read off the dashboard and typed in; SOTA grade checked
- [ ] No Scale row is sitting on a checksum
- [ ] FTE sheet has the new month
- [ ] If anything was typed in: KPIs metrics → table re-run, and published

**Weekly**

- [ ] Current paced Shopping target read from column AO of the current quarter's DPA tracker tab
- [ ] `shop_qtd_goal` updated in both `CATS SC KPIs Metrics` and `Ads Product and GTM Metrics`
- [ ] Both Table cells re-run; Shopping pacing colour looks right
