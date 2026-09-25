# Agent skill packs

The eight packs built against the [agent build plan](../agent_build_plan.md) and the
[operations runbook](../../OPERATIONS_RUNBOOK.md). Each folder is a self-contained pack:
a `SKILL.md` with the instructions, plus any scripts, fixtures, and reference files it needs.

> **These are documentation here, not live skills.** Cursor only loads skills from
> `.cursor/skills/<name>/SKILL.md`. They were moved out of that folder on purpose, so
> nothing in this directory is picked up automatically any more. To make a pack runnable
> again, copy or symlink its folder back:
> `ln -s ../../docs/handover/agent/skills/<pack> .cursor/skills/<pack>`

## Goal Creation & Pacing Workflow

Seven packs. Step 0 always runs first; the orchestrator can drive the whole chain.

| # | Pack | What it does |
|---|---|---|
| — | [goal-workflow-orchestrator](goal-workflow-orchestrator/) | Drives Registrar → Topographer → Architect → Pacer → Signaler → Publisher. Routes by goal shape, persists run state to disk, coordinates batch quarterly goal locks across many metrics and owners |
| 0 | [goal-step0-registrar](goal-step0-registrar/) | Resolve the metric to a stable `metric_id`, read what the Goal Registry already knows, detect existing or conflicting goals, classify the goal shape, route to the right path. **Always run before steps 1–5** |
| 1 | [goal-step1-topographer](goal-step1-topographer/) | Analyze metric behaviour, data health, and seasonality. Outputs an Insight Card, cleaned data, and a segmentation recommendation |
| 2 | [goal-step2-architect](goal-step2-architect/) | Set the quarterly target value from trends, strategic context, and scenario modelling. Outputs the goal value plus rationale |
| 3 | [goal-step3-pacer](goal-step3-pacer/) | Convert a period goal into the QTD expectation curve the dashboard grades against — metric-type pacing, seasonal shape, mid-quarter re-forecast, cumulative-ratio effort curves. Outputs a daily pacing CSV + MD |
| 4 | [goal-step4-signaler](goal-step4-signaler/) | Confirm the Red/Yellow/Green policy by reading `status_rule` from the Metric Registry and validating it fits the metric's type and direction. Outputs the confirmed rule + threshold explanation |
| 5 | [goal-step5-publisher](goal-step5-publisher/) | Write the goal to the canonical Goal Registry keyed on `metric_id`, append a change-log entry, produce the stakeholder deliverable. **The only step that creates a system of record** |

## Ingestion

| Pack | What it does |
|---|---|
| [scorecard-ingest](scorecard-ingest/) | Extract CATS scorecard Google Sheet sources into a DS staging workbook with a stable schema, then validate publish-ready rows. Covers the Phase 1 sheet-to-dashboard path, including MAA and DAUq goals. Ships `scripts/` (extractors, schema, validators) and `scripts/fixtures/` for offline tests |

Scope and guardrails for the ingestion agent — tiers, cadence, validation gates, status
rules, contact directory — live in the [agent build plan](../agent_build_plan.md).
