# CATS Scorecard

**As of:** 17 September 2026

The scorecard is a Hex app. It rebuilds at **9:00 AM Chicago time**.

**Hex**

- Draft: https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae
- Published: https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest

**Google**

- Governance sheet: https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc
- Automation plan: https://docs.google.com/document/d/1kBjrbheugF0CO_VRm-h6XLwKrzjNqjT4wfpLCkTUke8/edit?tab=t.0

## What's in this folder

| File | What it is |
|---|---|
| [README.md](README.md) | This page — links and where to start |
| [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Step-by-step: quarter roll, monthly and weekly upkeep, what to run, who to ask |
| [HOW_THE_SCORECARD_WORKS.md](HOW_THE_SCORECARD_WORKS.md) | Why the numbers behave as they do — clock, colors, deliberate exceptions |
| [METRIC_PLAYBOOK.md](METRIC_PLAYBOOK.md) | One card per live row — owner, source, how the number is built |
| [agent/agent_build_plan.md](agent/agent_build_plan.md) | Build plan for a staging-only ingestion agent (Scale, S+M FTE, Shopping Revenue pacing) |
| [agent/](agent/README.md) | The agent itself — runnable Tier-1 ingestion code, plus [SKILL.md](agent/SKILL.md), the skills pack that defines it |
| [agent/skills/](agent/skills/README.md) | The eight skill packs built from the build plan and runbook, step by step |

Read in this order. Stop when you have what you need.

| # | Document | What it is |
|---|---|---|
| 1 | This page | Links and routing |
| 2 | [Operations runbook](OPERATIONS_RUNBOOK.md) | Step-by-step: quarter roll, monthly upkeep, what to run, who to ask |
| 3 | [How the scorecard works](HOW_THE_SCORECARD_WORKS.md) | Why the numbers behave as they do — clock, colors, deliberate exceptions |
| 4 | [Metric playbook](METRIC_PLAYBOOK.md) | One card per live row — owner, source, how the number is built |
| 5 | [Agent build plan](agent/agent_build_plan.md) | Spec for automating Scale, FTE, and Shopping pacing into a staging sheet |
| 6 | [The agent](agent/README.md) | The code that implements Tier 1 of that plan, how to run it, and what is still open |
| 7 | [Agent skill packs](agent/skills/README.md) | The eight packs built from that spec — goal workflow (step 0 → 5 + orchestrator) and scorecard-ingest |

## Where to go

- You need to update the scorecard for a new quarter or a new month → **runbook**
- A number looks wrong and you want to know whether it is intentional → **how it works**
- You need one metric's owner or warehouse table → **playbook** (search the list)
- You are building or running the staging ingestion agent → **agents build plan**
- You want to actually run it, or see which rows still need an owner's sign-off → **[the agent](agent/README.md)**
