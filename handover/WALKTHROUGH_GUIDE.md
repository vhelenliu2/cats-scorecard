# CATS Scorecard — knowledge transfer walkthrough

**As of:** 15 September 2026

Facilitator guide for walking a teammate through the live dashboard and [Operations runbook](OPERATIONS_RUNBOOK.md). Use this doc during the meeting; point people at the runbook for day-to-day work afterward.

**Audience:** Coworker taking over day-to-day scorecard ops  
**Duration:** 90 min (or two 45-min sessions — see [Split format](#split-into-two-sessions))  
**Facilitator:** Current scorecard owner

---

## Before the meeting

**Send pre-read (5 min):** [README](README.md) — links only, no deep read required.

**Open these tabs before you join:**

| Tab | Link |
| --- | --- |
| Published app (stakeholder view) | https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest |
| Hex draft (your workspace) | https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae |
| Governance sheet | https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc |
| Operations runbook | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) |
| Shopping pacing sheet (weekly example) | https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712 |

**Facilitator checklist**

- [ ] Pre-read sent
- [ ] Tabs open (published app first)
- [ ] Recording on (optional — “deliberate weirdness” section is worth replaying)
- [ ] Shadow assignment picked (see [Handoff](#6-handoff--next-steps-10-min))

**Screen-share order:** Published app → Governance sheet → Runbook → Hex draft (only if time)

**Do not live-run a quarter roll.** Walk the checklist and cell names instead.

---

## Agenda

| Time | Block | Outcome |
| --- | --- | --- |
| 0:00–0:10 | [1. Framing](#1-framing-10-min) | Why the scorecard exists; what “owning it” means |
| 0:10–0:25 | [2. Mental model](#2-mental-model-15-min) | Auto-run, data clock, sheets vs notebook constants |
| 0:25–0:45 | [3. Dashboard tour](#3-dashboard-tour-20-min) | Four tabs, colors, deliberate “weird” behavior |
| 0:45–1:05 | [4. Runbook by cadence](#4-runbook-by-cadence-20-min) | Daily / weekly / monthly / quarterly |
| 1:05–1:20 | [5. Troubleshooting](#5-troubleshooting-15-min) | Stale rows, blank goals, Scale trap, Post-Install CPA |
| 1:20–1:30 | [6. Handoff](#6-handoff--next-steps-10-min) | Shadow assignment, doc map, escalation |

**Checkpoint after block 2:** Ask — *“When would you edit Hex vs fix a Google Sheet?”*  
Expected answer: sheet for sheet-backed goals; Hex only for notebook constants and label aliases.

---

## 1. Framing (10 min)

### Opening line

> The CATS Scorecard is a Hex app that leadership uses to see how we’re pacing against company and pillar goals. Most of it runs itself every morning at 9:00 AM Chicago. Your job is not to babysit the notebook — it’s to confirm upstream sources were updated and edit the handful of goals that still live as code.

### Three things to land

| # | Point | Show |
| --- | --- | --- |
| 1 | Stakeholder view | [Published app](https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest) — changes only appear after publish from draft |
| 2 | Your workspace | [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae) + [Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc) |
| 3 | Doc hierarchy | See table below |

### Doc hierarchy

| Need | Document |
| --- | --- |
| Do something (roll, verify, publish) | [Operations runbook](OPERATIONS_RUNBOOK.md) |
| Number looks wrong — is it a bug? | [How the scorecard works](HOW_THE_SCORECARD_WORKS.md) |
| One metric’s owner or warehouse table | [Metric playbook](METRIC_PLAYBOOK.md) |

### Ownership expectations

| Cadence | Your time | What you actually do |
| --- | --- | --- |
| Daily | ~0 min | Nothing unless something looks wrong |
| Weekly | ~5 min | Verify Vinay’s shopping pacing sheet updated |
| Monthly | ~20 min | Verify Scale actuals + FTE month landed |
| Quarterly | ~half day | Confirm goals with owners → roll → publish |

---

## 2. Mental model (15 min)

**Show the published app.** Point at the Data clock / freshness line.

### Talk track — Data clock

> Every row shares one `latest_date` — the Data clock. It’s not today; it’s the freshest date the warehouse allows. Sources within 3 days stay on the clock. Anything more than 3 days behind goes off the clock — that metric shows `—` and an orange banner. That’s intentional: one broken table shouldn’t freeze the whole scorecard.

### Data flow (whiteboard or screen)

```
Google Sheets ──┐
                ├──► Hex notebook (9 AM run) ──► Publish ──► Stakeholders
Warehouse SQL ──┘
         ↑
   A few notebook constants (Impressions, HQ Signal, fallbacks)
```

### Two rules — say verbatim

1. **At quarter roll, confirm goals with owners before you touch Hex.** A populated sheet is not confirmation. Hex cannot tell if targets are final, carried over, or provisional.

2. **Sheets refresh themselves. Fix the sheet, not Hex.** When you run cells, run only the cell you changed → that tab’s Table cell. Never rerun the whole notebook for a small fix.

### Auto vs manual

| Auto on 9:00 run | Still manual in Hex |
| --- | --- |
| MAA, DAUq, A/B goals | `IMPRESSIONS_GOALS` |
| Shopping CQ/FY + weekly paced QTD | HQ Signal (no source) |
| Measured Revenue, Upper Funnel | `_EXP_COUNTS` if SQL down |
| Rev/FTE, Scale actuals | `_SOTA_START` / `_SOTA_FY` only if year path changes |

### Targeted cell runs (when you must run something)

| Tab | Metrics cell | Table cell |
| --- | --- | --- |
| Company Level Goals | `Company Level Goals df` | `Company Level Goals Table` |
| CATS SC / KPIs | `CATS SC KPIs Metrics` | `CATS SC KPIs Table` |
| Ads Product & GTM | `Ads Product and GTM Metrics` | `Ads Product and GTM Table` |
| Ads Supply Drivers | `Ads Supply Drivers Metrics` | `Ads Supply Drivers Table` |

---

## 3. Dashboard tour (20 min)

Walk the **published app** tab by tab. For each: purpose → 2–3 anchor metrics → one “looks wrong but isn’t” example.

### Tab 1: Company Level Goals (~7 min)

**Purpose:** Executive view — revenue, MAA, DAUq, impressions, Tier 2 A/B suite.

**Show**

- Ads Realized Revenue, MAA family, DAUq (US/ROW) — warehouse + sheet goals
- Ad Impressions — **only hard-coded goal** on this tab (`IMPRESSIONS_GOALS`)
- A/B rows — grey early in quarter is **by design**

**Deliberate weirdness**

- DAUq on Company Level has goals and pacing colors
- DAUq on Supply tab is **display-only, always grey** — goals live on Company Level

---

### Tab 2: CATS SC / KPIs (~8 min)

**Purpose:** Pillar goals — Shopping, Measured, Upper Funnel, Rev/FTE, Scale, KPI copies of A/B.

**Show**

- Shopping Revenue — CQ/FY from Roadmap; **paced QTD** from Vinay’s weekly sheet (col B → AO)
- Scale Our Foundations (5 rows) — linear pacing, monthly actuals, ~1 month lag on OE
- Rev/FTE — `(LTM as of <month>)` — pins to last month with headcount
- HQ Signal — always grey, no published source

**Status colors (30 sec)**

> Each row has a named rule in the Metrics cell. Green/yellow/red thresholds live in **Status Strategies**. You’ll rarely change these — but owners may ask why something is grey vs red.

Layer order (last wins): rule → A/B patches → stale override → governance warnings.

---

### Tab 3: Ads Product & GTM (~3 min)

**Purpose:** Mostly warehouse actuals. Goals for Shopping/Measured live on KPIs tab.

**Show**

- GTM Shopping copy is grey by design (pacing color is KPI tab only)
- Budget Utilization is **intentionally blank** (source died 2 June 2026) — Dana owns replace-or-retire

---

### Tab 4: Ads Supply Drivers (~2 min)

**Purpose:** Supply-side view — DAUq, WAUq, monetizable inventory.

**Show**

- DAUq targets from sheet rolled in quarter Step 1
- WAUq and feed metrics have **no targets** by design

---

## 4. Runbook by cadence (20 min)

Open [Operations runbook](OPERATIONS_RUNBOOK.md). Walk the cadence table at the top, then one example per cadence.

### Daily — do nothing

> 9:00 AM Chicago reruns the whole notebook. Warehouse + all connected sheets refresh. Investigate only if a row looks wrong after the run.

---

### Weekly — Shopping pacing

**Owner:** Vinay Sridhar  
**Sheet:** [Shopping pacing sheet](https://docs.google.com/spreadsheets/d/1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8/edit?gid=1861501712#gid=1861501712)

> Vinay’s team updates col **B** (week) and **AO** (paced QTD target) on the current quarter’s DPA tracker tab. You don’t edit Hex. After Monday’s 9:00 run, spot-check Shopping pacing color on the KPI tab.

**Verify:** current quarter tab exists · col B has week date · col AO has target

---

### Monthly — Scale + FTE (~20 min, first week after month close)

**Scale — talk track**

> Nikhil confirms Scale source sheets got a new month. You verify Value and “as of {month}” moved. If they match last month exactly, the pull may have failed to a checksum — check with Nikhil, don’t type a cover number.

Detail: [Scale Our Foundations](OPERATIONS_RUNBOOK.md#scale-our-foundations-cats-sc--kpis) in the runbook.

**Rev/FTE — talk track**

> Confirm Nick’s sheet has the new month. That’s the whole task. If headcount hasn’t landed, leave it — pairing newer revenue with old headcount gives a wrong number.

**Sheet:** [Rev / S+M FTE gsheet](https://docs.google.com/spreadsheets/d/1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk/edit?gid=971510625)

---

### Quarterly — the big roll

Walk the [Quick checklists](OPERATIONS_RUNBOOK.md#quick-checklists) — do not execute live.

#### Step 0 — Owner confirmations (day 1 emails)

> Send these on day 1. Do not start Hex until owners reply. A populated sheet is not a reply.

Use the owner table in [Step 0](OPERATIONS_RUNBOOK.md#step-0--confirm-the-new-quarters-goals-with-each-owner).

#### Step 1 — Company Level

1. MAA — confirm MAB Daily Goals Allocation → run `Maa goals gsheet` → `Maa goals df`
2. DAUq — confirm Latest Forecast tab → run `DAUq targets gsheet` → `DAUq official targets df`
3. A/B — confirm Roadmap KPIs new quarter column → run goals chain
4. Ad Impressions — read numbers from Daily Forecast – Live → add key to `IMPRESSIONS_GOALS` in `Company Level Goals df`
5. Run `Company Level Goals df` → `Company Level Goals Table`

#### Step 2 — CATS SC / KPIs

**Goals chain (memorize):**

```
C performance goals ab gsheet
  → C performance goals ab df
  → C performance goals ad df with cpv
  → Rev FTE gsheet → Rev FTE df → Rev FTE actuals
  → CATS SC KPIs Metrics
  → CATS SC KPIs Table
```

#### Steps 3–4 — GTM + Supply

Re-run each tab’s Metrics → Table (verification only).

#### Step 5 — Publish

> Draft is the only place your changes exist until you publish. Then log notebook constant edits in the Governance sheet **Change Log** tab.

**Draft checks before publish**

- [ ] Goal columns show the new quarter
- [ ] No goal column unexpectedly blank
- [ ] A/B rows grey early in quarter (expected, not a bug)

---

## 5. Troubleshooting (15 min)

Open runbook section [When something looks stale](OPERATIONS_RUNBOOK.md#when-something-looks-stale).

### Top 5 scenarios

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Metric shows `—` + orange banner | Source >3 days behind | Note banner; escalate to warehouse owner if persistent |
| `WARN systemic freshness incident` | Warehouse-wide lag | Do not trust pacing colours; flag before anyone reads numbers |
| Goal column = last quarter | Sheet never rolled | Confirm with owner; next 9:00 run picks it up |
| A/B goal suddenly blank | Label renamed in goals sheet | Compare to Canonical Metric Map; add alias |
| Scale row identical to last month | Sheet not updated or checksum fallback | Check source with Nikhil |
| Shopping pacing color wrong | Pacing sheet tab / col B / AO stale | Verify sheet; re-run goals chain if needed |

### Zero vs dash

| Display | Meaning |
| --- | --- |
| `0`, `$0`, `0%` | Metric really was zero |
| `—` | We do not have the data |

> A failed pull showing `0` is a bug. Never convert a failed pull into a zero.

### Post-Install CPA vs plain CPA

**Two different metrics — never merge.**

| Metric | Goals sheet label | Canonical key |
| --- | --- | --- |
| Post-Install CPA A/B | `Price: Post-Install CPA` | `Post-Install CPA A/B` |
| Plain CPA | `Price: CPA`, `CPA`, `CPA A/B` | `CPA A/B` |

If goal blanks after rename: note exact label → run **C performance goals ab gsheet** → **C performance goals ad df with cpv** → fix alias in **Canonical Metric Map** → re-run KPI Metrics → Table.

Full detail: [Post-Install CPA A/B vs plain CPA](OPERATIONS_RUNBOOK.md#post-install-cpa-ab-vs-plain-cpa).

### First debug step for any stale row

Open draft → read output of **`Quarter dates based on latest date`** — clock date, freshest date, status of every source.

---

## 6. Handoff & next steps (10 min)

### Doc map

```
README (links)
  └── Operations runbook  ← start here for any task
        └── How the scorecard works  ← “is this intentional?”
              └── Metric playbook  ← one metric lookup
```

### Shadow assignment

Pick based on what’s next on the calendar:

| Next event | Shadow task |
| --- | --- |
| This week | Verify shopping pacing sheet + spot-check KPI tab color after Monday 9:00 run |
| Month close | Walk Scale actuals table with Nikhil; confirm FTE month on Rev/FTE sheet |
| Quarter start | Draft owner confirmation emails from runbook Step 0 table |

### Escalation paths

| Topic | Who |
| --- | --- |
| Scale actuals / sheet pulls | Nikhil Khanted |
| Shopping pacing sheet | Vinay Sridhar |
| FTE headcount sheet | Nick Asaad |
| Scale goals / pacing methodology | Virgilio Pigliucci |
| Metric owners | [Governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc) |
| Hex access / publish | Current facilitator until handoff complete |
| Budget Utilization retire/replace | Dana |

### Closing line

> Your default posture is: wait for the 9:00 run, verify upstream sources, run targeted cells only when you need to see a change today. The runbook is the source of truth — if anything in this meeting conflicts with it, trust the runbook.

### Attendee follow-up (send after meeting)

**Subject:** CATS Scorecard handoff — links + shadow task

**Body template:**

```
Thanks for joining the walkthrough. Here’s what to keep handy:

• Published app: https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest
• Operations runbook: [link to repo handover/OPERATIONS_RUNBOOK.md]
• Governance sheet: https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc

Your shadow task: [fill in from table above]

Pre-read for next time (optional): How the scorecard works — “Choices we made on purpose” section.

Recording: [link if applicable]
```

---

## Split into two sessions

| Session 1 (45 min) | Session 2 (45 min) |
| --- | --- |
| Framing + Mental model | Runbook: monthly + quarterly |
| Dashboard tour (all 4 tabs) | Troubleshooting + Hex draft peek |
| Weekly pacing example | Shadow assignment + Q&A |

---

## One-slide summary

**CATS Scorecard in one sentence:** A Hex dashboard that auto-refreshes daily from warehouse + Google Sheets; you confirm upstream sources landed and edit ~5 notebook constants at quarter roll.

**Your job:** Verify, don’t re-type. Confirm with owners before rolling. Fix sheets before Hex. Run changed cell → Table cell only.
