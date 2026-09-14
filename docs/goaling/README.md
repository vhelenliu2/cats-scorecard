# Goaling Skill — Audit, Test, and Improvement

Work on top of the existing 5-step goaling skill, aimed at making goal-setting standardized so
stakeholders do less while goals become traceable.

## Deliverables

| # | Document | Contents |
|---|---|---|
| 1 | [Skill Inventory](01_SKILL_INVENTORY.md) | The 6 baseline skills, reusable assets worth keeping, and 12 numbered gaps |
| 2 | [Test Set](02_TEST_SET.md) | 17 cases from real repo metrics — 3 golden path, 14 edge cases |
| 3 | [Evaluation](03_EVALUATION.md) | Live end-to-end run + desk trace. Per-skill scorecard and 10 decisions for Yoni |
| 4 | [Improvements](04_IMPROVEMENTS.md) | What changed in each skill and why, each traced to a finding |
| 5 | [Recommendation](05_RECOMMENDATION.md) | Productionize / automate / leave manual, with a sequenced plan |

Supporting:

| Asset | Purpose |
|---|---|
| [REFERENCE_status_policies.md](REFERENCE_status_policies.md) | The **10 active** `status_goal` values on the live scorecard, with thresholds and row assignments |
| [`eval/live_run_results_impressions_q3_2026.md`](../../eval/live_run_results_impressions_q3_2026.md) | Live BigQuery numbers behind the evaluation |
| [`governance/validate_goal_row.py`](../../governance/validate_goal_row.py) | Executable schema contract for Goal Registry rows |
| [`eval/goal_rows_testcases.csv`](../../eval/goal_rows_testcases.csv) | 10 fixture rows; 6 fail by design |

## The skills

Baseline installed unmodified first, then revised — so `git diff` shows every change.

| Step | Skill | Role |
|---|---|---|
| — | [orchestrator](../../.cursor/skills/goal-workflow-orchestrator/SKILL.md) | Routing, state on disk, batch quarterly lock |
| **0** | [registrar](../../.cursor/skills/goal-step0-registrar/SKILL.md) | **New.** `metric_id`, existing-goal detection, routing, approval capture |
| 1 | [topographer](../../.cursor/skills/goal-step1-topographer/SKILL.md) | Behaviour, data health, within-quarter shape |
| 2 | [architect](../../.cursor/skills/goal-step2-architect/SKILL.md) | Set *or validate* the goal value |
| 3 | [pacer](../../.cursor/skills/goal-step3-pacer/SKILL.md) | The QTD expectation curve |
| 4 | [signaler](../../.cursor/skills/goal-step4-signaler/SKILL.md) | Confirm the `status_rule` |
| 5 | [publisher](../../.cursor/skills/goal-step5-publisher/SKILL.md) | Write to the Goal Registry + change log |

## Three findings that drove everything

1. **The workflow had no way to detect an existing goal.** Ad Impressions Q3 2026 has *two*
   conflicting goals in live code — 117.70B and 112.33B, 4.8% apart. Followed literally, the baseline
   would have produced a third. Hence Step 0.

2. **It had nowhere to store the result.** Step 5 wrote to BigQuery tables that don't exist, while
   the canonical Goal Registry sat empty in `governance/`. Hence the registry-native rewrite.

3. **Every Step 4 policy ID was fictional.** None of the retired ids exist in the live Hex **Status Strategies** cell; selecting one crashes the dashboard with `ValueError`. Hence [REFERENCE_status_policies.md](REFERENCE_status_policies.md) and the validator.

## Start here

Read [Evaluation](03_EVALUATION.md) Part 4 — the 10 decisions that need Yoni — then
[Recommendation](05_RECOMMENDATION.md).
